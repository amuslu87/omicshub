# OmicsHub Nextflow Pipeline - Quick Start

## Step-by-Step Instructions

### Step 1: Verify Files
Make sure you have these files in `~/omicshub/workflows/nextflow/`:
- ✅ main.nf (most important!)
- ✅ nextflow.config
- ✅ setup_nextflow.sh
- ✅ test_pipeline.sh

### Step 2: Make Scripts Executable
```bash
cd ~/omicshub/workflows/nextflow
chmod +x setup_nextflow.sh test_pipeline.sh
```

### Step 3: Edit Configuration
Open `nextflow.config` and change the email:
```bash
nano nextflow.config
```
Find this line:
```
email = 'your.email@example.com'
```
Change it to your actual email (required by NCBI).

Press `Ctrl+O` to save, `Ctrl+X` to exit.

### Step 4: Run Setup
```bash
./setup_nextflow.sh
```
This will install Nextflow and check your system.

### Step 5: Test the Pipeline
```bash
nextflow run main.nf -profile test
```
This runs a quick test with 3 genes.

### Step 6: View Results
```bash
ls results/
open results/pipeline_report.html
```

### Step 7: Run Full Pipeline
```bash
nextflow run main.nf
```
This processes all 10 cancer genes.

## Troubleshooting

**If Nextflow not found:**
```bash
curl -s https://get.nextflow.io | bash
sudo mv nextflow /usr/local/bin/
```

**If PostgreSQL not running:**
```bash
sudo service postgresql start
```

**If database doesn't exist:**
```bash
sudo -u postgres psql -c "CREATE DATABASE omicshub;"
```

## What the Pipeline Does
1. Fetches genes from NCBI
2. Downloads Gene Ontology
3. Creates gene-GO annotations
4. Loads everything to PostgreSQL
5. Generates an HTML report

## Output Location
All results go to: `~/omicshub/workflows/nextflow/results/`
