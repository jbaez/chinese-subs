start_venv:
	python3 -m venv subs-venv && source subs-venv/bin/activate
install:
	pip install -r requirements.txt
install-dev:
	pip install -r requirements.txt && pip install -r dev-requirements.txt
test:
	python -m pytest
tdd:
	python -m pytest_watch
run:
	python3 src/main.py