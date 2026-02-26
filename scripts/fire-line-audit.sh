#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
#
# Fire Line Audit — scans all source files for forbidden identifiers.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EXIT_CODE=0

FORBIDDEN=(
  "progressLevel"
  "promoteLevel"
  "computeTrustScore"
  "behavioralScore"
  "adaptiveBudget"
  "optimizeBudget"
  "predictSpending"
  "detectAnomaly"
  "generateCounterfactual"
  "PersonalWorldModel"
  "MissionAlignment"
  "SocialTrust"
  "CognitiveLoop"
  "AttentionFilter"
  "GOVERNANCE_PIPELINE"
)

echo "=== Fire Line Audit: aumos-research ==="
echo "Scanning: ${REPO_ROOT}/packages/"

for term in "${FORBIDDEN[@]}"; do
  matches=$(grep -rn --include="*.py" --include="*.json" --include="*.toml" \
    "${term}" "${REPO_ROOT}/packages/" 2>/dev/null || true)
  if [ -n "${matches}" ]; then
    echo "VIOLATION: '${term}' found:"
    echo "${matches}"
    EXIT_CODE=1
  fi
done

if [ ${EXIT_CODE} -eq 0 ]; then
  echo "PASSED: Zero fire line violations."
else
  echo "FAILED: Fire line violations detected."
fi

exit ${EXIT_CODE}
