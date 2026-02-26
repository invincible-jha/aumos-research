# commitment-extractor

Research companion code for **Paper 21: Extracting and Tracking Commitments from Agent Communications**.

> **DISCLAIMER: This is research simulation code, not the production algorithm.**
> All dynamics are simplified for academic analysis. All data is synthetic.
> This package does NOT contain Paper 21's LLM-powered extraction system or any
> production agent communication monitoring implementation.

---

## Overview

This package provides a reproducible simulation environment for studying commitment
extraction and lifecycle tracking from agent message streams. The model uses
rule-based regex pattern matching to identify promises, obligations, deadlines, and
conditional commitments within synthetic agent conversations, then tracks fulfillment
status over subsequent message exchanges.

The simulation is intentionally simplified: extraction uses regex patterns only (no
LLM inference), classification is rule-based, fulfillment checking is keyword
matching, and all conversation data is synthetically generated. This simplified model
is sufficient to reproduce the paper's figures without encoding any production system
logic.

**Four core phenomena are studied:**

1. **Commitment extraction precision** — how accurately rule-based patterns identify commitments
2. **Classification accuracy** — how well commitment types are categorized
3. **Fulfillment lifecycle** — tracking commitment states from active to fulfilled/expired
4. **Conversation analysis** — commitment density across different conversation types

---

## Installation

```bash
pip install commitment-extractor
# or, from source:
pip install -e ".[dev]"
```

**Requirements:** Python 3.10+, numpy >= 1.24, matplotlib >= 3.7

---

## Quick Start

```python
from commitment_extractor.model import CommitmentExtractor
from commitment_extractor.tracker import CommitmentTracker

extractor = CommitmentExtractor()
tracker = CommitmentTracker()

message = "I will complete the report by Friday and ensure all metrics are included."
commitments = extractor.extract(message, sender="agent-alpha", recipient="agent-beta")

for commitment in commitments:
    tracker.register(commitment)
    print(f"Extracted: [{commitment.commitment_type}] {commitment.text_span}")

print(f"Active commitments: {len(tracker.list_active())}")
```

---

## Running Experiments

Each experiment script reproduces one figure from the paper:

```bash
# Individual experiments
python experiments/exp1_basic_extraction.py
python experiments/exp2_classification_accuracy.py
python experiments/exp3_fulfillment_tracking.py
python experiments/exp4_conversation_analysis.py

# All experiments at once (saves figures to results/figures/)
python experiments/run_all.py
```

---

## Package Structure

```
src/commitment_extractor/
    model.py          # CommitmentExtractor — extract commitments (RULE-BASED, NOT LLM)
    classifier.py     # CommitmentClassifier — regex-based type classification
    tracker.py        # CommitmentTracker — lifecycle state management
    evaluation.py     # Precision/recall evaluation metrics
    scenarios.py      # Synthetic conversation datasets
    visualization.py  # Matplotlib figure generators
experiments/
    exp1_basic_extraction.py         -> Fig. 1: Extraction recall across message types
    exp2_classification_accuracy.py  -> Fig. 2: Type classification accuracy
    exp3_fulfillment_tracking.py     -> Fig. 3: Commitment fulfillment lifecycle
    exp4_conversation_analysis.py    -> Fig. 4: Commitment density by conversation type
    run_all.py                       -> Generates all figures
results/
    precomputed/                # Frozen JSON data for offline verification
    figures/                    # Generated figure output directory
```

---

## Reproducing Paper Results

Pre-computed result data is stored in `results/precomputed/fig{1-4}_data.json`.
These files were generated with `seed=42` and can be used to verify that your
installation produces identical results:

```python
import json
from commitment_extractor.model import CommitmentExtractor
from commitment_extractor.scenarios import SCENARIOS

with open("results/precomputed/fig1_data.json") as f:
    reference = json.load(f)

extractor = CommitmentExtractor()
scenario = SCENARIOS["mixed_conversation"]
total_extracted = sum(
    len(extractor.extract(msg.text, msg.sender, msg.recipient))
    for msg in scenario.messages
)
print(f"Total extracted: {total_extracted} (reference: {reference['total_extracted']})")
```

---

## Citing

```bibtex
@software{muveraai_ce_2026,
  title  = {Commitment Extractor: Extracting and Tracking Commitments from Agent Communications},
  author = {{MuVeraAI Research}},
  year   = {2026},
  url    = {https://github.com/aumos-ai/aumos-research},
  note   = {Research companion code for Paper 21}
}
```

Or use the `CITATION.cff` file at the root of this package.

---

## Constraints and Boundaries

See `FIRE_LINE.md` for the full constraint specification. Key points:

- Extraction uses **regex pattern matching ONLY** — NOT LLM-powered production extraction
- Paper 21's **full semantic extraction system is proprietary** and NOT included here
- All data is **synthetic** — no real agent communications
- Classification uses **static regex rules** — no learned or adaptive classifiers
- **No vector embeddings or semantic similarity** is implemented

---

## License

MIT License — Copyright (c) 2026 MuVeraAI Corporation. See `LICENSE`.
