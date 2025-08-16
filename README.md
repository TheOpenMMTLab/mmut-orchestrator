

prefect server start

=> localhost:4200

uvicorn api:app --host 0.0.0.0 --port 8002 --reload

=> localhost:8002


python run_transformations.py 574ae00d-db14-4e46-82db-c143aa8c1a0f

#Tests
```
python -m pytest tests/
```

