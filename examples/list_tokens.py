"""List all supported tokens, optionally filtered by blockchain."""

import asyncio

from intents import IntentsClient


async def main() -> None:
    async with IntentsClient() as client:
        tokens = await client.get_tokens()

    print(f"{'Symbol':<12} {'Blockchain':<12} {'Price (USD)':<14} Asset ID")
    print("-" * 80)
    for token in sorted(tokens, key=lambda t: (t.blockchain, t.symbol)):
        price = f"${token.price:.4f}"
        print(f"{token.symbol:<12} {token.blockchain:<12} {price:<14} {token.asset_id}")


if __name__ == "__main__":
    asyncio.run(main())
