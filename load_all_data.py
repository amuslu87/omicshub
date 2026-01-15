"""
OmicsHub - Complete Data Loader for Docker
This script loads all data into the Docker PostgreSQL database
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Database configuration for Docker
DB_CONFIG = {
    'host': os.getenv('DATABASE_HOST', 'db'),
    'port': os.getenv('DATABASE_PORT', '5432'),
    'database': os.getenv('DATABASE_NAME', 'omicshub'),
    'user': os.getenv('DATABASE_USER', 'postgres'),
    'password': os.getenv('DATABASE_PASSWORD', 'xxxx')
}

def get_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)

def create_tables():
    """Create all necessary tables"""
    print("\n" + "="*60)
    print("📋 Creating Database Tables")
    print("="*60)
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Create genes table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS genes (
            gene_id INTEGER PRIMARY KEY,
            symbol VARCHAR(50) NOT NULL,
            description TEXT,
            chromosome VARCHAR(10),
            gene_type VARCHAR(50),
            fetch_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("✅ Table 'genes' created")
    
    # Create go_terms table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS go_terms (
            go_id VARCHAR(20) PRIMARY KEY,
            term_name TEXT NOT NULL,
            namespace VARCHAR(50),
            definition TEXT,
            is_obsolete BOOLEAN DEFAULT FALSE
        );
    """)
    print("✅ Table 'go_terms' created")
    
    # Create gene_go_annotations table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS gene_go_annotations (
            annotation_id SERIAL PRIMARY KEY,
            gene_id INTEGER REFERENCES genes(gene_id),
            go_id VARCHAR(20) REFERENCES go_terms(go_id),
            evidence_code VARCHAR(10),
            source VARCHAR(50),
            annotation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("✅ Table 'gene_go_annotations' created")
    
    # Create indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_genes_symbol ON genes(symbol);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_go_terms_namespace ON go_terms(namespace);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_annotations_gene ON gene_go_annotations(gene_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_annotations_go ON gene_go_annotations(go_id);")
    print("✅ Indexes created")
    
    conn.commit()
    cur.close()
    conn.close()

def load_genes():
    """Load cancer genes data"""
    print("\n" + "="*60)
    print("🧬 Loading Cancer Genes Data")
    print("="*60)
    
    # Sample cancer genes with their NCBI gene IDs
    genes_data = [
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
    ]
    
    conn = get_connection()
    cur = conn.cursor()
    
    for gene_id, symbol, description, chromosome, gene_type in genes_data:
        cur.execute("""
            INSERT INTO genes (gene_id, symbol, description, chromosome, gene_type)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (gene_id) DO UPDATE 
            SET symbol = EXCLUDED.symbol,
                description = EXCLUDED.description,
                chromosome = EXCLUDED.chromosome,
                gene_type = EXCLUDED.gene_type;
        """, (gene_id, symbol, description, chromosome, gene_type))
        print(f"  ✓ {symbol}")
    
    conn.commit()
    
    # Verify
    cur.execute("SELECT COUNT(*) FROM genes;")
    count = cur.fetchone()[0]
    print(f"\n✅ Loaded {count} genes")
    
    cur.close()
    conn.close()

def load_go_terms():
    """Load sample GO terms"""
    print("\n" + "="*60)
    print("🔬 Loading Gene Ontology Terms")
    print("="*60)
    
    # Sample GO terms relevant to cancer genes
    go_terms = [
        ('GO:0006281', 'DNA repair', 'biological_process', 'The process of restoring DNA after damage.'),
        ('GO:0006974', 'cellular response to DNA damage stimulus', 'biological_process', 'Any process that results in a change in state or activity of a cell.'),
        ('GO:0051276', 'chromosome organization', 'biological_process', 'A process that is carried out at the cellular level.'),
        ('GO:0006302', 'double-strand break repair', 'biological_process', 'The repair of double-strand breaks in DNA.'),
        ('GO:0008283', 'cell population proliferation', 'biological_process', 'The multiplication or reproduction of cells.'),
        ('GO:0006915', 'apoptotic process', 'biological_process', 'A form of programmed cell death.'),
        ('GO:0042981', 'regulation of apoptotic process', 'biological_process', 'Any process that modulates the frequency, rate or extent of cell death.'),
        ('GO:0007165', 'signal transduction', 'biological_process', 'The cellular process in which a signal is conveyed.'),
        ('GO:0008283', 'cell proliferation', 'biological_process', 'The multiplication or reproduction of cells.'),
        ('GO:0045786', 'negative regulation of cell cycle', 'biological_process', 'Any process that stops, prevents or reduces the frequency.'),
        ('GO:0003677', 'DNA binding', 'molecular_function', 'Any molecular function by which a gene product interacts selectively with DNA.'),
        ('GO:0005524', 'ATP binding', 'molecular_function', 'Interacting selectively and non-covalently with ATP.'),
        ('GO:0004672', 'protein kinase activity', 'molecular_function', 'Catalysis of the phosphorylation of an amino acid residue.'),
        ('GO:0005515', 'protein binding', 'molecular_function', 'Interacting selectively and non-covalently with any protein.'),
        ('GO:0005634', 'nucleus', 'cellular_component', 'A membrane-bounded organelle of eukaryotic cells.'),
        ('GO:0005737', 'cytoplasm', 'cellular_component', 'All of the contents of a cell excluding the nucleus.'),
        ('GO:0005886', 'plasma membrane', 'cellular_component', 'The membrane surrounding a cell.')
    ]
    
    conn = get_connection()
    cur = conn.cursor()
    
    for go_id, term_name, namespace, definition in go_terms:
        cur.execute("""
            INSERT INTO go_terms (go_id, term_name, namespace, definition)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (go_id) DO UPDATE 
            SET term_name = EXCLUDED.term_name,
                namespace = EXCLUDED.namespace,
                definition = EXCLUDED.definition;
        """, (go_id, term_name, namespace, definition))
        print(f"  ✓ {go_id}: {term_name}")
    
    conn.commit()
    
    # Verify
    cur.execute("SELECT COUNT(*) FROM go_terms;")
    count = cur.fetchone()[0]
    print(f"\n✅ Loaded {count} GO terms")
    
    cur.close()
    conn.close()

