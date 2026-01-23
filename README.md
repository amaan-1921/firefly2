# firefly2
Testing

to host FastAPI app and test alerts endpoints, 
activate virtual environment, install from requirements file, cd into /backend directory,

run ``` python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 ```


## API Endpoints

### Documentation
- **Swagger UI**  
  http://localhost:8000/docs

- **ReDoc**  
  http://localhost:8000/redoc

---

### Alert Pipelines
- **Run mock pipeline**  
  GET http://localhost:8000/alerts/run-mock

- **Run JSONL pipeline**  
  GET http://localhost:8000/alerts/run-from-jsonl

---

### News Intelligence
- **Get articles**  
  GET http://localhost:8000/monitoring/news-intelligence/articles

- **Get article count**  
  GET http://localhost:8000/monitoring/news-intelligence/articles/count

---

### System
- **Health check**  
  GET http://localhost:8000/health

- **Root info**  
  GET http://localhost:8000/

---

## Data Flow

```
agent.py (run manually/scheduled)
  ↓
Scrapes news, generates articles
  ↓
Writes to scraped_articles.jsonl
  ↓
FastAPI server (always running)
  ↓
Reads scraped_articles.jsonl on each request
  ↓
Exposes data via /monitoring/news-intelligence/articles endpoint
```
