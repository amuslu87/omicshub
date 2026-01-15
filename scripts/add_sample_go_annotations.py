
import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'database': 'omicshub',
    'user': 'postgres',
    'password': 'xxxxx'
}

# Curated GO annotations for cancer genes
# Format: (gene_symbol, go_id, go_term, evidence_code)
CANCER_GENE_ANNOTATIONS = [
    # BRCA1 - DNA repair and tumor suppression
    ('BRCA1', 'GO:0006281', 'DNA repair', 'IEA'),
    ('BRCA1', 'GO:0006974', 'cellular response to DNA damage stimulus', 'IEA'),
    ('BRCA1', 'GO:0051276', 'chromosome organization', 'IEA'),
    ('BRCA1', 'GO:0006302', 'double-strand break repair', 'IDA'),
    ('BRCA1', 'GO:0042127', 'regulation of cell population proliferation', 'IEA'),
    
    # BRCA2 - DNA repair
    ('BRCA2', 'GO:0006281', 'DNA repair', 'IEA'),
    ('BRCA2', 'GO:0006302', 'double-strand break repair', 'IDA'),
    ('BRCA2', 'GO:0000724', 'double-strand break repair via homologous recombination', 'IMP'),
    
    # TP53 - Tumor suppressor
    ('TP53', 'GO:0006915', 'apoptotic process', 'IDA'),
    ('TP53', 'GO:0042981', 'regulation of apoptotic process', 'IDA'),
    ('TP53', 'GO:0006974', 'cellular response to DNA damage stimulus', 'IDA'),
    ('TP53', 'GO:0051276', 'chromosome organization', 'IEA'),
    ('TP53', 'GO:0042127', 'regulation of cell population proliferation', 'IDA'),
    
    # PTEN - Tumor suppressor
    ('PTEN', 'GO:0008285', 'negative regulation of cell population proliferation', 'IDA'),
    ('PTEN', 'GO:0006915', 'apoptotic process', 'IEA'),
    ('PTEN', 'GO:0016055', 'Wnt signaling pathway', 'IEA'),
    
    # KRAS - Oncogene
    ('KRAS', 'GO:0007165', 'signal transduction', 'IEA'),
    ('KRAS', 'GO:0007049', 'cell cycle', 'IEA'),
    ('KRAS', 'GO:0008283', 'cell population proliferation', 'IEA'),
    ('KRAS', 'GO:0006915', 'apoptotic process', 'IEA'),
    
    # EGFR - Growth factor receptor
    ('EGFR', 'GO:0007165', 'signal transduction', 'IDA'),
    ('EGFR', 'GO:0008283', 'cell population proliferation', 'IDA'),
    ('EGFR', 'GO:0007173', 'epidermal growth factor receptor signaling pathway', 'IDA'),
    
    # BRAF - Kinase
    ('BRAF', 'GO:0000165', 'MAPK cascade', 'IDA'),
    ('BRAF', 'GO:0007165', 'signal transduction', 'IEA'),
    ('BRAF', 'GO:0008283', 'cell population proliferation', 'IEA'),
    
    # PIK3CA - Kinase
    ('PIK3CA', 'GO:0007165', 'signal transduction', 'IEA'),
    ('PIK3CA', 'GO:0008283', 'cell population proliferation', 'IEA'),
    ('PIK3CA', 'GO:0016055', 'Wnt signaling pathway', 'IEA'),
]

