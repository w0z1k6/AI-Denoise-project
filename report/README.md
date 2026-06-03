# Project Report (LaTeX)

English academic project report template for **Intelligent Audio Denoising Analysis Platform (Denoise Selection)**.

## Structure

```text
report/
  report.tex              # Main document
  references.bib          # Bibliography
  frontmatter/
    titlepage.tex
    abstract.tex
  chapters/               # 11 chapters (01--11)
  appendix/               # Appendices A & B
  figures/                # Place figures here
```

## Compile

Requires a LaTeX distribution with `pdflatex` and `biber` (TeX Live / MiKTeX).

```bash
cd report
pdflatex report.tex
biber report
pdflatex report.tex
pdflatex report.tex
```

Or with `latexmk`:

```bash
latexmk -pdf -bibtex report.tex
```

Output: `report/report.pdf`

## Writing Notes

- Replace `\todo{...}` placeholders as you fill in content.
- Update author metadata in `frontmatter/titlepage.tex` and `report.tex`.
- Add figures to `figures/` and include via `\includegraphics`.
- Target length: 40+ pages when sections are fully expanded with figures and results.