def load_annotations():
    """Load gene-GO annotations"""
    print("\n" + "="*60)
    print("📊 Loading Gene-GO Annotations")
    print("="*60)
    
    # Gene-GO annotations (gene_id, go_id, evidence_code)
    annotations = [
        # BRCA1 annotations
        (672, 'GO:0006281', 'IDA', 'UniProt'),
        (672, 'GO:0006974', 'IDA', 'UniProt'),
        (672, 'GO:0051276', 'IDA', 'UniProt'),
        (672, 'GO:0006302', 'IDA', 'UniProt'),
        (672, 'GO:0003677', 'IDA', 'UniProt'),
        # BRCA2 annotations
        (675, 'GO:0006281', 'IDA', 'UniProt'),
        (675, 'GO:0006302', 'IDA', 'UniProt'),
        (675, 'GO:0003677', 'IDA', 'UniProt'),
        # TP53 annotations
        (7157, 'GO:0006915', 'IDA', 'UniProt'),
        (7157, 'GO:0042981', 'IDA', 'UniProt'),
        (7157, 'GO:0045786', 'IDA', 'UniProt'),
        (7157, 'GO:0003677', 'IDA', 'UniProt'),
        # PTEN annotations
        (5728, 'GO:0008283', 'IMP', 'UniProt'),
        (5728, 'GO:0042981', 'IMP', 'UniProt'),
        # KRAS annotations
        (3845, 'GO:0007165', 'IDA', 'UniProt'),
        (3845, 'GO:0008283', 'IDA', 'UniProt'),
        (3845, 'GO:0005524', 'IDA', 'UniProt'),
        # EGFR annotations
        (1956, 'GO:0007165', 'IDA', 'UniProt'),
        (1956, 'GO:0004672', 'IDA', 'UniProt'),
        (1956, 'GO:0005886', 'IDA', 'UniProt'),
        # NRAS annotations
        (4893, 'GO:0007165', 'IDA', 'UniProt'),
        (4893, 'GO:0005524', 'IDA', 'UniProt'),
        # BRAF annotations
        (673, 'GO:0007165', 'IDA', 'UniProt'),
        (673, 'GO:0004672', 'IDA', 'UniProt'),
        # PIK3CA annotations
        (5290, 'GO:0007165', 'IDA', 'UniProt'),
        (5290, 'GO:0005524', 'IDA', 'UniProt'),
        # MAPK1 annotations
        (5594, 'GO:0007165', 'IDA', 'UniProt'),
        (5594, 'GO:0004672', 'IDA', 'UniProt'),
    ]
    
    conn = get_connection()
    cur = conn.cursor()
    
    for gene_id, go_id, evidence_code, source in annotations:
        cur.execute("""
            INSERT INTO gene_go_annotations (gene_id, go_id, evidence_code, source)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (gene_id, go_id, evidence_code, source))
    
    conn.commit()
    
    # Verify
    cur.execute("SELECT COUNT(*) FROM gene_go_annotations;")
    count = cur.fetchone()[0]
    print(f"✅ Loaded {count} annotations")
    
    cur.close()
    conn.close()

def verify_data():
    """Verify all data is loaded correctly"""
    print("\n" + "="*60)
    print("✅ Data Verification Summary")
    print("="*60)
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Count genes
    cur.execute("SELECT COUNT(*) FROM genes;")
    genes_count = cur.fetchone()[0]
    print(f"  Genes: {genes_count}")
    
    # Count GO terms
    cur.execute("SELECT COUNT(*) FROM go_terms;")
    go_count = cur.fetchone()[0]
    print(f"  GO Terms: {go_count}")
    
    # Count annotations
    cur.execute("SELECT COUNT(*) FROM gene_go_annotations;")
    annotations_count = cur.fetchone()[0]
    print(f"  Annotations: {annotations_count}")
    
    # Show sample data
    print("\n📋 Sample genes:")
    cur.execute("SELECT symbol, description FROM genes LIMIT 5;")
    for row in cur.fetchall():
        print(f"  - {row[0]}: {row[1][:50]}...")
    
    print("\n📋 Sample GO terms:")
    cur.execute("SELECT go_id, term_name FROM go_terms LIMIT 5;")
    for row in cur.fetchall():
        print(f"  - {row[0]}: {row[1]}")
    
    print("\n📋 Sample annotations:")
    cur.execute("""
        SELECT g.symbol, go.term_name, a.evidence_code
        FROM gene_go_annotations a
        JOIN genes g ON a.gene_id = g.gene_id
        JOIN go_terms go ON a.go_id = go.go_id
        LIMIT 5;
    """)
    for row in cur.fetchall():
        print(f"  - {row[0]} → {row[1]} ({row[2]})")
    
    cur.close()
    conn.close()

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("🚀 OmicsHub - Complete Data Loader")
    print("="*60)
    print(f"Database: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        create_tables()
        load_genes()
        load_go_terms()
        load_annotations()
        verify_data()
        
        print("\n" + "="*60)
        print("🎉 Data Loading Complete!")
        print("="*60)
        print("\nNext steps:")
        print("  1. Test API: http://localhost:8000/docs")
        print("  2. Check stats: curl http://localhost:8000/stats")
        print("  3. View genes: curl http://localhost:8000/genes")
        
    except Exception as e:
        print(f"\n❌ Error during data loading: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
