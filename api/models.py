"""
Pydantic models for API request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Gene(BaseModel):
    """Gene model"""
    gene_id: int
    symbol: str
    description: Optional[str] = None
    chromosome: Optional[str] = None
    gene_type: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "gene_id": 672,
                "symbol": "BRCA1",
                "description": "BRCA1 DNA repair associated",
                "chromosome": "17",
                "gene_type": "protein-coding"
            }
        }

class GOTerm(BaseModel):
    """Gene Ontology term model"""
    go_id: str
    term_name: str
    namespace: Optional[str] = None
    definition: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "go_id": "GO:0006281",
                "term_name": "DNA repair",
                "namespace": "biological_process",
                "definition": "The process of restoring DNA..."
            }
        }

class GeneAnnotation(BaseModel):
    """Gene-GO annotation model"""
    go_id: str
    term_name: str
    evidence_code: Optional[str] = None
    namespace: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "go_id": "GO:0006281",
                "term_name": "DNA repair",
                "evidence_code": "IDA",
                "namespace": "biological_process"
            }
        }

class GeneWithFunctions(BaseModel):
    """Gene with its functional annotations"""
    gene: Gene
    functions: List[GeneAnnotation]
    annotation_count: int

class DatabaseStats(BaseModel):
    """Database statistics"""
    total_genes: int
    total_go_terms: int
    total_annotations: int
    genes_with_annotations: int
