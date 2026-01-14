-- Create database (if not exists)
CREATE DATABASE omicshub;

-- Connect to the database
\c omicshub;

-- Create genes table
CREATE TABLE IF NOT EXISTS genes (
    gene_id SERIAL PRIMARY KEY,
    symbol VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    chromosome VARCHAR(10),
    gene_type VARCHAR(50),
    fetch_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create go_terms table
CREATE TABLE IF NOT EXISTS go_terms (
    go_id VARCHAR(20) PRIMARY KEY,
    term_name VARCHAR(255) NOT NULL,
    namespace VARCHAR(50),
    definition TEXT,
    is_obsolete BOOLEAN DEFAULT FALSE
);

-- Create gene_go_annotations table
CREATE TABLE IF NOT EXISTS gene_go_annotations (
    annotation_id SERIAL PRIMARY KEY,
    gene_id INTEGER REFERENCES genes(gene_id) ON DELETE CASCADE,
    go_id VARCHAR(20) REFERENCES go_terms(go_id) ON DELETE CASCADE,
    evidence_code VARCHAR(10),
    source VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(gene_id, go_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_go_namespace ON go_terms(namespace);
CREATE INDEX IF NOT EXISTS idx_go_term_name ON go_terms(term_name);
CREATE INDEX IF NOT EXISTS idx_annotations_gene ON gene_go_annotations(gene_id);
CREATE INDEX IF NOT EXISTS idx_annotations_go ON gene_go_annotations(go_id);
