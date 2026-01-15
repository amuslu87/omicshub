#!/bin/bash

#######################################################################
# OmicsHub Nextflow Pipeline - Test Script
# Validates pipeline functionality with a small dataset
#######################################################################

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================"
echo "  OmicsHub Pipeline Test Suite"
echo "========================================"
echo ""

TEST_DIR="test_results_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$TEST_DIR"

# Test 1: Basic pipeline execution
echo -e "${BLUE}Test 1: Basic pipeline execution${NC}"
nextflow run main.nf \
    -profile test \
    --outdir "$TEST_DIR" \
    --gene_list "BRCA1,TP53,KRAS" \
    --max_genes 3 \
    --max_go_terms 100 \
    -with-report "$TEST_DIR/report.html" \
    -with-timeline "$TEST_DIR/timeline.html" \
    -with-dag "$TEST_DIR/dag.html"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Test 1 PASSED${NC}"
else
    echo -e "${RED}✗ Test 1 FAILED${NC}"
    exit 1
fi

# Test 2: Check output files
echo -e "${BLUE}Test 2: Checking output files${NC}"

REQUIRED_FILES=(
    "$TEST_DIR/genes/genes.csv"
    "$TEST_DIR/ontology/go_terms.csv"
    "$TEST_DIR/annotations/gene_go_annotations.csv"
    "$TEST_DIR/database/database_stats.json"
    "$TEST_DIR/pipeline_report.html"
)

ALL_EXIST=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}  ✓ Found: $file${NC}"
    else
        echo -e "${RED}  ✗ Missing: $file${NC}"
        ALL_EXIST=false
    fi
done

if [ "$ALL_EXIST" = true ]; then
    echo -e "${GREEN}✓ Test 2 PASSED${NC}"
else
    echo -e "${RED}✗ Test 2 FAILED${NC}"
    exit 1
fi

# Test 3: Validate data
echo -e "${BLUE}Test 3: Validating data content${NC}"

# Check genes.csv has data
GENE_COUNT=$(wc -l < "$TEST_DIR/genes/genes.csv")
if [ "$GENE_COUNT" -gt 1 ]; then
    echo -e "${GREEN}  ✓ genes.csv has $GENE_COUNT lines${NC}"
else
    echo -e "${RED}  ✗ genes.csv is empty${NC}"
    exit 1
fi

# Check go_terms.csv has data
GO_COUNT=$(wc -l < "$TEST_DIR/ontology/go_terms.csv")
if [ "$GO_COUNT" -gt 1 ]; then
    echo -e "${GREEN}  ✓ go_terms.csv has $GO_COUNT lines${NC}"
else
    echo -e "${RED}  ✗ go_terms.csv is empty${NC}"
    exit 1
fi

# Check annotations.csv has data
ANN_COUNT=$(wc -l < "$TEST_DIR/annotations/gene_go_annotations.csv")
if [ "$ANN_COUNT" -gt 1 ]; then
    echo -e "${GREEN}  ✓ gene_go_annotations.csv has $ANN_COUNT lines${NC}"
else
    echo -e "${RED}  ✗ gene_go_annotations.csv is empty${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Test 3 PASSED${NC}"

# Test 4: Database validation
echo -e "${BLUE}Test 4: Validating database${NC}"

DB_GENE_COUNT=$(sudo -u postgres psql -d omicshub -tAc "SELECT COUNT(*) FROM genes;")
DB_GO_COUNT=$(sudo -u postgres psql -d omicshub -tAc "SELECT COUNT(*) FROM go_terms;")
DB_ANN_COUNT=$(sudo -u postgres psql -d omicshub -tAc "SELECT COUNT(*) FROM gene_go_annotations;")

echo -e "${GREEN}  ✓ Database has $DB_GENE_COUNT genes${NC}"
echo -e "${GREEN}  ✓ Database has $DB_GO_COUNT GO terms${NC}"
echo -e "${GREEN}  ✓ Database has $DB_ANN_COUNT annotations${NC}"

if [ "$DB_GENE_COUNT" -gt 0 ] && [ "$DB_GO_COUNT" -gt 0 ] && [ "$DB_ANN_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ Test 4 PASSED${NC}"
else
    echo -e "${RED}✗ Test 4 FAILED${NC}"
    exit 1
fi

# Test 5: Report generation
echo -e "${BLUE}Test 5: Checking reports${NC}"

if [ -f "$TEST_DIR/pipeline_report.html" ] && grep -q "Pipeline Completed" "$TEST_DIR/pipeline_report.html"; then
    echo -e "${GREEN}  ✓ HTML report generated successfully${NC}"
else
    echo -e "${RED}  ✗ HTML report missing or incomplete${NC}"
    exit 1
fi

if [ -f "$TEST_DIR/pipeline_summary.txt" ]; then
    echo -e "${GREEN}  ✓ Summary report generated${NC}"
else
    echo -e "${RED}  ✗ Summary report missing${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Test 5 PASSED${NC}"

# Summary
echo ""
echo -e "${GREEN}========================================"
echo "  ✓ ALL TESTS PASSED!"
echo "========================================${NC}"
echo ""
echo "Test results saved to: $TEST_DIR"
echo ""
echo "View reports:"
echo "  - Pipeline report: open $TEST_DIR/pipeline_report.html"
echo "  - Execution report: open $TEST_DIR/report.html"
echo "  - Timeline: open $TEST_DIR/timeline.html"
echo "  - DAG: open $TEST_DIR/dag.html"
echo ""
echo "Database status:"
echo "  - Genes: $DB_GENE_COUNT"
echo "  - GO terms: $DB_GO_COUNT"
echo "  - Annotations: $DB_ANN_COUNT"
echo ""
