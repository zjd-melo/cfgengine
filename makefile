.PHONY: build install uninstall install_editable publish_testpypi publish_pypi clean help

PACKAGE_NAME := cfgengine

help:
	@echo "Available targets:"
	@echo "  build              - Build the Python package"
	@echo "  clean              - Uninstall the package and clean up build files"
	@echo "  install            - Install the package locally"
	@echo "  install_editable   - Install the package in editable mode (development)"
	@echo "  uninstall          - Uninstall the package"
	@echo "  publish       - Upload the package to private PyPI"
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

install_editable:
	@echo "Installing $(PACKAGE_NAME) in editable mode..."
	@pip install -e . || { echo "Editable install failed. Ensure 'pip' is installed and available."; exit 1; }

uninstall:
	@echo "Uninstalling $(PACKAGE_NAME)..."
	@pip uninstall -y $(PACKAGE_NAME) || { echo "Uninstall failed. Ensure 'pip' is installed and available."; exit 1; }

publish:
	@echo "Uploading $(PACKAGE_NAME) to TestPyPI..."
	@if [ ! -d "dist" ]; then \
		echo "Error: 'dist' directory not found. Run 'make build' first."; \
		exit 1; \
	fi
	@twine upload --verbose --repository private dist/* || { echo "Upload failed. Ensure 'twine' is installed: pip install twine"; exit 1; }
