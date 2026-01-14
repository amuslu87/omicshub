#!/usr/bin/env python3
"""
Simple gene fetcher for OmicsHub
Fetches basic gene information from NCBI
"""

import os
from Bio import Entrez
import psycopg2
from datetime import datetime

# Set your email for NCBI
Entrez.email = "your.email@example.com"

# Database configuration - uses environment variables with fallback
DB_CONFIG = {
    'host': os.getenv('DATABASE_HOST', 'localhost'),
    'database': os.getenv('DATABASE_NAME', 'omicshub'),
    'user': os.getenv('DATABASE_USER', 'postgres'),
    'password': os.getenv('DATABASE_PASSWORD', '7856'),
    'port': int(os.getenv('DATABASE_PORT', '5432'))
}

def create_genes_table(conn):
    """Create genes table if it doesn't exist"""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS genes (
            gene_id INTEGER PRIMARY KEY,
            symbol VARCHAR(50) UNIQUE NOT NULL,
            description TEXT,
            chromosome VARCHAR(10),
            gene_type VARCHAR(50),
            fetch_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    print("✅ Genes table ready")
def fetch_gene_info_simple(gene_ids):
    """Fetch using esummary (simpler)"""
    print(f"🔍 Fetching information for {len(gene_ids)} genes...")
    
    handle = Entrez.esummary(db="gene", id=",".join(map(str, gene_ids)))
    records = Entrez.read(handle)
    handle.close()
    
    genes_data = []
    for record in records['DocumentSummarySet']['DocumentSummary']:
        genes_data.append({
            'gene_id': int(record['Id']),
            'symbol': record.get('Name', 'Unknown'),
            'description': record.get('Description', ''),
            'chromosome': record.get('Chromosome', ''),
            'gene_type': record.get('GeneType', '')
        })
        print(f"  ✓ {record.get('Name', 'Unknown')}")
    
    return genes_data

def load_to_database(genes_data):
    """Load genes into PostgreSQL"""
    conn = psycopg2.connect(**DB_CONFIG)
    print("  ✅ Connected to database")
    
    create_genes_table(conn)
    
    cursor = conn.cursor()
    
    for gene in genes_data:
        cursor.execute("""
            INSERT INTO genes (gene_id, symbol, description, chromosome, gene_type, fetch_date)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (gene_id) DO UPDATE SET
                symbol = EXCLUDED.symbol,
                description = EXCLUDED.description,
                chromosome = EXCLUDED.chromosome,
                gene_type = EXCLUDED.gene_type,
                fetch_date = EXCLUDED.fetch_date
        """, (
            gene['gene_id'],
            gene['symbol'],
            gene['description'],
            gene['chromosome'],
            gene['gene_type'],
            datetime.now()
        ))
    
    conn.commit()
 # Verify
    cursor.execute("SELECT gene_id, symbol, chromosome FROM genes ORDER BY gene_id")
    results = cursor.fetchall()
    
    print("\n" + "="*60)
    print(f"  gene_id  symbol    chromosome")
    for row in results:
        print(f"  {row[0]:6d}  {row[1]:8s}  {row[2]:3s}")
    
    cursor.close()
    conn.close()
    print("="*60)

def main():
    print("="*60)
    print("🧬 OmicsHub Gene Fetcher (Simple)")
    print("="*60)
    
    # 10 important cancer genes
    gene_ids = [
        672,    # BRCA1
        675,    # BRCA2
        7157,   # TP53
        5728,   # PTEN
        3845,   # KRAS
        1956,   # EGFR
        4893,   # NRAS
        673,    # BRAF
        5290,   # PIK3CA
        5594    # MAPK1
    ]
    
    # Fetch genes
    genes_data = fetch_gene_info_simple(gene_ids)
    
    # Load to database
    load_to_database(genes_data)
    
    print("\n🎉 Success!")

if __name__ == "__main__":
    main()
