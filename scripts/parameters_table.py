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
"""

import argparse
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

HEADER = ["Parameter", "Description", "Value", "Range", "Source"]


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("input", nargs="?", default=DEFAULT_INPUT, help="parameters YAML file")
    parser.add_argument("-o", "--output", help="output Markdown file (default: stdout)")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        doc = yaml.safe_load(f)

    tables = make_tables(doc)

    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="\n") as f:
            f.write(WARNING + tables)
    else:
        sys.stdout.reconfigure(encoding="utf-8")  # For the en dashes, e.g. on Windows consoles.
        sys.stdout.write(tables)


def make_tables(doc):
    """Returns the Markdown sections for a parsed parameters document."""
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
                lines += [entry["description"], ""]
            lines += [row(HEADER), "|" + "|".join("---" for _ in HEADER) + "|"]
            lines += [row(make_row(param)) for param in params]
            sections.append("\n".join(lines) + "\n")
    return "\n".join(sections)


def make_row(param):
    """Returns the cells of a parameter's table row, as Markdown."""
    unit = param.get("unit")
    return [
        f"`{param['name']}`",
        f"{param.get('description', '')} *({param.get('category', '')})*",
        with_unit(format_value(param.get("value")), unit),
        format_range(param.get("range"), unit),
        param.get("source") or "",
    ]


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
