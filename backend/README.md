# FastAPI Backend

## Setup
```bash
pip install -r requirements.txt
```

## Run
```bash
uvicorn app.main:app --reload
```

## Migrations
```bash
alembic upgrade head
alembic revision --autogenerate -m "description"
```
