"""
OmicsHub REST API
Serves ontology-annotated genomic data
"""

from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from api.database import get_db_connection, test_connection
from api.models import Gene, GOTerm, GeneAnnotation, GeneWithFunctions, DatabaseStats

# Create FastAPI app
app = FastAPI(
    title="OmicsHub API",
    description="REST API for ontology-annotated genomic data",
    version="1.0.0",
    contact={
        "name": "OmicsHub Project",
        "url": "https://github.com/amuslu87/omicshub"
    }
)

@app.get("/")
def root():
    """API information and available endpoints"""
    return {
        "message": "Welcome to OmicsHub API",
        "version": "1.0.0",
        "endpoints": {
            "genes": "/genes",
            "gene_detail": "/genes/{symbol}",
            "gene_functions": "/genes/{symbol}/functions",
            "go_terms": "/go/terms",
            "go_search": "/go/search?keyword={keyword}",
            "analysis": "/analysis/pathway",
            "stats": "/stats",
            "health": "/health"
        },
        "documentation": "/docs"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    db_status = test_connection()
    return {
        "status": "healthy",
        "database": db_status
    }

@app.get("/genes", response_model=List[Gene])
def get_genes(limit: int = Query(10, le=100)):
    """
    Get list of genes
    
    - **limit**: Maximum number of genes to return (default: 10, max: 100)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT gene_id, symbol, description, chromosome, gene_type
                FROM genes
                ORDER BY symbol
                LIMIT %s
            """, (limit,))
            genes = cursor.fetchall()
            return genes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/genes/{symbol}", response_model=Gene)
def get_gene(symbol: str):
    """
    Get specific gene by symbol
    
    - **symbol**: Gene symbol (e.g., BRCA1, TP53)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT gene_id, symbol, description, chromosome, gene_type
                FROM genes
                WHERE UPPER(symbol) = UPPER(%s)
            """, (symbol,))
            gene = cursor.fetchone()
            
            if not gene:
                raise HTTPException(status_code=404, detail=f"Gene '{symbol}' not found")
            
            return gene
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/genes/{symbol}/functions", response_model=List[GeneAnnotation])
def get_gene_functions(symbol: str):
    """
    Get functional annotations (GO terms) for a gene
    
    - **symbol**: Gene symbol (e.g., BRCA1, TP53)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # First check if gene exists
            cursor.execute("SELECT gene_id FROM genes WHERE UPPER(symbol) = UPPER(%s)", (symbol,))
            gene = cursor.fetchone()
            
            if not gene:
                raise HTTPException(status_code=404, detail=f"Gene '{symbol}' not found")
            
            # Get annotations
            cursor.execute("""
                SELECT 
                    gt.go_id,
                    gt.term_name,
                    gt.namespace,
                    gga.evidence_code
                FROM gene_go_annotations gga
                JOIN go_terms gt ON gga.go_id = gt.go_id
                WHERE gga.gene_id = %s
                ORDER BY gt.term_name
            """, (gene['gene_id'],))
            
            annotations = cursor.fetchall()
            
            if not annotations:
                return []
            
            return annotations
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/go/terms", response_model=List[GOTerm])
def get_go_terms(
    namespace: Optional[str] = Query(None, description="GO namespace: biological_process, molecular_function, or cellular_component"),
    limit: int = Query(20, le=100)
):
    """
    Get GO terms, optionally filtered by namespace
    
    - **namespace**: Filter by GO namespace (optional)
    - **limit**: Maximum number of terms to return
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if namespace:
                cursor.execute("""
                    SELECT go_id, term_name, namespace, definition
                    FROM go_terms
                    WHERE namespace = %s
                    ORDER BY term_name
                    LIMIT %s
                """, (namespace, limit))
            else:
                cursor.execute("""
                    SELECT go_id, term_name, namespace, definition
                    FROM go_terms
                    ORDER BY term_name
                    LIMIT %s
                """, (limit,))
            
            terms = cursor.fetchall()
            return terms
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/go/search", response_model=List[GOTerm])
def search_go_terms(keyword: str = Query(..., min_length=3)):
    """
    Search GO terms by keyword
    
    - **keyword**: Search term (minimum 3 characters)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT go_id, term_name, namespace, definition
                FROM go_terms
                WHERE LOWER(term_name) LIKE LOWER(%s)
                ORDER BY term_name
                LIMIT 50
            """, (f"%{keyword}%",))
            
            terms = cursor.fetchall()
            return terms
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analysis/pathway")
def analyze_pathway(genes: str = Query(..., description="Comma-separated gene symbols")):
    """
    Find shared biological pathways for a set of genes
    
    - **genes**: Comma-separated gene symbols (e.g., "BRCA1,BRCA2,TP53")
    """
    try:
        gene_list = [g.strip().upper() for g in genes.split(',')]
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Find shared GO terms
            cursor.execute("""
                SELECT 
                    gt.go_id,
                    gt.term_name,
                    gt.namespace,
                    COUNT(DISTINCT g.symbol) as gene_count,
                    STRING_AGG(DISTINCT g.symbol, ', ' ORDER BY g.symbol) as genes
                FROM genes g
                JOIN gene_go_annotations gga ON g.gene_id = gga.gene_id
                JOIN go_terms gt ON gga.go_id = gt.go_id
                WHERE UPPER(g.symbol) = ANY(%s)
                GROUP BY gt.go_id, gt.term_name, gt.namespace
                HAVING COUNT(DISTINCT g.symbol) >= 2
                ORDER BY gene_count DESC, gt.term_name
            """, (gene_list,))
            
            pathways = cursor.fetchall()
            
            return {
                "input_genes": gene_list,
                "shared_pathways": pathways,
                "pathway_count": len(pathways)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats", response_model=DatabaseStats)
def get_stats():
    """Get database statistics"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM genes) as total_genes,
                    (SELECT COUNT(*) FROM go_terms) as total_go_terms,
                    (SELECT COUNT(*) FROM gene_go_annotations) as total_annotations,
                    (SELECT COUNT(DISTINCT gene_id) FROM gene_go_annotations) as genes_with_annotations
            """)
            
            stats = cursor.fetchone()
            return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
