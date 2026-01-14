# OmicsHub Docker Database - Fix Instructions

## Problem
The scripts are trying to connect to `localhost`, but inside Docker containers, they need to connect to the service name `db`.

## Solution - 3 Simple Steps

### Step 1: Copy the data loader script into your project

Copy the file `load_all_data.py` to your omicshub project:

```bash
# Navigate to your project
cd ~/omicshub

# Create the script directory if it doesn't exist
mkdir -p scripts

# Copy the data loader (adjust path as needed)
# You'll need to create this file in your project with the content provided
```

### Step 2: Run the data loader inside the Docker container

```bash
# Make sure containers are running
docker-compose up -d

# Check container status
docker-compose ps

# Run the data loader
docker-compose exec api python /app/load_all_data.py
```

**ALTERNATIVE:** If you can't get the script into the container, copy it directly:

```bash
# Create the file locally, then:
docker cp load_all_data.py omicshub-api:/app/load_all_data.py

# Then run it:
docker-compose exec api python /app/load_all_data.py
```

### Step 3: Verify the data

```bash
# Check database tables
docker-compose exec db psql -U postgres -d omicshub -c "\dt"

# Count records
docker-compose exec db psql -U postgres -d omicshub -c "SELECT COUNT(*) FROM genes;"
docker-compose exec db psql -U postgres -d omicshub -c "SELECT COUNT(*) FROM go_terms;"
docker-compose exec db psql -U postgres -d omicshub -c "SELECT COUNT(*) FROM gene_go_annotations;"

# Test the API
curl http://localhost:8000/health
curl http://localhost:8000/stats
curl http://localhost:8000/genes
```

## Expected Results

✅ **genes table:** 10 records  
✅ **go_terms table:** 17 records  
✅ **gene_go_annotations table:** 28 records  
✅ **API responds** with data

## If Step 2 Fails

If you can't copy or run the script, you can load data **directly via SQL**:

