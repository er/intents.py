# Examples

Runnable scripts from the [`examples/`](https://github.com/er/intents.py/tree/main/examples) directory in the repo.

## List tokens

List all supported tokens, optionally filtered by blockchain.

```{literalinclude} ../examples/list_tokens.py
:language: python
:linenos:
```

## Dry quote

Preview a swap quote without creating a deposit address — no funds move.

```{literalinclude} ../examples/dry_quote.py
:language: python
:linenos:
```

## Swap

End-to-end live swap: fetch a real quote, get a deposit address, then poll for execution status.

```{literalinclude} ../examples/swap.py
:language: python
:linenos:
```

## Submit deposit

Notify the 1Click service of an on-chain deposit transaction hash so it processes the swap immediately.

```{literalinclude} ../examples/submit_deposit.py
:language: python
:linenos:
```

## Any-input withdrawals

Fetch withdrawals for an `ANY_INPUT` quote, paginating through results.

```{literalinclude} ../examples/any_input_withdrawals.py
:language: python
:linenos:
```
