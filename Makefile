PYTHON ?= python3

.PHONY: help install-dev test

help:
	@echo "install-dev: instalar dependências na venv ativa"
	@echo "test: executar pytest (a nova estrutura ainda não contém testes)"

install-dev:
	$(PYTHON) -m pip install -r requirements.txt 'pytest>=8.3,<10'

test:
	$(PYTHON) -m pytest
