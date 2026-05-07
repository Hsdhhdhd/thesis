from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TEMP = ROOT / "_word_review_src"
PANDOC = ROOT / "_tools" / "pandoc" / "pandoc-3.9.0.2" / "pandoc.exe"
OUT = ROOT / "thesis_可批注正文_文字校对版.docx"


def label_map() -> dict[str, str]:
    aux = (ROOT / "thesis.aux").read_text(encoding="utf-8", errors="ignore")
    labels: dict[str, str] = {}
    for match in re.finditer(r"\\newlabel\{([^}]+)\}\{\{([^{}]+)\}", aux):
        labels[match.group(1)] = match.group(2)
    return labels


def math_to_text(expr: str) -> str:
    compact = re.sub(r"\s+", "", expr)
    special = {
        r"\approx": "approximately",
        r"k=7": "k = 7",
        r"k\in\{3,5,7\}": "k in {3, 5, 7}",
        r"a_m(t)=\left|\lVert\mathbf{a}(t)\rVert-g\right|": "a_m(t) = | ||a(t)|| - g |",
        r"\omega_m(t)=\lVert\boldsymbol{\omega}(t)\rVert": "omega_m(t) = ||omega(t)||",
    }
    if compact in special:
        return special[compact]

    replacements = [
        (r"\left", ""),
        (r"\right", ""),
        (r"\,", " "),
        (r"\le", "<="),
        (r"\approx", " approximately "),
        (r"\cdot", "*"),
        (r"\pi", "pi"),
        (r"\in", " in "),
        (r"\lVert", "||"),
        (r"\rVert", "||"),
        (r"\mathbf", ""),
        (r"\boldsymbol", ""),
        (r"\omega", "omega"),
        (r"\gamma", "gamma"),
    ]
    text = expr
    for old, new in replacements:
        text = text.replace(old, new)
    text = re.sub(r"\\(?:mathrm|texttt)\{([^{}]*)\}", r"\1", text)
    text = re.sub(r"_\{([^{}]+)\}", r"_\1", text)
    text = re.sub(r"\^\{([^{}]+)\}", r"^\1", text)
    text = text.replace(r"\{", "{").replace(r"\}", "}")
    text = text.replace("{", "").replace("}", "")
    text = text.replace("I^2C", "I2C")
    text = re.sub(r"\s*=\s*", " = ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def replace_refs(text: str, labels: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        label = match.group(1)
        return labels.get(label, f"[{label}]")

    return re.sub(r"\\ref\{([^}]+)\}", repl, text)


def preprocess_latex(text: str, labels: dict[str, str]) -> str:
    text = replace_refs(text, labels)
    text = text.replace("~", " ")
    text = text.replace(r"\si{\meter\per\second\squared}", "m/s^2")
    text = text.replace(r"\si{\degree\per\second}", "deg/s")
    text = re.sub(r"\\\((.*?)\\\)", lambda m: f" {math_to_text(m.group(1))} ", text)
    text = re.sub(r"\$(.*?)\$", lambda m: f" {math_to_text(m.group(1))} ", text)
    return text


def build_temp_sources(labels: dict[str, str]) -> Path:
    if TEMP.exists():
        shutil.rmtree(TEMP)
    (TEMP / "chapters").mkdir(parents=True)

    for src in (ROOT / "chapters").glob("*.tex"):
        text = src.read_text(encoding="utf-8")
        (TEMP / "chapters" / src.name).write_text(
            preprocess_latex(text, labels),
            encoding="utf-8",
        )

    thesis = (ROOT / "thesis_pandoc.tex").read_text(encoding="utf-8")
    thesis = thesis.replace(r"\input{chapters/", r"\input{_word_review_src/chapters/")
    thesis = preprocess_latex(thesis, labels)
    review_tex = TEMP / "thesis_pandoc_review.tex"
    review_tex.write_text(thesis, encoding="utf-8")
    return review_tex


def run_pandoc(review_tex: Path) -> None:
    cmd = [
        str(PANDOC),
        str(review_tex.relative_to(ROOT)),
        "--from",
        "latex",
        "--to",
        "docx",
        "--resource-path=.;images",
        "--bibliography=bibliography.bib",
        "--citeproc",
        "-o",
        str(OUT.relative_to(ROOT)),
    ]
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> None:
    labels = label_map()
    review_tex = build_temp_sources(labels)
    run_pandoc(review_tex)
    print(OUT)


if __name__ == "__main__":
    main()
