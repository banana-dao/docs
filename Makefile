.PHONY: build serve

build:
	@if [ ! -d "venv" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv venv; \
	fi
	@echo "Updating dependencies..."
	@. venv/bin/activate && pip uninstall mkdocs-bootstrap386 -y > /dev/null 2>&1  && \
		pip install ./pkg/mkdocs-bootstrap386 mkdocs > /dev/null 2>&1

serve:
	@echo "Serving documentation..."
	@. venv/bin/activate && mkdocs serve -a 0.0.0.0:8000
