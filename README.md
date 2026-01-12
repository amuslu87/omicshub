🧬 OmicsHub: Computational Infrastructure for Genomics Research

This is a Portfolio Study for Mid to Senior Level Bioinformaticians who are interested in scalable, end-to-end data infrastructure platform for biological and genetic research, providing production-grade bioinformatics data engineering capabilities.

 🎯 Project Overview

OmicsHub showcases skills in:
- Data modeling with biological ontologies (GO, HPO)
- ETL pipeline development
- RESTful API design
- Containerization & workflow orchestration
- Cloud deployment (AWS)

 ✨ Current Features

- ✅ NCBI Entrez API integration for gene data retrieval
- ✅ PostgreSQL database with normalized schema
- ✅ 10 cancer-related genes loaded and validated
- ✅ Tested database connectivity with psycopg2

 🗄️ Database Schema

**genes** table:
- `gene_id` (INTEGER, PRIMARY KEY)
- `symbol` (VARCHAR)
- `description` (TEXT)
- `chromosome` (VARCHAR)
- `gene_type` (VARCHAR)
- `fetch_date` (TIMESTAMP)

📊 Sample Data

Currently loaded: BRCA1, BRCA2, TP53, PTEN, KRAS, EGFR, NRAS, BRAF, PIK3CA, MAPK1

 🛠️ Tech Stack

- **Language**: Python 3.13.2
- **Database**: PostgreSQL 16
- **Key Libraries**: 
  - Biopython 1.83
  - pandas 2.3.3
  - psycopg2-binary 2.9.11
  - fastapi 0.128.0

 🚀 Quick Start
```bash
# Clone repository
git clone git@github.com:amuslu87/omicshub.git
cd omicshub
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run gene fetcher
python scripts/fetch_genes_simple.py
```
