# AumOS Research Companions — Agent Instructions

## Identity

This monorepo contains research companion code for AumOS governance protocol papers.
All packages are MIT licensed. All code is simulation-only for academic reproduction.

## ABSOLUTE RULES

1. All simulation models must include "this is simulation, not production" disclaimers
2. All data must be SYNTHETIC — never use real agent behavioral data
3. NEVER implement production algorithms — only simplified dynamics
4. NEVER reference PWM, MAE, STP, CognitiveLoop, or GOVERNANCE_PIPELINE
5. NEVER include specific tuning parameters or threshold values from production

## Forbidden Identifiers

progressLevel, promoteLevel, computeTrustScore, behavioralScore
adaptiveBudget, optimizeBudget, predictSpending
detectAnomaly, generateCounterfactual
PersonalWorldModel, MissionAlignment, SocialTrust
CognitiveLoop, AttentionFilter, GOVERNANCE_PIPELINE

## Code Standards

- Python 3.10+, type hints on all functions
- Pydantic v2 for configuration models
- numpy for numerical computation
- matplotlib for visualization
- ruff for linting, mypy --strict for type checking
- pytest for testing, >80% coverage

## License Header

Every source file:
```python
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
```
