"""
OmicsHub - Simple Gene Fetcher (using esummary)
"""

from Bio import Entrez
import pandas as pd
import psycopg2
from datetime import datetime
import os


Entrez.email = "amuslu@nmu.edu"  # ← CHANGE THIS

DB_CONFIG = {
    'host': 'localhost',
    'database': 'omicshub',
    'user': 'postgres',
    'password': '7856'
}

def fetch_gene_info_simple(gene_ids):
    """Fetch using esummary (simpler)"""
    print(f"🔍 Fetching information for {len(gene_ids)} genes...")

    genes_data = []

    for gene_id in gene_ids:
        try:
            handle = Entrez.esummary(db="gene", id=str(gene_id))
            record = Entrez.read(handle)
            handle.close()

            if record['DocumentSummarySet']['DocumentSummary']:
                summary = record['DocumentSummarySet']['DocumentSummary'][0]

                gene_data = {
                    'gene_id': int(gene_id),
                    'symbol': summary.get('Name', 'Unknown'),
                    'description': summary.get('Description', ''),
                    'chromosome': summary.get('Chromosome', None),
                    'gene_type': summary.get('GeneType', 'unknown'),
                    'fetch_date': datetime.now()
                }

                genes_data.append(gene_data)
                print(f"  ✓ {gene_data['symbol']}")

        except Exception as e:
            print(f"  ✗ Error fetching gene {gene_id}: {e}")
            continue

    return pd.DataFrame(genes_data)

def create_genes_table(conn):
    """Create genes table"""
    cursor = conn.cursor()

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS genes (
        gene_id INTEGER PRIMARY KEY,
        symbol VARCHAR(50) NOT NULL,
        description TEXT,
        chromosome VARCHAR(10),
        gene_type VARCHAR(50),
        fetch_date TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_genes_symbol ON genes(symbol);
    """

    cursor.execute(create_table_sql)
    conn.commit()
    cursor.close()
    print("✅ Table 'genes' created")

def load_to_database(df):
    """Load to database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("🔌 Connected to database")

        create_genes_table(conn)

        cursor = conn.cursor()

        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO genes (gene_id, symbol, description, chromosome, gene_type, fetch_date)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (gene_id) DO UPDATE SET
                    symbol = EXCLUDED.symbol,
                    description = EXCLUDED.description;
            """, (row['gene_id'], row['symbol'], row['description'], 
                  row['chromosome'], row['gene_type'], row['fetch_date']))

        conn.commit()
        cursor.close()
        conn.close()

        print(f"✅ Loaded {len(df)} genes to database")

    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("=" * 60)
    print("🧬 OmicsHub Gene Fetcher (Simple)")
    print("=" * 60)

    gene_ids = [672, 675, 7157, 5728, 3845, 1956, 4893, 673, 5290, 5594]

    df = fetch_gene_info_simple(gene_ids)

    if not df.empty:
        print("\n" + "=" * 60)
        print(df[['gene_id', 'symbol', 'chromosome']].to_string(index=False))
        print("=" * 60)

        load_to_database(df)

        print("\n🎉 Success!")

if __name__ == "__main__":
    main()
