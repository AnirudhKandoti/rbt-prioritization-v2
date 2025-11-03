run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
init:
	python -m app.database --init
load-sample:
	python scripts/load_sample.py
load-incidents:
	python scripts/load_incidents.py
test:
	pytest -q