```bash
# Connect to database
docker-compose exec -i db psql -U postgres -d omicshub << 'EOF'

-- Insert genes
INSERT INTO genes (gene_id, symbol, description, chromosome, gene_type) VALUES
(672, 'BRCA1', 'BRCA1 DNA repair associated', '17', 'protein-coding'),
(675, 'BRCA2', 'BRCA2 DNA repair associated', '13', 'protein-coding'),
(7157, 'TP53', 'tumor protein p53', '17', 'protein-coding'),
(5728, 'PTEN', 'phosphatase and tensin homolog', '10', 'protein-coding'),
(3845, 'KRAS', 'KRAS proto-oncogene, GTPase', '12', 'protein-coding'),
(1956, 'EGFR', 'epidermal growth factor receptor', '7', 'protein-coding'),
(4893, 'NRAS', 'NRAS proto-oncogene, GTPase', '1', 'protein-coding'),
(673, 'BRAF', 'B-Raf proto-oncogene', '7', 'protein-coding'),
(5290, 'PIK3CA', 'phosphatidylinositol-4,5-bisphosphate 3-kinase', '3', 'protein-coding'),
(5594, 'MAPK1', 'mitogen-activated protein kinase 1', '22', 'protein-coding')
ON CONFLICT DO NOTHING;

-- Insert GO terms
INSERT INTO go_terms (go_id, term_name, namespace, definition) VALUES
('GO:0006281', 'DNA repair', 'biological_process', 'The process of restoring DNA after damage.'),
('GO:0006974', 'cellular response to DNA damage stimulus', 'biological_process', 'Any process that results in a change in state.'),
('GO:0051276', 'chromosome organization', 'biological_process', 'A process carried out at the cellular level.'),
('GO:0006302', 'double-strand break repair', 'biological_process', 'The repair of double-strand breaks in DNA.'),
('GO:0008283', 'cell population proliferation', 'biological_process', 'The multiplication of cells.'),
('GO:0006915', 'apoptotic process', 'biological_process', 'A form of programmed cell death.'),
('GO:0042981', 'regulation of apoptotic process', 'biological_process', 'Any process that modulates cell death.'),
('GO:0007165', 'signal transduction', 'biological_process', 'The cellular process in which a signal is conveyed.'),
('GO:0045786', 'negative regulation of cell cycle', 'biological_process', 'Any process that stops the cell cycle.'),
('GO:0003677', 'DNA binding', 'molecular_function', 'Interacting selectively with DNA.'),
('GO:0005524', 'ATP binding', 'molecular_function', 'Interacting selectively with ATP.'),
('GO:0004672', 'protein kinase activity', 'molecular_function', 'Catalysis of phosphorylation.'),
('GO:0005515', 'protein binding', 'molecular_function', 'Interacting selectively with any protein.'),
('GO:0005634', 'nucleus', 'cellular_component', 'A membrane-bounded organelle.'),
('GO:0005737', 'cytoplasm', 'cellular_component', 'Contents of a cell excluding nucleus.'),
('GO:0005886', 'plasma membrane', 'cellular_component', 'The membrane surrounding a cell.')
ON CONFLICT DO NOTHING;

-- Insert annotations
INSERT INTO gene_go_annotations (gene_id, go_id, evidence_code, source) VALUES
(672, 'GO:0006281', 'IDA', 'UniProt'),
(672, 'GO:0006974', 'IDA', 'UniProt'),
(672, 'GO:0051276', 'IDA', 'UniProt'),
(672, 'GO:0006302', 'IDA', 'UniProt'),
(672, 'GO:0003677', 'IDA', 'UniProt'),
(675, 'GO:0006281', 'IDA', 'UniProt'),
(675, 'GO:0006302', 'IDA', 'UniProt'),
(675, 'GO:0003677', 'IDA', 'UniProt'),
(7157, 'GO:0006915', 'IDA', 'UniProt'),
(7157, 'GO:0042981', 'IDA', 'UniProt'),
(7157, 'GO:0045786', 'IDA', 'UniProt'),
(7157, 'GO:0003677', 'IDA', 'UniProt'),
(5728, 'GO:0008283', 'IMP', 'UniProt'),
(5728, 'GO:0042981', 'IMP', 'UniProt'),
(3845, 'GO:0007165', 'IDA', 'UniProt'),
(3845, 'GO:0008283', 'IDA', 'UniProt'),
(3845, 'GO:0005524', 'IDA', 'UniProt'),
(1956, 'GO:0007165', 'IDA', 'UniProt'),
(1956, 'GO:0004672', 'IDA', 'UniProt'),
(1956, 'GO:0005886', 'IDA', 'UniProt'),
(4893, 'GO:0007165', 'IDA', 'UniProt'),
(4893, 'GO:0005524', 'IDA', 'UniProt'),
(673, 'GO:0007165', 'IDA', 'UniProt'),
(673, 'GO:0004672', 'IDA', 'UniProt'),
(5290, 'GO:0007165', 'IDA', 'UniProt'),
(5290, 'GO:0005524', 'IDA', 'UniProt'),
(5594, 'GO:0007165', 'IDA', 'UniProt'),
(5594, 'GO:0004672', 'IDA', 'UniProt')
ON CONFLICT DO NOTHING;

-- Verify
SELECT 'Genes:', COUNT(*) FROM genes;
SELECT 'GO Terms:', COUNT(*) FROM go_terms;
SELECT 'Annotations:', COUNT(*) FROM gene_go_annotations;

EOF
```

## What This Fixes

The core issue is that scripts inside Docker need to use:
- **host:** `db` (not `localhost`)
- **port:** `5432`
- **database:** `omicshub`

The `load_all_data.py` script uses environment variables from `docker-compose.yml` which are automatically set to the correct values.

## Once Data is Loaded

1. **Test API:** Open http://localhost:8000/docs
2. **View data:** 
   - GET /genes
   - GET /stats
   - GET /genes/BRCA1/functions
3. **Commit to Git:**
   ```bash
   git add load_all_data.py
   git commit -m "feat: Docker-compatible data loader"
   git push origin main
   ```

## Ready for Day 5!

Once data is loaded, you'll be ready for:
- ✅ Advanced ontology-driven queries
- ✅ Pathway enrichment analysis
- ✅ Data visualization
- ✅ Nextflow pipeline (Day 6)
