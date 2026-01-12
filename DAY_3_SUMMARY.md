**Production-ready REST API** serving ontology-annotated genomic data

## How to Run
```bash
cd ~/omicshub
source venv/bin/activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Access documentation: http://localhost:8000/docs

## API Endpoints Summary
- `/genes` - Browse genes
- `/genes/BRCA1` - Gene details  
- `/genes/BRCA1/functions` - Biological functions
- `/go/search?keyword=DNA` - Search ontology
- `/analysis/pathway?genes=BRCA1,BRCA2` - Shared pathways
- `/stats` - Database stats

## Current Data Served
- 10 cancer genes
- 1,014 GO terms
- 29 functional annotations

## Next: Day 4 - Docker Containerization
