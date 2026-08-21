#!/usr/bin/env python3
# vault/library/script-templates/schema_check.py
# TEMPLATE — validate an emitted artifact against the PUBLISHED JSON Schema file, no dependency.
# first_seen: wesnoth (session 009).
"""
PURPOSE: let a producer's test suite assert "what we emit conforms to the schema we publish" by
reading `contracts/<name>.schema.json` ITSELF, on a machine with nothing installed. Embodies
[[pinned-version-discriminator]] and [[byte-stable-artifact]] rule 11; see also
[[producer-contract-ownership]] and [[negative-test-mutation-proof]].

WHY THIS EXISTS (rationale a less-capable agent can follow and reproduce):

1. **Validate against the published FILE, never a copy of its rules.** A producer typically
   grows a hand-written verifier (`verify_manifest()`) that mirrors its schema. That mirror is
   useful — it refuses to WRITE a bad artifact — but it is a second copy of the contract, and
   two copies drift. The drift is invisible: both agree, the tests pass, and the consumer
   holding the real schema is the one who finds out. So at least one test must read the schema
   file off disk. Keep the hand-written verifier too; they check different things.

2. **No dependency, because the alternative is no test at all.** `jsonschema` is the right tool
   when it is available. In this project it is not installed, installing it needs network, and
   the toolkits are stdlib-only by rule — so a full validator would mean the schema file is
   never actually read by anything. Forty lines covering the keywords a contract object really
   uses beats a perfect validator that cannot run. If `jsonschema` IS available where you are,
   use it and delete this.

3. **What it deliberately does not implement:** `$ref` / `$defs` resolution beyond a top-level
   lookup, `allOf`/`anyOf`/`oneOf`, `format`, numeric bounds, `uniqueItems`, `patternProperties`.
   If your contract needs those, that is the signal to take the dependency rather than to grow
   this file — an under-implemented validator that silently PASSES what it cannot express is the
   same failure mode as an unpinned version field.

4. **`const` is why this matters.** The keyword that makes a contract-version field load-bearing
   is `const`, and a checker that ignores it reports success on a bundle written against a
   different contract. That is exactly the defect [[pinned-version-discriminator]] exists to
   close, reproduced inside the tool meant to catch it. `const` is therefore the first keyword
   implemented here, not an afterthought.

HOW TO PARAMETERISE:
  1. Point SCHEMA_PATH at your published schema.
  2. `defn("manifest")` returns `$defs.manifest`; pass the object you emitted.
  3. Assert `problems == []` for the positive test, and — next to it — assert the NEGATIVE test:
     a wrong `const` value produces a problem naming that field.
  4. Then mutate the guard to prove the negative test is real ([[negative-test-mutation-proof]]):
     loosen `const` to {"type": "string"} IN MEMORY and confirm the bad object now validates.
"""
import json, os, re

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "..", "..", "..", "contracts", "bundle.schema.json")

_TYPES = {"object": dict, "array": list, "string": str, "integer": int,
          "number": (int, float), "boolean": bool}


def defn(name, path=SCHEMA_PATH):
    """The named definition out of $defs — the unit a producer actually emits."""
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)["$defs"][name]


def schema_problems(obj, schema, path="$"):
    """Return a list of human-readable problems; [] means valid. Never raises on bad input —
    a validator that throws on the first defect hides the rest, and the whole point of a
    problem LIST is to report every failure in one run (see [[byte-stable-artifact]] rule 10)."""
    p = []
    t = schema.get("type")
    wants = [t] if isinstance(t, str) else (t or [])
    if wants:
        for want in wants:
            if want == "null":
                if obj is None:
                    return []                      # null branch: nothing further applies
            elif isinstance(obj, _TYPES.get(want, object)) \
                    and not (want in ("integer", "number") and isinstance(obj, bool)):
                break                              # bool is an int in Python; a schema means no
        else:
            return [f"{path}: type {type(obj).__name__} not in {wants}"]

    # const FIRST — the keyword that makes a version discriminator load-bearing.
    if "const" in schema and obj != schema["const"]:
        p.append(f"{path}: const {schema['const']!r} != {obj!r}")
    if "enum" in schema and obj not in schema["enum"]:
        p.append(f"{path}: {obj!r} not in enum")
    if "pattern" in schema and isinstance(obj, str) and not re.match(schema["pattern"], obj):
        p.append(f"{path}: {obj!r} does not match {schema['pattern']}")
    if isinstance(obj, int) and not isinstance(obj, bool) and "minimum" in schema \
            and obj < schema["minimum"]:
        p.append(f"{path}: {obj} < minimum {schema['minimum']}")

    if isinstance(obj, dict):
        for k in schema.get("required", []):
            if k not in obj:
                p.append(f"{path}: missing required {k!r}")
        props = schema.get("properties", {})
        extra = schema.get("additionalProperties")
        for k, v in obj.items():
            sub = props.get(k)
            if sub is None:
                if extra is False:
                    p.append(f"{path}: {k!r} is outside the schema (additionalProperties: false)")
                sub = extra if isinstance(extra, dict) else None   # e.g. a typed string map
            if sub:
                p += schema_problems(v, sub, f"{path}.{k}")
    if isinstance(obj, list) and isinstance(schema.get("items"), dict):
        for i, v in enumerate(obj):
            p += schema_problems(v, schema["items"], f"{path}[{i}]")
    return p


# --- the pair to copy into the producer's test suite, KEPT ADJACENT -------------------
# Someone reading the suite in six months must see both at once and understand what `const`
# buys. Split them across the file and the negative one reads as an odd edge case.
#
# def test_manifest_validates_against_published_schema(tmp_path):
#     assert schema_problems(emit_manifest(...), defn("manifest")) == []
#
# def test_wrong_version_fails_validation(tmp_path):
#     """Loosening const -> {"type": "string"} makes this pass — verified, see
#     [[negative-test-mutation-proof]]. That is the whole reason the pin is there."""
#     bad = dict(emit_manifest(...), bundle_version="2.0.0")
#     assert any("bundle_version" in x and "const" in x
#                for x in schema_problems(bad, defn("manifest")))
