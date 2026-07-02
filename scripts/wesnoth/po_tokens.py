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
    # $var, $obj.attr, $arr[0], optional trailing | terminator (Wesnoth; preserve verbatim)
    "wml_var":   re.compile(r'\$[A-Za-z_][\w.]*(?:\[\d+\])?\|?'),
    # Pango / legacy markup tags (open, close, self-closing)
    "markup_tag": re.compile(r'</?[A-Za-z][\w]*(?:\s[^>]*?)?/?>'),
    # translatable payload inside legacy attribute-form markup
    "text_attr": re.compile(r"text='[^']*'"),
    # XML/Pango character entities (must stay escaped)
    "entity":    re.compile(r'&(?:quot|lt|gt|amp|apos|#\d+);'),
    # backslash escapes actually seen: \n \t \r \" \\
    "escape":    re.compile(r'\\[ntr"\\]'),
    # printf / strftime style formats (rare; #, c-format flags these)
    "printf":    re.compile(r'%[-#0-9.]*\d*\$?[sdiouxXeEfFgGcp%]'),
}

# Tags we recognise as real Wesnoth/Pango markup. Anything else in <...> is treated as a
# non-markup angle token (command-help metasyntax like <side>, or literal like <unknown>).
KNOWN_TAGS = {
    "b", "i", "u", "s", "tt", "big", "small", "sub", "sup", "span",
    "bold", "italic", "underline", "header", "h", "format",
    "ref", "img", "jump", "character",
}


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
