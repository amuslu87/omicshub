🧬 **OmicsHub: A Scalable, Ontology-Aware Genomics Data Infrastructure Platform**

OmicsHub is a computational infrastructure project designed to demonstrate end-to-end data engineering capabilities for genomics and biological research. The repository focuses on building production-oriented pipelines that integrate biological ontologies, public genomics resources, and modern backend technologies.

This project is intended for mid to senior-level bioinformaticians, computational biologists, and data infrastructure scientists interested in scalable, reproducible genomics platforms.

 🎯 **Project Overview**

The primary goals of OmicsHub are to:
* Design a normalized relational data model for genomic entities
* Integrate biological ontologies into downstream data workflows
* Implement reproducible ETL pipelines for public genomics data
* Expose structured biological data through programmatic interfaces
* Demonstrate containerized, cloud-ready execution patterns

 ✨ **Current Capabilities**

OmicsHub currently demonstrates the following competencies:
* Biological data modeling with ontology-aware schema design
* ETL pipeline development for gene metadata ingestion
* Programmatic access to public genomics resources
* Relational database design and validation
* Backend-ready architecture suitable for API and analytics layers

 🎉 **Current Features**

* Integration with the NCBI Entrez API for gene metadata retrieval
* PostgreSQL database with a normalized gene schema
* Automated ingestion and validation of curated gene sets
* Verified database connectivity using Python-based clients
* Modular project structure designed for extension
 
 🗄️ **Database Schema**

*Genes Table*:
| Column Name | Type      | Description                 |
| ----------- | --------- | --------------------------- |
| gene_id     | INTEGER   | Primary key                 |
| symbol      | VARCHAR   | Official gene symbol        |
| description | TEXT      | Functional gene description |
| chromosome  | VARCHAR   | Chromosomal location        |
| gene_type   | VARCHAR   | Gene classification         |
| fetch_date  | TIMESTAMP | Data retrieval timestamp    |


📊 **Sample Data**

The following genes are currently ingested and validated within the database: BRCA1, BRCA2, TP53, PTEN, KRAS, EGFR, NRAS, BRAF, PIK3CA, MAPK1

These genes were selected to support downstream use cases such as oncology-focused analytics, pathway annotation, and ontology-driven querying.

 🛠️ **Technology Stack**

Programming Language: Python 3.13.2
Database: PostgreSQL 16
Key Libraries: 
  - Biopython 1.83
  - pandas 2.3.3
  - psycopg2-binary 2.9.11
  - fastapi 0.128.0

🛠️ **Repository Structure**
omicshub/
 
  ├── scripts/              # ETL and data ingestion scripts
  ├── database/             # Schema definitions and migrations
  ├── api/                  # API layer (in progress)
  ├── requirements.txt      # Python dependencies
  └── README.md

 🚀 **Quick Start**
*Clone the repository and set up the local environment:*

   git clone git@github.com:amuslu87/omicshub.git
   cd omicshub

   python3 -m venv venv
   source venv/bin/activate

   pip install -r requirements.txt

**Run the gene ingestion pipeline**:

 * python scripts/fetch_genes_simple.py
 * python scripts/add_sample_go_annotations.py
 * python scripts/fetch_ontology.py
 * python scripts/link_genes_to_go.py

  
  

