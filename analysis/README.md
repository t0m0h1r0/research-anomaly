# Numerical Evaluation Workspace

Use this directory for reproducible checks that support research claims,
experiment results, figures, memory estimates, or manuscript edits.

Each promoted study should use:

```text
analysis/{study}/
  run.py
  README.md
  config.yaml or config.json
  results/
    manifest.json
    run.log
    metrics.csv or metrics.json
    figures/*.pdf or *.png
```

`manifest.json` is required before a numerical result can support a manuscript
or research-summary claim. It should record the exact command, dataset refs,
split protocol, feature schema, parameters, Python and package versions, output
files, random seed or `null`, timestamp, metrics, and verdict.

Exploratory notebooks may live in `notebooks/`, but notebook-only output is not
accepted as evidence.
