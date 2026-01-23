# firefly2
Testing

to host FastAPI app and test alerts endpoints, 
activate virtual environment, install from requirements file, cd into /backend directory,

run ``` python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 ```


endpoints: 


## API Endpoints

### Documentation
- **Swagger UI**  
  http://localhost:8000/docs

- **ReDoc**  
  http://localhost:8000/redoc

---

### Alert Pipelines
- **Run mock pipeline**  
  POST http://localhost:8000/alerts/run-mock

- **Run JSONL pipeline**  
  POST http://localhost:8000/alerts/run-from-jsonl

---

### System
- **Health check**  
  GET http://localhost:8000/health

- **Root info**  
  GET http://localhost:8000/
