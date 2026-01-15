"""
OmicsHub - Link Genes to GO Terms
Download GO annotations and link genes to GO terms
"""

import pandas as pd
import psycopg2
import requests
import gzip
from io import StringIO

DB_CONFIG = {
    'host': 'localhost',
    'database': 'omicshub',
    'user': 'postgres',
    'password': 'xxxxxx'
}

def download_go_annotations():
    """Download human GO annotations from GOA"""
    print("=" * 60)
    print("📥 Downloading GO Annotations from GOA")
    print("=" * 60)
    
    # Use smaller QuickGO annotations for our genes
    # We'll query for each gene individually
    
    genes = ['BRCA1', 'BRCA2', 'TP53', 'PTEN', 'KRAS', 
             'EGFR', 'NRAS', 'BRAF', 'PIK3CA', 'MAPK1']
    
    all_annotations = []
    
    for gene in genes:
        try:
            print(f"  Fetching annotations for {gene}...")
            
            # QuickGO API
            url = f"https://www.ebi.ac.uk/QuickGO/services/annotation/search"
            params = {
                'geneProductId': f'UniProtKB:*',
                'geneProductSubset': 'Swiss-Prot',
                'taxonId': '9606',  # Human
                'goUsage': 'descendants',
                'goUsageRelationships': 'is_a,part_of,occurs_in',
                'limit': 100,
                'aspect': 'biological_process',
                'symbol': gene
            }
            
            headers = {
                'Accept': 'application/json'
            }
            
            response = requests.get(url, params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                for result in results:
                    all_annotations.append({
                        'gene_symbol': result.get('symbol', gene),
                        'go_id': result.get('goId', ''),
                        'go_term': result.get('goName', ''),
                        'evidence_code': result.get('goEvidence', ''),
                        'source': result.get('assignedBy', 'QuickGO')
                    })
                
                print(f"    ✓ Found {len(results)} annotations")
            else:
                print(f"    ✗ API error: {response.status_code}")
                
        except Exception as e:
            print(f"    ✗ Error: {e}")
            continue
    
    df = pd.DataFrame(all_annotations)
    print(f"\n✅ Total annotations retrieved: {len(df)}")
    
    return df

def load_annotations_to_db(df):
    """Load gene-GO annotations to database"""
    if df.empty:
        print("❌ No annotations to load")
        return
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("\n🔌 Connected to database")
        
        cursor = conn.cursor()
        
        # Get gene IDs mapping
        cursor.execute("SELECT gene_id, symbol FROM genes")
        gene_map = {row[1]: row[0] for row in cursor.fetchall()}
        
        print(f"📋 Found {len(gene_map)} genes in database")
        
        # Insert annotations
        print("\n💾 Loading annotations...")
        
        insert_sql = """
        INSERT INTO gene_go_annotations (gene_id, go_id, evidence_code, source)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (gene_id, go_id) DO NOTHING;
        """
        
        loaded = 0
        skipped = 0
        
        for _, row in df.iterrows():
            gene_symbol = row['gene_symbol']
            go_id = row['go_id']
            
            if gene_symbol in gene_map and go_id:
                gene_id = gene_map[gene_symbol]
                
                try:
                    cursor.execute(insert_sql, (
                        gene_id,
                        go_id,
                        row['evidence_code'],
                        row['source']
                    ))
                    loaded += 1
                except Exception as e:
                    # GO term might not be in our go_terms table
                    skipped += 1
                    continue
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Loaded {loaded} annotations")
        print(f"⚠️  Skipped {skipped} (GO terms not in database)")
        
    except Exception as e:
        print(f"❌ Database error: {e}")

def query_gene_annotations():
    """Query and display gene GO annotations"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        
        cursor = conn.cursor()
        
        # Count annotations per gene
        query = """
        SELECT g.symbol, COUNT(gga.annotation_id) as annotation_count
        FROM genes g
        LEFT JOIN gene_go_annotations gga ON g.gene_id = gga.gene_id
        GROUP BY g.symbol
        ORDER BY annotation_count DESC;
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        print("\n" + "=" * 60)
        print("📊 GO Annotations per Gene")
        print("=" * 60)
        
        for gene, count in results:
            print(f"  {gene}: {count} annotations")
        
        # Show example annotations for BRCA1
        print("\n" + "=" * 60)
        print("🔬 Example: BRCA1 GO Annotations")
        print("=" * 60)
        
        query = """
        SELECT gga.go_id, gt.term_name, gga.evidence_code
        FROM gene_go_annotations gga
        JOIN genes g ON gga.gene_id = g.gene_id
        JOIN go_terms gt ON gga.go_id = gt.go_id
        WHERE g.symbol = 'BRCA1'
        LIMIT 10;
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if results:
            for go_id, term_name, evidence in results:
                print(f"  {go_id}: {term_name[:60]}... [{evidence}]")
        else:
            print("  No annotations found (GO terms might not be loaded yet)")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main execution"""
    print("=" * 60)
    print("🧬 OmicsHub - Gene-GO Annotation Linking")
    print("=" * 60)
    
    # Download annotations
    df = download_go_annotations()
    
    if not df.empty:
        # Show sample
        print("\n" + "=" * 60)
        print("📋 Sample Annotations")
        print("=" * 60)
        print(df.head(10).to_string(index=False))
        
        # Load to database
        load_annotations_to_db(df)
        
        # Query results
        query_gene_annotations()
    
    print("\n" + "=" * 60)
    print("🎉 Gene-GO Linking Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
