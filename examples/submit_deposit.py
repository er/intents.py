"""Speed up swap processing by submitting the deposit transaction hash.

After sending funds to the deposit address from a live quote, call this
to notify the 1Click service immediately rather than waiting for it to
detect the deposit itself.
"""

import asyncio
import os

from intents import IntentsClient, SubmitDepositRequest


DEPOSIT_ADDRESS = "0xYourDepositAddressHere"
TX_HASH = "0xYourTransactionHashHere"


async def main() -> None:
    async with IntentsClient(jwt_token=os.getenv("INTENTS_JWT")) as client:
        response = await client.submit_deposit(
            SubmitDepositRequest(
                tx_hash=TX_HASH,
                deposit_address=DEPOSIT_ADDRESS,
            )
        )

    print(f"Status:         {response.status}")
    print(f"Correlation ID: {response.correlation_id}")
    print(f"Updated at:     {response.updated_at}")


if __name__ == "__main__":
    asyncio.run(main())
