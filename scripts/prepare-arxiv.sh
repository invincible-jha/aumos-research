#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 MuVeraAI Corporation
#
# prepare-arxiv.sh — Prepare arXiv supplementary materials tarball
#
# DISCLAIMER: This is simulation code for academic reproduction,
# not production implementation.
#
# Usage: ./scripts/prepare-arxiv.sh <package-name>
# Example: ./scripts/prepare-arxiv.sh graduated-trust-convergence

set -euo pipefail

# ── Constants ──────────────────────────────────────────────────────────────────
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PACKAGES_DIR="${REPO_ROOT}/packages"
OUTPUT_DIR="${REPO_ROOT}/.arxiv-build"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

# ── Colour helpers ─────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }
die()   { error "$*"; exit 1; }

# ── Usage ──────────────────────────────────────────────────────────────────────
usage() {
    cat <<EOF
Usage: $(basename "$0") <package-name> [--version <ver>]

Prepare an arXiv-ready supplementary materials tarball for a research package.

Arguments:
  package-name    Name of the package under packages/ (e.g. graduated-trust-convergence)

Options:
  --version <ver> Paper version string (default: v1.0.0)
  --help          Show this help

Output:
  .arxiv-build/<package-name>-arxiv-<version>-<timestamp>.tar.gz
  .arxiv-build/<package-name>-manifest-<timestamp>.txt
EOF
    exit 0
}

# ── Argument parsing ───────────────────────────────────────────────────────────
PACKAGE_NAME=""
VERSION="v1.0.0"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h) usage ;;
        --version) shift; VERSION="${1}"; shift ;;
        -*) die "Unknown option: $1" ;;
        *) PACKAGE_NAME="$1"; shift ;;
    esac
done

[[ -z "${PACKAGE_NAME}" ]] && die "Package name is required. Run with --help for usage."

# ── Validate package ───────────────────────────────────────────────────────────
PACKAGE_DIR="${PACKAGES_DIR}/${PACKAGE_NAME}"
[[ -d "${PACKAGE_DIR}" ]] || die "Package not found: ${PACKAGE_DIR}"

info "Validating package: ${PACKAGE_NAME}"

REQUIRED_FILES=("README.md")
for req in "${REQUIRED_FILES[@]}"; do
    if [[ ! -f "${PACKAGE_DIR}/${req}" ]]; then
        die "Required file missing: ${PACKAGE_DIR}/${req}"
    fi
done
ok "Required files present"

# Check src/ directory exists and has Python files
SRC_DIR="${PACKAGE_DIR}/src"
if [[ ! -d "${SRC_DIR}" ]]; then
    die "No src/ directory found in ${PACKAGE_DIR}"
fi

