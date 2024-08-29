.PHONY: install clean build-container

CONTAINER_NAME=forward-export-api
VENV=venv
BIN=$(VENV)/bin

install: requirements.txt
	test -d $(VENV) || ( virtualenv -p python3 $(VENV) && \
	$(BIN)/pip3 install -qr requirements.txt )

run-local: venv
	source $(VENV)/bin/activate; $(BIN)/python3 -m uvicorn app.main:app --reload --port 9009

clean:
	rm -rf $(VENV)

build-container:
	@echo Building container...
	docker build -t $(CONTAINER_NAME) .
	@echo Container built!
