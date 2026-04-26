# Contributing to pykiwoomapi

We welcome contributions! Please follow these guidelines.

## Development Setup

```bash
git clone https://github.com/warvirus/pykiwoomapi.git
cd pykiwoomapi
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest
```

## Code Style

We use `ruff` for linting:

```bash
ruff check src/pykiwoomapi/
```

## Pull Requests

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request