PY_FILES=( "${SRC_DIR}"/*.py )
if [[ ${#PY_FILES[@]} -eq 0 ]] || [[ ! -f "${PY_FILES[0]}" ]]; then
    die "No Python source files found in ${SRC_DIR}"
fi
ok "Found ${#PY_FILES[@]} Python source file(s)"

# ── Python syntax validation ───────────────────────────────────────────────────
info "Running Python syntax checks..."
SYNTAX_ERRORS=0
for py_file in "${PY_FILES[@]}"; do
    if python3 -m py_compile "${py_file}" 2>/dev/null; then
        ok "  Syntax OK: $(basename "${py_file}")"
    else
        warn "  Syntax FAIL: $(basename "${py_file}")"
        SYNTAX_ERRORS=$((SYNTAX_ERRORS + 1))
    fi
done

if [[ ${SYNTAX_ERRORS} -gt 0 ]]; then
    die "Syntax errors in ${SYNTAX_ERRORS} file(s). Fix before submission."
fi

# ── License header validation ──────────────────────────────────────────────────
info "Checking license headers..."
MISSING_HEADERS=0
for py_file in "${PY_FILES[@]}"; do
    if ! grep -q "SPDX-License-Identifier: MIT" "${py_file}"; then
        warn "  Missing license header: $(basename "${py_file}")"
        MISSING_HEADERS=$((MISSING_HEADERS + 1))
    fi
done

if [[ ${MISSING_HEADERS} -gt 0 ]]; then
    warn "${MISSING_HEADERS} file(s) missing SPDX license headers"
fi

# ── Collect files ──────────────────────────────────────────────────────────────
info "Collecting files for tarball..."

BUILD_STAGING="${OUTPUT_DIR}/${PACKAGE_NAME}-${VERSION}"
mkdir -p "${BUILD_STAGING}/src"

# Copy README
cp "${PACKAGE_DIR}/README.md" "${BUILD_STAGING}/"

# Copy source files
for py_file in "${PY_FILES[@]}"; do
    cp "${py_file}" "${BUILD_STAGING}/src/"
done

# Copy notebooks if present
NOTEBOOKS_DIR="${PACKAGE_DIR}/notebooks"
if [[ -d "${NOTEBOOKS_DIR}" ]]; then
    mkdir -p "${BUILD_STAGING}/notebooks"
    find "${NOTEBOOKS_DIR}" -name "*.ipynb" -exec cp {} "${BUILD_STAGING}/notebooks/" \;
    NB_COUNT=$(find "${BUILD_STAGING}/notebooks" -name "*.ipynb" | wc -l)
    ok "Copied ${NB_COUNT} notebook(s)"
fi

# Copy colab template if present
COLAB_TEMPLATE="${REPO_ROOT}/colab-templates/${PACKAGE_NAME//-/_}.py"
if [[ -f "${COLAB_TEMPLATE}" ]]; then
    mkdir -p "${BUILD_STAGING}/colab"
    cp "${COLAB_TEMPLATE}" "${BUILD_STAGING}/colab/"
    ok "Copied Colab template"
fi

# ── Generate manifest ──────────────────────────────────────────────────────────
MANIFEST_FILE="${OUTPUT_DIR}/${PACKAGE_NAME}-manifest-${TIMESTAMP}.txt"
{
    echo "arXiv Supplementary Materials Manifest"
    echo "Package: ${PACKAGE_NAME}"
    echo "Version: ${VERSION}"
    echo "Generated: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
    echo "========================================"
    find "${BUILD_STAGING}" -type f | sort | while read -r f; do
        rel="${f#"${BUILD_STAGING}/"}"
        size=$(wc -c < "${f}")
        echo "  ${rel}  (${size} bytes)"
    done
    echo "========================================"
    TOTAL=$(find "${BUILD_STAGING}" -type f | xargs wc -c 2>/dev/null | tail -1 | awk '{print $1}')
    echo "Total: ${TOTAL} bytes"
} > "${MANIFEST_FILE}"

ok "Manifest written: ${MANIFEST_FILE}"

# ── Create tarball ─────────────────────────────────────────────────────────────
TARBALL="${OUTPUT_DIR}/${PACKAGE_NAME}-arxiv-${VERSION}-${TIMESTAMP}.tar.gz"
tar -czf "${TARBALL}" -C "${OUTPUT_DIR}" "${PACKAGE_NAME}-${VERSION}"
ok "Tarball created: ${TARBALL}"

# ── Summary ───────────────────────────────────────────────────────────────────
TARBALL_SIZE=$(wc -c < "${TARBALL}")
FILE_COUNT=$(find "${BUILD_STAGING}" -type f | wc -l)

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  arXiv Submission Package Ready${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "  Package:  ${PACKAGE_NAME} ${VERSION}"
echo "  Files:    ${FILE_COUNT} file(s)"
echo "  Size:     ${TARBALL_SIZE} bytes (compressed)"
echo "  Tarball:  ${TARBALL}"
echo "  Manifest: ${MANIFEST_FILE}"
echo ""
echo "Next: upload the tarball as arXiv supplementary material."
