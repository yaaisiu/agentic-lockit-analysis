#!/usr/bin/env python3
# scripts/wesnoth/po_tokens.py
# source: profile wesnoth (GATE 1) — the SINGLE source of truth for in-string token detection.
"""
WHY: every script that inventories or validates tokens (placeholders, markup, escapes,
entities) must agree on *what a token looks like*. Defining the regexes once here means a
fix to a pattern propagates everywhere, and the profile's [[variables]] note and the code
never drift apart. Patterns mirror vault/lockits/wesnoth/variables.md §1–§7.
"""
import re

PATTERNS = {
    # $var, $obj.attr, $arr[0], optional trailing | terminator (Wesnoth; preserve verbatim).
    # A dotted segment is only part of the name when the '.' is followed by an identifier
    # ($unit.name), so a var at a sentence end ($version.) does NOT swallow the period —
    # that over-capture caused false cross-locale placeholder mismatches. See variables.md §1.
    "wml_var":   re.compile(r'\$[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*(?:\[\d+\])?\|?'),
    # Pango / legacy markup tags (open, close, self-closing)
    "markup_tag": re.compile(r'</?[A-Za-z][\w]*(?:\s[^>]*?)?/?>'),
    # translatable payload inside legacy attribute-form markup
    "text_attr": re.compile(r"text='[^']*'"),
    # XML/Pango character entities (must stay escaped). Numeric refs come in three forms:
    # decimal &#8217;  · XML hex &#x7B;  · Wesnoth hex &#0x7B; (literal { , escaped because
    # {} are WML macro delimiters). 0x-form must precede \d+ in the alternation.
    "entity":    re.compile(r'&(?:quot|lt|gt|amp|apos|#(?:0x[0-9A-Fa-f]+|x[0-9A-Fa-f]+|\d+));'),
    # backslash escapes actually seen: \n \t \r \" \\
    "escape":    re.compile(r'\\[ntr"\\]'),
    # printf / strftime style formats (rare; #, c-format flags these)
    "printf":    re.compile(r'%[-#0-9.]*\d*\$?[sdiouxXeEfFgGcp%]'),
    # {name} braces — name-generator grammar rules (wesnoth core [naming]) and
    # python-brace-format. A placeholder class: preserve verbatim, never translate the key.
    "brace_var": re.compile(r'\{[A-Za-z_][A-Za-z0-9_]*\}'),
}

# ---------------------------------------------------------------------------
# Markup families. The corpus carries THREE markup systems, cleanly separated by
# domain (see vault/lockits/wesnoth/variables.md §markup):
#   * pango   — game-content UI text (29 domains): <b>…</b>, <span …>, <ref>…
#   * docbook — the wesnoth-manual domain: <emphasis>…</emphasis>, <link>…, <imagedata/>
#   * po4a    — the wesnoth-manpages domain: POD-style man markup B<bold> I<italic>,
#               with E<lt>/E<gt>/E<amp> standing in for literal < > & (see pod_* below).
# pango+docbook share the SAME open/close balance model, so KNOWN_TAGS is their union and
# balance-checking is identical. po4a is a different syntax, handled by its own helpers.
# Anything in <…> that is NOT a known tag and NOT po4a is command/CLI metasyntax
# (bare <side>, <nickname>, <file>) — a single-token argument slot, never balanced.
# ---------------------------------------------------------------------------
MARKUP_FAMILIES = {
    "pango": {
        "b", "i", "u", "s", "tt", "big", "small", "sub", "sup", "span",
        "bold", "italic", "underline", "header", "h", "format",
        "ref", "img", "jump", "character",
    },
    # DocBook tags. The first line is evidenced in the English wesnoth-manual; the rest are
    # pre-seeded from the DocBook inline/phrase/GUI vocabulary (Marcin, session 001 B4) so a
    # *translated* manual using tags English didn't happen to use still balance-checks rather
    # than reporting them as unknown.
    # DELIBERATELY EXCLUDED: DocBook element names that collide with Wesnoth's bare CLI
    # metasyntax slots — `command`, `option`, `filename`, `replaceable`, `parameter`, `varname`,
    # `prompt`, `constant`, `function`, `systemitem`, `userinput`, `computeroutput`, `envar`.
    # Those appear as single bare <slot> tokens in the wesnoth/manpages CLI help (no close
    # tag), so treating them as balance-checked markup produced false "unclosed" errors.
    # DocBook-distinctive names below don't collide.
    "docbook": {
        # evidenced in the English source:
        "emphasis", "imageobject", "imagedata", "link", "ulink", "literal", "placeholder",
        # pre-seeded DocBook-distinctive inline / phrase / GUI / structural elements:
        "phrase", "quote", "citetitle", "superscript", "subscript",
        "keycap", "keycombo", "guimenu", "guimenuitem", "guibutton", "guilabel", "guiicon",
        "menuchoice", "varlistentry", "listitem", "simpara", "inlinemediaobject",
        "mediaobject", "screenshot",
    },
}
# DocBook elements that are empty (self-closing) — never expect a matching close tag.
DOCBOOK_EMPTY = {"imagedata", "xref", "anchor", "inlinegraphic", "colspec"}
KNOWN_TAGS = set().union(*MARKUP_FAMILIES.values())

# po4a / POD man markup: an uppercase letter immediately followed by '<' opens a span that
# closes at the matching '>'. E<...> is the entity form (E<lt>=<, E<gt>=>, E<amp>=&, E<NN>).
POD_OPEN   = re.compile(r'[A-Z]<')
POD_ENTITY = re.compile(r'E<(?:lt|gt|amp|sol|verbar|[0-9]+)>')
# A real close tag <name> (letters/digits then '>'); distinguishes Pango/DocBook from a po4a
# path like B</var/run/socket> (where </var/run…> is content, not a close tag).
CLOSE_TAG  = re.compile(r'</[A-Za-z][\w]*\s*>')


def tag_family(name: str):
    """Which balanced-tag family a lowercase tag name belongs to (pango|docbook|None)."""
    for fam, tags in MARKUP_FAMILIES.items():
        if name in tags:
            return fam
    return None


def markup_family(text: str) -> str:
    """Classify a string's markup system: 'po4a' | 'tag'.
    'tag' covers pango+docbook (same balance model). po4a is detected by a POD opener
    ([A-Z]<) with no real close tag (</name>) — the discriminator that keeps a po4a path
    like B</var/run/socket> classified po4a while HP<b>x</b> stays a tag string."""
    if POD_OPEN.search(text) and not CLOSE_TAG.search(text):
        return "po4a"
    return "tag"


def find(text: str) -> dict:
    """Return {pattern_name: [raw matches]} for one string (RAW form, escapes intact)."""
    return {name: pat.findall(text) for name, pat in PATTERNS.items()}


def angle_tokens(text: str):
    """Yield (raw, tagname, kind) for every <...>. kind in {open, close, selfclose}.
    Lets callers separate KNOWN_TAGS (markup) from unknown angle tokens (metasyntax/literal)."""
    for m in re.finditer(r'<\s*(/?)\s*([A-Za-z][\w]*)[^>]*?(/?)\s*>', text):
        close, name, selfc = m.group(1), m.group(2), m.group(3)
        kind = "close" if close else ("selfclose" if selfc else "open")
        yield m.group(0), name.lower(), kind
