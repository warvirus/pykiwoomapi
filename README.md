# pykiwoomapi

Python wrapper for **Kiwoom Open API+** (Korea Stock Market).

## Installation

```bash
pip install pykiwoomapi
```

## Development

This project uses [uv](https://docs.astral.sh/uv/). The pinned Python version is in `.python-version` (3.12), and dependencies are locked in `uv.lock`.

```bash
uv sync --managed-python        # create .venv and install runtime + dev dependencies
uv run pytest                   # run tests
uv run ruff check src/pykiwoomapi/
uv run mypy src/pykiwoomapi/
uv build                        # build sdist and wheel
```

Development tools live in `[dependency-groups].dev` in `pyproject.toml`. The package itself supports Python 3.9 and above.

## Quick Start

```python
from pykiwoomapi import Auth, KiwoomClient

# Create auth object (mock=True for demo account)
auth = Auth(mock=True)
auth.login("YOUR_APP_KEY", "YOUR_SECRET_KEY")

# Create API client
client = KiwoomClient(auth)

# Request stock basic info (Samsung Electronics)
result = client.read("주식기본정보요청", stk_cd="005930")
print(result)
```

## Features

- **180+ API endpoints** covering Korean stock market data
- **REST API** - Query stock info, account, rankings, charts, themes, ETFs, ELWs
- **WebSocket** - Real-time market data streaming
- **Account** - Balance, profit/loss, orders (buy/sell/modify/cancel)
- **Mock mode** - Test with demo account without real trading

## Environment

| Environment | Base URL |
|-------------|----------|
| Mock (Demo) | `https://mockapi.kiwoom.com` |
| Production | `https://api.kiwoom.com` |
| Rest API | `https://openapi.kiwoom.com/guide/apiguide` |

## License

MIT License