"""Execute a real swap: ETH (Ethereum) → USDC (Arbitrum).

Flow:
  1. Fetch a live quote (dry=False) to get a deposit address.
  2. Print the deposit instructions.
  3. Poll the status until the swap completes or fails.

Set INTENTS_JWT in your environment if you have a JWT token.
"""

import asyncio
import os
from datetime import datetime, timedelta, timezone

from intents import (
    DepositType,
    IntentsClient,
    QuoteRequest,
    RecipientType,
    RefundType,
    SwapStatus,
    SwapType,
    find_token,
    token_to_atomic,
)

REFUND_ADDRESS = "0x2527D02599Ba641c19FEa793cD0F167589a0f10D"
RECIPIENT_ADDRESS = "0x2527D02599Ba641c19FEa793cD0F167589a0f10D"
AMOUNT_ETH = "0.01"
POLL_INTERVAL_SECONDS = 10
TERMINAL_STATUSES = {SwapStatus.SUCCESS, SwapStatus.REFUNDED, SwapStatus.FAILED}


async def main() -> None:
    async with IntentsClient(jwt_token=os.getenv("INTENTS_JWT")) as client:
        tokens = await client.get_tokens()
        eth = find_token(tokens, "eth", "ETH")
        usdc = find_token(tokens, "arb", "USDC")

        response = await client.get_quote(
            QuoteRequest(
                dry=False,
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
        print(f"Send exactly {quote.amount_in_formatted} ETH to:")
        print(f"  Deposit address: {quote.deposit_address}")
        if quote.deposit_memo:
            print(f"  Memo (required): {quote.deposit_memo}")
        print(f"  Quote expires:   {quote.deadline}")
        print(f"  Expected out:    {quote.amount_out_formatted} USDC")
        print()

        print("Polling for swap status...")
        while True:
            status_response = await client.get_status(
                deposit_address=quote.deposit_address,
                deposit_memo=quote.deposit_memo,
            )
            status = status_response.status
            print(f"  [{datetime.now().strftime('%H:%M:%S')}] {status}")

            if status in TERMINAL_STATUSES:
                break

            await asyncio.sleep(POLL_INTERVAL_SECONDS)

        details = status_response.swap_details
        if status == SwapStatus.SUCCESS:
            print(f"\nSwap complete!")
            print(f"  Received: {details.amount_out_formatted} USDC (${details.amount_out_usd})")
            for tx in details.destination_chain_tx_hashes:
                print(f"  Explorer: {tx.explorer_url}")
        elif status == SwapStatus.REFUNDED:
            print(f"\nSwap refunded. Reason: {details.refund_reason}")
            print(f"  Refunded: {details.refunded_amount_formatted} ETH")
        else:
            print(f"\nSwap failed.")


if __name__ == "__main__":
    asyncio.run(main())
