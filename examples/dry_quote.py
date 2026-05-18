"""Preview a swap quote without creating a deposit address.

Simulates swapping 0.01 ETH (Ethereum) → USDC (Arbitrum).
No funds are moved — dry=True means no deposit address is generated.
"""

import asyncio
from datetime import datetime, timedelta, timezone

from intents import (
    DepositType,
    IntentsClient,
    QuoteRequest,
    RecipientType,
    RefundType,
    SwapType,
    find_token,
    from_atomic,
    token_to_atomic,
)

REFUND_ADDRESS = "0x2527D02599Ba641c19FEa793cD0F167589a0f10D"
RECIPIENT_ADDRESS = "0x2527D02599Ba641c19FEa793cD0F167589a0f10D"
AMOUNT_ETH = "0.01"


async def main() -> None:
    async with IntentsClient() as client:
        tokens = await client.get_tokens()

        eth = find_token(tokens, "eth", "ETH")
        usdc = find_token(tokens, "arb", "USDC")

        response = await client.get_quote(
            QuoteRequest(
                dry=True,
                swap_type=SwapType.EXACT_INPUT,
                slippage_tolerance=100,
                origin_asset=eth.asset_id,
                destination_asset=usdc.asset_id,
                deposit_type=DepositType.ORIGIN_CHAIN,
                amount=token_to_atomic(AMOUNT_ETH, eth),
                refund_to=REFUND_ADDRESS,
                refund_type=RefundType.ORIGIN_CHAIN,
                recipient=RECIPIENT_ADDRESS,
                recipient_type=RecipientType.DESTINATION_CHAIN,
                deadline=datetime.now(timezone.utc) + timedelta(hours=1),
            )
        )

    quote = response.quote
    print(f"Swap preview: {AMOUNT_ETH} ETH → USDC")
    print(f"  Amount in:       {quote.amount_in_formatted} ETH (${quote.amount_in_usd})")
    print(f"  Expected out:    {quote.amount_out_formatted} USDC (${quote.amount_out_usd})")
    print(f"  Minimum out:     {from_atomic(quote.min_amount_out, usdc.decimals):.6f} USDC")
    print(f"  Time estimate:   {quote.time_estimate}s")
    print(f"  Correlation ID:  {response.correlation_id}")


if __name__ == "__main__":
    asyncio.run(main())
