# intents.py

[![PyPI](https://img.shields.io/pypi/v/intents-py.svg)](https://pypi.org/project/intents-py/)
[![Python](https://img.shields.io/pypi/pyversions/intents-py.svg)](https://pypi.org/project/intents-py/)
[![Docs](https://readthedocs.org/projects/intents-py/badge/?version=latest)](https://intentspy.readthedocs.io/en/latest/)
[![License](https://img.shields.io/pypi/l/intents-py.svg)](LICENSE)

An async Python wrapper for the [NEAR Intents 1Click Swap API](https://docs.near-intents.org/integration/distribution-channels/1click-api/about-1click-api).

- **Docs:** https://intentspy.readthedocs.io
- **PyPI:** https://pypi.org/project/intents-py/

```
pip install intents-py
```

## Requirements

- Python 3.10+
- `httpx`
- `pydantic`

## Quickstart

```python
import asyncio
from intents import IntentsClient, find_token

async def main():
    async with IntentsClient() as client:
        tokens = await client.get_tokens()
        eth = find_token(tokens, "eth", "ETH")
        print(eth.asset_id)  # nep141:eth.omft.near

asyncio.run(main())
```

## Swap flow

```python
import asyncio
from datetime import datetime, timedelta, timezone
from intents import (
    IntentsClient,
    QuoteRequest,
    SwapType,
    DepositType,
    RecipientType,
    RefundType,
    SwapStatus,
    find_token,
    token_to_atomic,
)

async def main():
    async with IntentsClient(jwt_token="your-jwt-token") as client:
        tokens = await client.get_tokens()
        eth  = find_token(tokens, "eth", "ETH")
        usdc = find_token(tokens, "arb", "USDC")

        # 1. Get a quote
        response = await client.get_quote(QuoteRequest(
            dry=False,
            swap_type=SwapType.EXACT_INPUT,
            slippage_tolerance=100,          # 1% — use pct_to_bps(1) for clarity
            origin_asset=eth.asset_id,
            destination_asset=usdc.asset_id,
            deposit_type=DepositType.ORIGIN_CHAIN,
            amount=token_to_atomic("0.01", eth),
            refund_to="0xYourAddress",
            refund_type=RefundType.ORIGIN_CHAIN,
            recipient="0xYourAddress",
            recipient_type=RecipientType.DESTINATION_CHAIN,
            deadline=datetime.now(timezone.utc) + timedelta(hours=1),
        ))

        quote = response.quote
        print(f"Send {quote.amount_in_formatted} ETH to {quote.deposit_address}")
        if quote.deposit_memo:
            print(f"Memo (required): {quote.deposit_memo}")

        # 2. Send funds to quote.deposit_address, then poll for status
        while True:
            status = await client.get_status(quote.deposit_address, quote.deposit_memo)
            print(status.status)
            if status.status in {SwapStatus.SUCCESS, SwapStatus.REFUNDED, SwapStatus.FAILED}:
                break
            await asyncio.sleep(10)

asyncio.run(main())
```

## Authentication

Most endpoints require a JWT token. Pass it when constructing the client:

```python
client = IntentsClient(jwt_token="your-jwt-token")
```

## API reference

Full API reference is on [Read the Docs](https://intents-py.readthedocs.io/en/latest/).

### `IntentsClient`

| Method | Description |
|---|---|
| `get_tokens()` | List all supported tokens |
| `get_quote(request)` | Request a swap quote |
| `get_status(deposit_address, deposit_memo?)` | Check swap status |
| `get_any_input_withdrawals(deposit_address, ...)` | Get withdrawals for an `ANY_INPUT` quote |
| `submit_deposit(request)` | Notify the service a deposit has been sent |

### Utilities

| Function | Description |
|---|---|
| `find_token(tokens, blockchain, symbol)` | Look up a token by chain and symbol |
| `to_atomic(amount, decimals)` | Convert `0.1` → `"100000000000000000"` |
| `from_atomic(amount, decimals)` | Convert `"100000000000000000"` → `Decimal("0.1")` |
| `token_to_atomic(amount, token)` | `to_atomic` using a `TokenResponse` |
| `token_from_atomic(amount, token)` | `from_atomic` using a `TokenResponse` |
| `pct_to_bps(percent)` | Convert `1` (%) → `100` (bps) |
| `bps_to_pct(bps)` | Convert `100` (bps) → `Decimal("1")` (%) |

### Swap types

| Value | Behaviour |
|---|---|
| `EXACT_INPUT` | Specify input amount, receive calculated output |
| `EXACT_OUTPUT` | Specify output amount, deposit calculated input |
| `FLEX_INPUT` | Variable input with slippage bounds |
| `ANY_INPUT` | Multiple partial deposits over time |

### Swap statuses

`KNOWN_DEPOSIT_TX` → `PENDING_DEPOSIT` → `PROCESSING` → `SUCCESS`

Terminal states: `SUCCESS`, `REFUNDED`, `FAILED`

## Examples

See the [`examples/`](examples/) directory:

- [`list_tokens.py`](examples/list_tokens.py) — fetch and display all supported tokens
- [`dry_quote.py`](examples/dry_quote.py) — preview a swap without creating a deposit address
- [`swap.py`](examples/swap.py) — full swap lifecycle with status polling
- [`submit_deposit.py`](examples/submit_deposit.py) — notify the service after sending funds
- [`any_input_withdrawals.py`](examples/any_input_withdrawals.py) — fetch `ANY_INPUT` withdrawals

## License

MIT
