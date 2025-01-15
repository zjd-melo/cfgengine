.PHONY: build install uninstall publish_testpypi publish_pypi clean help

PACKAGE_NAME := cfgengine

help:
	@echo "Available targets:"
	@echo "  build              - Build the Python package"
	@echo "  clean              - Uninstall the package and clean up build files"
	@echo "  install            - Install the package locally"
	@echo "  uninstall          - Uninstall the package"
	@echo "  publish_testpypi   - Upload the package to TestPyPI"
	@echo "  publish_pypi       - Upload the package to PyPI"
	@echo "  help               - Display this help message"

build:
	@echo "Building $(PACKAGE_NAME)..."
	@python -m build || { echo "Build failed. Ensure 'build' module is installed: pip install build"; exit 1; }

clean: uninstall
	@echo "Cleaning up..."
	@rm -rf $(PACKAGE_NAME).egg-info dist build
	@echo "Cleanup complete."

install:
	@echo "Installing $(PACKAGE_NAME)..."
	@pip install . || { echo "Install failed. Ensure 'pip' is installed and available."; exit 1; }

uninstall:
	@echo "Uninstalling $(PACKAGE_NAME)..."
	@pip uninstall -y $(PACKAGE_NAME) || { echo "Uninstall failed. Ensure 'pip' is installed and available."; exit 1; }

publish_testpypi:
	@echo "Uploading $(PACKAGE_NAME) to TestPyPI..."
	@if [ ! -d "dist" ]; then \
		echo "Error: 'dist' directory not found. Run 'make build' first."; \
		exit 1; \
	fi
	@twine upload --verbose --repository testpypi dist/* || { echo "Upload failed. Ensure 'twine' is installed: pip install twine"; exit 1; }

publish_pypi:
	@echo "Uploading $(PACKAGE_NAME) to PyPI..."
	@if [ ! -d "dist" ]; then \
		echo "Error: 'dist' directory not found. Run 'make build' first."; \
		exit 1; \
	fi
	@twine upload --verbose --repository pypi dist/* || { echo "Upload failed. Ensure 'twine' is installed: pip install twine"; exit 1; }
