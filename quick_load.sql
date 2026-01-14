-- OmicsHub Quick Data Loader - Run this inside Docker PostgreSQL
-- Usage: docker-compose exec -i db psql -U postgres -d omicshub < quick_load.sql

-- Insert genes
INSERT INTO genes (gene_id, symbol, description, chromosome, gene_type) VALUES
(672, 'BRCA1', 'BRCA1 DNA repair associated', '17', 'protein-coding'),
(675, 'BRCA2', 'BRCA2 DNA repair associated', '13', 'protein-coding'),
(7157, 'TP53', 'tumor protein p53', '17', 'protein-coding'),
(5728, 'PTEN', 'phosphatase and tensin homolog', '10', 'protein-coding'),
(3845, 'KRAS', 'KRAS proto-oncogene, GTPase', '12', 'protein-coding'),
(1956, 'EGFR', 'epidermal growth factor receptor', '7', 'protein-coding'),
(4893, 'NRAS', 'NRAS proto-oncogene, GTPase', '1', 'protein-coding'),
(673, 'BRAF', 'B-Raf proto-oncogene, serine/threonine kinase', '7', 'protein-coding'),
(5290, 'PIK3CA', 'phosphatidylinositol-4,5-bisphosphate 3-kinase catalytic subunit alpha', '3', 'protein-coding'),
(5594, 'MAPK1', 'mitogen-activated protein kinase 1', '22', 'protein-coding')
ON CONFLICT (gene_id) DO NOTHING;

-- Insert GO terms
INSERT INTO go_terms (go_id, term_name, namespace, definition, is_obsolete) VALUES
('GO:0006281', 'DNA repair', 'biological_process', 'The process of restoring DNA after damage.', FALSE),
('GO:0006974', 'cellular response to DNA damage stimulus', 'biological_process', 'Any process that results in a change in state or activity of a cell.', FALSE),
('GO:0051276', 'chromosome organization', 'biological_process', 'A process that is carried out at the cellular level.', FALSE),
('GO:0006302', 'double-strand break repair', 'biological_process', 'The repair of double-strand breaks in DNA.', FALSE),
('GO:0008283', 'cell population proliferation', 'biological_process', 'The multiplication or reproduction of cells.', FALSE),
('GO:0006915', 'apoptotic process', 'biological_process', 'A form of programmed cell death.', FALSE),
('GO:0042981', 'regulation of apoptotic process', 'biological_process', 'Any process that modulates the frequency, rate or extent of cell death.', FALSE),
('GO:0007165', 'signal transduction', 'biological_process', 'The cellular process in which a signal is conveyed.', FALSE),
('GO:0045786', 'negative regulation of cell cycle', 'biological_process', 'Any process that stops, prevents or reduces the frequency.', FALSE),
('GO:0003677', 'DNA binding', 'molecular_function', 'Any molecular function by which a gene product interacts selectively with DNA.', FALSE),
('GO:0005524', 'ATP binding', 'molecular_function', 'Interacting selectively and non-covalently with ATP.', FALSE),
('GO:0004672', 'protein kinase activity', 'molecular_function', 'Catalysis of the phosphorylation of an amino acid residue.', FALSE),
('GO:0005515', 'protein binding', 'molecular_function', 'Interacting selectively and non-covalently with any protein.', FALSE),
('GO:0005634', 'nucleus', 'cellular_component', 'A membrane-bounded organelle of eukaryotic cells.', FALSE),
('GO:0005737', 'cytoplasm', 'cellular_component', 'All of the contents of a cell excluding the nucleus.', FALSE),
('GO:0005886', 'plasma membrane', 'cellular_component', 'The membrane surrounding a cell.', FALSE)
ON CONFLICT (go_id) DO NOTHING;

-- Insert gene-GO annotations
INSERT INTO gene_go_annotations (gene_id, go_id, evidence_code, source) VALUES
-- BRCA1 annotations
(672, 'GO:0006281', 'IDA', 'UniProt'),
(672, 'GO:0006974', 'IDA', 'UniProt'),
(672, 'GO:0051276', 'IDA', 'UniProt'),
(672, 'GO:0006302', 'IDA', 'UniProt'),
(672, 'GO:0003677', 'IDA', 'UniProt'),
-- BRCA2 annotations
(675, 'GO:0006281', 'IDA', 'UniProt'),
(675, 'GO:0006302', 'IDA', 'UniProt'),
(675, 'GO:0003677', 'IDA', 'UniProt'),
-- TP53 annotations
(7157, 'GO:0006915', 'IDA', 'UniProt'),
(7157, 'GO:0042981', 'IDA', 'UniProt'),
(7157, 'GO:0045786', 'IDA', 'UniProt'),
(7157, 'GO:0003677', 'IDA', 'UniProt'),
-- PTEN annotations
(5728, 'GO:0008283', 'IMP', 'UniProt'),
(5728, 'GO:0042981', 'IMP', 'UniProt'),
-- KRAS annotations
(3845, 'GO:0007165', 'IDA', 'UniProt'),
(3845, 'GO:0008283', 'IDA', 'UniProt'),
(3845, 'GO:0005524', 'IDA', 'UniProt'),
-- EGFR annotations
(1956, 'GO:0007165', 'IDA', 'UniProt'),
(1956, 'GO:0004672', 'IDA', 'UniProt'),
(1956, 'GO:0005886', 'IDA', 'UniProt'),
-- NRAS annotations
(4893, 'GO:0007165', 'IDA', 'UniProt'),
(4893, 'GO:0005524', 'IDA', 'UniProt'),
-- BRAF annotations
(673, 'GO:0007165', 'IDA', 'UniProt'),
(673, 'GO:0004672', 'IDA', 'UniProt'),
-- PIK3CA annotations
(5290, 'GO:0007165', 'IDA', 'UniProt'),
(5290, 'GO:0005524', 'IDA', 'UniProt'),
-- MAPK1 annotations
(5594, 'GO:0007165', 'IDA', 'UniProt'),
(5594, 'GO:0004672', 'IDA', 'UniProt')
ON CONFLICT DO NOTHING;

-- Verify data loaded
\echo '=================================================='
\echo 'Data Loading Summary:'
\echo '=================================================='
SELECT 'Genes:' as table_name, COUNT(*) as record_count FROM genes
UNION ALL
SELECT 'GO Terms:', COUNT(*) FROM go_terms
UNION ALL
SELECT 'Annotations:', COUNT(*) FROM gene_go_annotations;

\echo ''
\echo 'Sample Data:'
\echo '=================================================='
SELECT symbol, description FROM genes LIMIT 5;
