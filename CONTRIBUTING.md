# Contributing to AumOS Research Companions

Thank you for your interest in contributing to AumOS research companions.

## CLA Requirement

All contributors must sign the MuVeraAI Contributor License Agreement (CLA) before any contribution can be merged. The CLA bot will prompt you on your first pull request.

## What We Accept

- Bug fixes in simulation code
- New experiment configurations
- Improved visualizations
- Documentation improvements
- Additional synthetic test scenarios

## What We Do NOT Accept

- Production algorithm implementations
- Real-world behavioral data
- Changes that cross fire line boundaries (see FIRE_LINE.md in each package)

## Development Setup

```bash
cd packages/<package-name>
pip install -e ".[dev]"
pytest
```

## Code Standards

- Python 3.10+
- Type hints on all function signatures
- ruff for linting
- mypy --strict for type checking
- pytest for testing
