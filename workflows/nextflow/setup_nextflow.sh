#!/bin/bash

#######################################################################
# OmicsHub Nextflow Pipeline - Quick Start Script
# Date: January 14, 2026
#######################################################################

set -e  # Exit on error

echo "========================================"
echo "  OmicsHub Nextflow Quick Start"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Nextflow is installed
echo -e "${BLUE}[1/5] Checking Nextflow installation...${NC}"
if ! command -v nextflow &> /dev/null; then
    echo -e "${YELLOW}Nextflow not found. Installing...${NC}"
    curl -s https://get.nextflow.io | bash
    sudo mv nextflow /usr/local/bin/
    echo -e "${GREEN}✓ Nextflow installed${NC}"
else
    VERSION=$(nextflow -version | head -n 1)
    echo -e "${GREEN}✓ Nextflow found: $VERSION${NC}"
fi

# Check PostgreSQL
echo -e "${BLUE}[2/5] Checking PostgreSQL...${NC}"
if sudo service postgresql status | grep -q "is running"; then
    echo -e "${GREEN}✓ PostgreSQL is running${NC}"
else
    echo -e "${YELLOW}Starting PostgreSQL...${NC}"
    sudo service postgresql start
    echo -e "${GREEN}✓ PostgreSQL started${NC}"
fi

# Check database
echo -e "${BLUE}[3/5] Checking database...${NC}"
if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw omicshub; then
    echo -e "${GREEN}✓ Database 'omicshub' exists${NC}"
else
    echo -e "${YELLOW}Creating database 'omicshub'...${NC}"
    sudo -u postgres psql -c "CREATE DATABASE omicshub;"
    echo -e "${GREEN}✓ Database created${NC}"
fi

# Check tables
echo -e "${BLUE}[4/5] Checking database tables...${NC}"
TABLE_COUNT=$(sudo -u postgres psql -d omicshub -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';")

if [ "$TABLE_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}Creating database schema...${NC}"
    sudo -u postgres psql -d omicshub << 'EOF'
-- Create genes table
CREATE TABLE IF NOT EXISTS genes (
    gene_id VARCHAR(50) PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL,
    description TEXT,
    chromosome VARCHAR(50),
    gene_type VARCHAR(50),
    fetch_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_genes_symbol ON genes(symbol);

-- Create GO terms table
CREATE TABLE IF NOT EXISTS go_terms (
    go_id VARCHAR(20) PRIMARY KEY,
    term_name VARCHAR(500) NOT NULL,
    namespace VARCHAR(50),
    definition TEXT,
    is_obsolete BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_go_terms_namespace ON go_terms(namespace);
CREATE INDEX IF NOT EXISTS idx_go_terms_name ON go_terms(term_name);

-- Create gene-GO annotations table
CREATE TABLE IF NOT EXISTS gene_go_annotations (
    annotation_id SERIAL PRIMARY KEY,
    gene_id VARCHAR(50) REFERENCES genes(gene_id) ON DELETE CASCADE,
    go_id VARCHAR(20) REFERENCES go_terms(go_id) ON DELETE CASCADE,
    evidence_code VARCHAR(10),
    source VARCHAR(100),
    annotation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(gene_id, go_id, evidence_code)
);

CREATE INDEX IF NOT EXISTS idx_annotations_gene ON gene_go_annotations(gene_id);
CREATE INDEX IF NOT EXISTS idx_annotations_go ON gene_go_annotations(go_id);
EOF
    echo -e "${GREEN}✓ Database schema created${NC}"
else
    echo -e "${GREEN}✓ Tables already exist ($TABLE_COUNT tables)${NC}"
fi

# Install Python dependencies
echo -e "${BLUE}[5/5] Checking Python dependencies...${NC}"
if python3 -c "import Bio" 2>/dev/null; then
    echo -e "${GREEN}✓ Biopython installed${NC}"
else
    echo -e "${YELLOW}Installing Biopython...${NC}"
    pip install biopython --break-system-packages
fi

if python3 -c "import psycopg2" 2>/dev/null; then
    echo -e "${GREEN}✓ psycopg2 installed${NC}"
else
    echo -e "${YELLOW}Installing psycopg2...${NC}"
    pip install psycopg2-binary --break-system-packages
fi

echo ""
echo -e "${GREEN}========================================"
echo "  ✓ Setup Complete!"
echo "========================================${NC}"
echo ""
echo "Ready to run the pipeline!"
echo ""
echo "Basic usage:"
echo "  nextflow run main.nf"
echo ""
echo "With custom parameters:"
echo "  nextflow run main.nf --gene_list 'BRCA1,TP53' --email 'your@email.com'"
echo ""
echo "Test run (small dataset):"
echo "  nextflow run main.nf -profile test"
echo ""
echo "Resume after interruption:"
echo "  nextflow run main.nf -resume"
echo ""
echo "View help:"
echo "  nextflow run main.nf --help"
echo ""
echo -e "${YELLOW}Don't forget to set your email in nextflow.config!${NC}"
echo "NCBI requires an email address for Entrez queries."
echo ""
