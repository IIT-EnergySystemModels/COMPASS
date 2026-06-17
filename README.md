# COmputational Models for Planning And Supporting energy Systems

**The Energy Modeller’s Compass: Decision-support modelling for energy systems**

This repository is structured as a Quarto book for bilingual Python and Julia examples in energy-system decision-support modelling.

You can read the book and follow the examples online at [COMPASS](https://iit-energysystemmodels.github.io/COMPASS/).

The source code is available in this repository, and you can run the examples locally or in Binder.

[![Static Badge](https://img.shields.io/badge/Book-stable-blue?style=flat&logo=quarto&logoSize=auto)](https://iit-energysystemmodels.github.io/COMPASS/)
[![Render Quarto book](https://github.com/IIT-EnergySystemModels/COMPASS/actions/workflows/render-book.yml/badge.svg)](https://github.com/IIT-EnergySystemModels/COMPASS/actions/workflows/render-book.yml)
[![Test examples](https://github.com/IIT-EnergySystemModels/COMPASS/actions/workflows/test-examples.yml/badge.svg)](https://github.com/IIT-EnergySystemModels/COMPASS/actions/workflows/test-examples.yml)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/IIT-EnergySystemModels/COMPASS/HEAD)

## Repository layout

```text
.
├─ _quarto.yml
├─ index.qmd
├─ chapters/
│  ├─ 01-chapter/
│  │  ├─ index.qmd
│  │  └─ 01-description.qmd
│  ├─ 02-chapter/
│  │  ├─ index.qmd
│  │  └─ 01-description.qmd
│  ├─ ...
│  ├─ 10-chapter/
│  │  ├─ index.qmd
│  │  └─ 01-description.qmd
│  └─ references.qmd
├─ examples/
│  ├─ data/
│  ├─ python/
│  └─ julia/
├─ environment.yml
├─ pyproject.toml
├─ uv.lock
├─ Project.toml
└─ .github/workflows/
   ├─ render-book.yml
   └─ test-examples.yml
```

## Local development

Chapters are organised as folders. Each chapter folder has an `index.qmd` file that defines the chapter and includes one numbered `.qmd` file per subchapter.

Install Quarto and uv, then install the Python and Julia environments:

```bash
uv sync
uv run python -m ipykernel install --user --name compass-python --display-name "Python (COMPASS uv)"
julia --project=. -e 'using Pkg; Pkg.instantiate()'
julia --project=. -e 'using IJulia; IJulia.installkernel("julia", "--project=@.")'
```

Render the HTML book:

```bash
uv run quarto render --to html
```

Run the example checks:

```bash
uv run python examples/python/dispatch_model.py
julia --project=. examples/julia/dispatch_model.jl
```

## Publishing and execution

GitHub Actions renders the Quarto book on pull requests and deploys the HTML output to GitHub Pages on pushes to `main`. A second workflow runs the Python and Julia example scripts so rendered material is backed by executable examples.

Binder uses `environment.yml` and `Project.toml` to provide Python and Julia kernels side by side for readers. The Python project dependencies are managed with `uv` through `pyproject.toml` and `uv.lock`.
