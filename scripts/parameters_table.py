"""Creates Markdown tables of the model parameters from parameters.yaml.

Usage:
    python scripts/parameters_table.py [parameters.yaml] [-o parameters.md]

Without -o, the output is printed to stdout. With -o, a warning that the file
is auto-generated is added at the top. Requires PyYAML.

Each resource and system gets its own section: a heading with its type name,
its description, and a table of its parameters. Resources and systems without
parameters are left out. A type that appears more than once (e.g.
TreeAttraction) is told apart in its heading by the entry's optional `label`,
or by its 1-based occurrence number if it has none.

Citations of the form [@key] in descriptions and sources are replaced by short
citations (e.g. "Naves et al., 2006") linking to the reference list, which is
appended as a final section. Citing an unknown key is an error; references
that are never cited give a warning.
"""

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

DEFAULT_INPUT = Path(__file__).resolve().parent.parent / "parameters.yaml"

# Prepended to the output when writing it to a file (-o).
WARNING = """> [!WARNING]
> This file is auto-generated from `parameters.yaml`. Do not edit it by hand!
> Instead, edit `parameters.yaml` and regenerate this file with:
>
> ```
> python scripts/parameters_table.py -o parameters.md
> ```

"""

CITATION = re.compile(r"\[@([\w-]+)\]")

HEADER = ["Parameter", "Description", "Value", "Range", "Source"]


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("input", nargs="?", default=DEFAULT_INPUT, help="parameters YAML file")
    parser.add_argument("-o", "--output", help="output Markdown file (default: stdout)")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        doc = yaml.safe_load(f)

    refs = {}
    for ref in doc.get("references") or []:
        if ref["key"] in refs:
            sys.exit(f"error: duplicate reference key '{ref['key']}'")
        refs[ref["key"]] = ref
    cited = set()

    tables = make_tables(doc, refs, cited)
    for key in refs.keys() - cited:
        print(f"warning: reference '{key}' is never cited", file=sys.stderr)
    if refs:
        tables += "\n" + make_references(refs)

    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="\n") as f:
            f.write(WARNING + tables)
    else:
        sys.stdout.reconfigure(encoding="utf-8")  # For the en dashes, e.g. on Windows consoles.
        sys.stdout.write(tables)


def make_tables(doc, refs, cited):
    """Returns the Markdown sections for a parsed parameters document.

    Keys of the references cited are added to cited.
    """
    sections = []
    for section in ("resources", "systems"):
        entries = doc.get(section) or []
        type_counts = Counter(e["type"] for e in entries)
        occurrence = Counter()
        for entry in entries:
            typ = entry["type"]
            occurrence[typ] += 1
            params = entry.get("parameters") or []
            if not params:
                continue

            title = typ
            if type_counts[typ] > 1:
                title += f" ({entry.get('label', occurrence[typ])})"
            lines = [f"## {title}", ""]
            if entry.get("description"):
                lines += [expand_citations(entry["description"], refs, cited), ""]
            lines += [row(HEADER), "|" + "|".join("---" for _ in HEADER) + "|"]
            lines += [row(make_row(param, refs, cited)) for param in params]
            sections.append("\n".join(lines) + "\n")
    return "\n".join(sections)


def make_row(param, refs, cited):
    """Returns the cells of a parameter's table row, as Markdown."""
    unit = param.get("unit")
    description = expand_citations(param.get("description", ""), refs, cited)
    return [
        f"`{param['name']}`",
        f"{description} *({param.get('category', '')})*",
        with_unit(format_value(param.get("value")), unit),
        format_range(param.get("range"), unit),
        expand_citations(param.get("source") or "", refs, cited),
    ]


def expand_citations(text, refs, cited):
    """Replaces [@key] citations in text by short citations linking to the reference list."""

    def replace(match):
        key = match.group(1)
        if key not in refs:
            sys.exit(f"error: citation of unknown reference '{key}'")
        cited.add(key)
        return f"[{short_citation(refs[key])}](#{key})"

    return CITATION.sub(replace, str(text))


def short_citation(ref):
    """Returns the short citation of a reference, e.g. "Naves et al., 2006"."""
    families = [family_name(a) for a in ref["authors"]]
    if len(families) == 1:
        names = families[0]
    elif len(families) == 2:
        names = f"{families[0]} & {families[1]}"
    else:
        names = f"{families[0]} et al."
    return f"{names}, {ref['year']}"


def family_name(author):
    return author.split(",")[0].strip()


def make_references(refs):
    """Returns the Markdown section listing all references, in APA style."""
    lines = ["## References", ""]
    for ref in sorted(refs.values(), key=lambda r: ([family_name(a) for a in r["authors"]], r["year"])):
        lines.append(f'- <a id="{ref["key"]}"></a>{format_reference(ref)}')
    return "\n".join(lines) + "\n"


def format_reference(ref):
    """Returns the full APA-style reference, as Markdown."""
    authors = ref["authors"]
    if len(authors) == 1:
        text = authors[0]
    else:
        text = ", ".join(authors[:-1]) + ", & " + authors[-1]
    title = ref["title"]
    if not title.endswith((".", "?", "!")):
        title += "."
    text += f" ({ref['year']}). {title}"
    if ref.get("journal"):
        text += f" *{ref['journal']}*"
        if ref.get("volume"):
            text += f", *{ref['volume']}*"
            if ref.get("issue"):
                text += f"({ref['issue']})"
        if ref.get("pages"):
            text += f", {ref['pages']}"
        text += "."
    if ref.get("doi"):
        text += f" https://doi.org/{ref['doi']}"
    return text


def row(cells):
    """Returns a Markdown table row of cells."""
    return "| " + " | ".join(cell(c) for c in cells) + " |"


def format_value(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "–"
    return str(value)


def format_range(rng, unit):
    if rng is None:
        return "–"
    if isinstance(rng, list) and len(rng) == 2:
        return with_unit(f"{format_value(rng[0])} – {format_value(rng[1])}", unit)
    return str(rng)  # e.g. TODO


def with_unit(text, unit):
    if not unit or unit == "-" or text == "–":
        return text
    return f"{text} {unit}"


def cell(text):
    """Escapes text for use in a Markdown table cell."""
    return str(text).replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    main()
