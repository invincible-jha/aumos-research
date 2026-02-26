# AumOS Research Companions

Research companion code for AumOS governance protocol papers. Each package provides simulation code, experiment scripts, and pre-computed results for reproducing paper figures.

## Packages

| Package | Paper | Description |
|---|---|---|
| `graduated-trust-convergence` | Paper 13 | Trust progression convergence simulation |
| `governed-forgetting` | Paper 5 | Memory retention policy verification |
| `protocol-composition-verifier` | Papers 9/25 | Protocol composition formal properties |
| `economic-safety-verifier` | Paper 22 | Economic safety property verification |

## Important Disclaimer

All code in this repository is **research simulation code** for academic reproduction purposes. It does **NOT** contain production algorithms. All data is synthetic. See individual package READMEs for details.

## License

All packages: MIT

## Quick Start

```bash
# Install any package
cd packages/<package-name>
pip install -e ".[dev]"

# Run all experiments
python experiments/run_all.py

# Run tests
pytest
```

## Citation

Each package contains a `CITATION.cff` file with BibTeX entries. Please cite the relevant paper when using this code.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. All contributions require a signed CLA.
