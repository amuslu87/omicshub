"""
OmicsHub - Gene Ontology Loader
Downloads and loads GO terms into PostgreSQL
"""

from pronto import Ontology
import pandas as pd
import psycopg2
from datetime import datetime
import os

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'database': 'omicshub',
    'user': 'postgres',
    'password': 'xxxxxxx'
}

def download_gene_ontology():
    """Download and parse Gene Ontology"""
    print("=" * 60)
    print("🧬 Downloading Gene Ontology...")
    print("=" * 60)

    # Download GO (takes 1-2 minutes first time, then cached)
    go_url = "http://purl.obolibrary.org/obo/go/go-basic.obo"

    try:
        go = Ontology(go_url)
        print(f"✅ Loaded {len(go)} GO terms")
        return go
    except Exception as e:
        print(f"❌ Error loading GO: {e}")
        return None

def explore_ontology(go):
    """Explore GO structure"""
    print("\n" + "=" * 60)
    print("📊 Gene Ontology Statistics")
    print("=" * 60)

    # Count by namespace
    namespaces = {}
    for term in go.terms():
        ns = term.namespace
        if ns:
            namespaces[ns] = namespaces.get(ns, 0) + 1

    for ns, count in namespaces.items():
        print(f"  {ns}: {count:,} terms")

    print("\n" + "=" * 60)
    print("🔍 Example: Biological Process Root")
    print("=" * 60)

    # Get biological process root
    bp_root = go["GO:0008150"]  # biological_process
    print(f"Term: {bp_root.id}")
    print(f"Name: {bp_root.name}")
    print(f"Definition: {bp_root.definition[:100]}...")

    # Show some children
    print(f"\nFirst 5 direct children:")
    children = list(bp_root.subclasses(distance=1))[:5]
    for child in children:
        if child.id != bp_root.id:  # Skip self
            print(f"  - {child.id}: {child.name}")

def search_go_terms(go, keyword):
    """Search for GO terms containing keyword"""
    print("\n" + "=" * 60)
    print(f"🔎 Searching for: '{keyword}'")
    print("=" * 60)

    matches = []
    for term in go.terms():
        if keyword.lower() in term.name.lower():
            matches.append({
                'go_id': term.id,
                'name': term.name,
                'namespace': term.namespace,
                'definition': term.definition
            })

    df = pd.DataFrame(matches)
    print(f"Found {len(df)} matching terms\n")

    if len(df) > 0:
        print(df[['go_id', 'name', 'namespace']].head(10).to_string(index=False))

    return df

def extract_go_terms_to_db(go):
    """Extract GO terms and save to database"""
    print("\n" + "=" * 60)
    print("💾 Extracting GO Terms for Database")
    print("=" * 60)

    go_terms = []

    # Limit to first 1000 terms for now (full GO is ~45,000 terms)
    count = 0
    for term in go.terms():
        if count >= 1000:
            break

        go_terms.append({
            'go_id': term.id,
            'term_name': term.name,
            'namespace': term.namespace,
            'definition': str(term.definition) if term.definition else '',
            'is_obsolete': term.obsolete
        })
        count += 1

        if count % 200 == 0:
            print(f"  Processed {count} terms...")

    df = pd.DataFrame(go_terms)
    print(f"✅ Extracted {len(df)} GO terms")

    return df

def create_go_tables(conn):
    """Create Gene Ontology tables in PostgreSQL"""
    cursor = conn.cursor()

    print("\n" + "=" * 60)
    print("🗄️  Creating GO Tables")
    print("=" * 60)

    # GO Terms table
    create_table_sql = """
    -- GO Terms table
    CREATE TABLE IF NOT EXISTS go_terms (
        go_id VARCHAR(10) PRIMARY KEY,
        term_name VARCHAR(255) NOT NULL,
        namespace VARCHAR(50),
        definition TEXT,
        is_obsolete BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Gene-GO Annotations table
    CREATE TABLE IF NOT EXISTS gene_go_annotations (
        annotation_id SERIAL PRIMARY KEY,
        gene_id INTEGER REFERENCES genes(gene_id),
        go_id VARCHAR(10) REFERENCES go_terms(go_id),
        evidence_code VARCHAR(10),
        source VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(gene_id, go_id)
    );

    -- Indexes for performance
    CREATE INDEX IF NOT EXISTS idx_go_namespace ON go_terms(namespace);
    CREATE INDEX IF NOT EXISTS idx_go_name ON go_terms(term_name);
    CREATE INDEX IF NOT EXISTS idx_gene_go_gene ON gene_go_annotations(gene_id);
    CREATE INDEX IF NOT EXISTS idx_gene_go_term ON gene_go_annotations(go_id);
    """

    cursor.execute(create_table_sql)
    conn.commit()
    cursor.close()

    print("✅ Tables created:")
    print("   - go_terms")
    print("   - gene_go_annotations")

def load_go_terms_to_db(df):
    """Load GO terms to PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("\n🔌 Connected to database")

        # Create tables
        create_go_tables(conn)

        # Insert GO terms
        cursor = conn.cursor()

        print("\n💾 Loading GO terms to database...")

        insert_sql = """
        INSERT INTO go_terms (go_id, term_name, namespace, definition, is_obsolete)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (go_id) DO UPDATE SET
            term_name = EXCLUDED.term_name,
            definition = EXCLUDED.definition;
        """

        for idx, row in df.iterrows():
            cursor.execute(insert_sql, (
                row['go_id'],
                row['term_name'],
                row['namespace'],
                row['definition'],
                row['is_obsolete']
            ))

            if (idx + 1) % 200 == 0:
                print(f"  Loaded {idx + 1} terms...")

        conn.commit()
        cursor.close()
        conn.close()

        print(f"✅ Loaded {len(df)} GO terms to database")

    except Exception as e:
        print(f"❌ Database error: {e}")

def main():
    """Main execution"""
    print("=" * 60)
    print("🧬 OmicsHub - Gene Ontology Integration")
    print("=" * 60)

    # Download and parse GO
    go = download_gene_ontology()
    if not go:
        return

    # Explore ontology structure
    explore_ontology(go)

    # Search examples
    search_go_terms(go, "immune")
    search_go_terms(go, "cancer")

    # Extract and load to database
    df_go = extract_go_terms_to_db(go)

    # Load to database
    load_go_terms_to_db(df_go)

    print("\n" + "=" * 60)
    print("🎉 Gene Ontology Integration Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Link genes to GO terms")
    print("  2. Query ontology-annotated data")
    print("  3. Build ontology-driven analysis")

if __name__ == "__main__":
    main()
