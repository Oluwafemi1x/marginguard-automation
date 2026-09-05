.PHONY: install test run demo
install:
	pip install -r requirements.txt
	playwright install chromium

test:
	pytest -q

run:
	uvicorn app.main:app --reload

demo:
	python demo_record.py