def ensure_go_terms_exist():
    """Make sure the GO terms we're using exist in go_terms table"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("📋 Ensuring GO Terms Exist")
    print("=" * 60)
    
    # Get unique GO terms from annotations
    go_terms_needed = {}
    for _, go_id, go_term, _ in CANCER_GENE_ANNOTATIONS:
        go_terms_needed[go_id] = go_term
    
    # Insert GO terms if they don't exist
    insert_sql = """
    INSERT INTO go_terms (go_id, term_name, namespace)
    VALUES (%s, %s, 'biological_process')
    ON CONFLICT (go_id) DO NOTHING;
    """
    
    added = 0
    for go_id, go_term in go_terms_needed.items():
        cursor.execute(insert_sql, (go_id, go_term))
        if cursor.rowcount > 0:
            added += 1
    
    conn.commit()
    print(f"✅ Ensured {len(go_terms_needed)} GO terms exist ({added} newly added)")
    
    cursor.close()
    conn.close()

def add_gene_annotations():
    """Add gene GO annotations"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("\n" + "=" * 60)
    print("🔗 Adding Gene-GO Annotations")
    print("=" * 60)
    
    # Get gene ID mapping
    cursor.execute("SELECT gene_id, symbol FROM genes")
    gene_map = {row[1]: row[0] for row in cursor.fetchall()}
    
    insert_sql = """
    INSERT INTO gene_go_annotations (gene_id, go_id, evidence_code, source)
    VALUES (%s, %s, %s, 'Manual curation')
    ON CONFLICT (gene_id, go_id) DO NOTHING;
    """
    
    added = 0
    for gene_symbol, go_id, go_term, evidence in CANCER_GENE_ANNOTATIONS:
        if gene_symbol in gene_map:
            gene_id = gene_map[gene_symbol]
            cursor.execute(insert_sql, (gene_id, go_id, evidence))
            if cursor.rowcount > 0:
                added += 1
                print(f"  ✓ {gene_symbol} → {go_id}: {go_term}")
    
    conn.commit()
    print(f"\n✅ Added {added} gene-GO annotations")
    
    cursor.close()
    conn.close()

def display_annotations_summary():
    """Display summary of annotations"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("\n" + "=" * 60)
    print("📊 Annotation Summary")
    print("=" * 60)
    
    # Count per gene
    query = """
    SELECT g.symbol, COUNT(gga.annotation_id) as count
    FROM genes g
    LEFT JOIN gene_go_annotations gga ON g.gene_id = gga.gene_id
    GROUP BY g.symbol
    ORDER BY count DESC;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print("\nAnnotations per gene:")
    for gene, count in results:
        bar = "█" * count
        print(f"  {gene:8s} {count:2d} {bar}")
    
    # Show BRCA1 annotations as example
    print("\n" + "=" * 60)
    print("🔬 Example: BRCA1 Functional Annotations")
    print("=" * 60)
    
    query = """
    SELECT gt.go_id, gt.term_name, gga.evidence_code
    FROM gene_go_annotations gga
    JOIN genes g ON gga.gene_id = g.gene_id
    JOIN go_terms gt ON gga.go_id = gt.go_id
    WHERE g.symbol = 'BRCA1'
    ORDER BY gt.term_name;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    for go_id, term, evidence in results:
        print(f"  {go_id}: {term} [{evidence}]")
    
    cursor.close()
    conn.close()

def demonstrate_ontology_query():
    """Demonstrate ontology-driven query"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    print("\n" + "=" * 60)
    print("🎯 Ontology-Driven Query Example")
    print("=" * 60)
    print("Question: Which genes are involved in DNA repair?")
    print("=" * 60)
    
    query = """
    SELECT DISTINCT g.symbol, g.chromosome, gt.term_name
    FROM genes g
    JOIN gene_go_annotations gga ON g.gene_id = gga.gene_id
    JOIN go_terms gt ON gga.go_id = gt.go_id
    WHERE gt.term_name LIKE '%DNA repair%'
    ORDER BY g.symbol;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    if results:
        print("\nGenes involved in DNA repair:")
        for symbol, chrom, term in results:
            print(f"  • {symbol} (chr{chrom}): {term}")
    
    cursor.close()
    conn.close()

def main():
    """Main execution"""
    print("=" * 60)
    print("🧬 OmicsHub - Sample GO Annotation Loader")
    print("=" * 60)
    
    # Ensure GO terms exist
    ensure_go_terms_exist()
    
    # Add annotations
    add_gene_annotations()
    
    # Display summary
    display_annotations_summary()
    
    # Demonstrate ontology query
    demonstrate_ontology_query()
    
    print("\n" + "=" * 60)
    print("🎉 Ontology Integration Complete!")
    print("=" * 60)
    print("\n✨ You now have ontology-annotated genomic data!")
    print("   This demonstrates:")
    print("   - Ontology-driven data modeling")
    print("   - Semantic data integration")
    print("   - Knowledge-based queries")

if __name__ == "__main__":
    main()
