"""Fetch withdrawals for an ANY_INPUT quote with pagination."""

import asyncio
import os

from intents import IntentsClient

DEPOSIT_ADDRESS = "0xYourDepositAddressHere"


async def main() -> None:
    async with IntentsClient(jwt_token=os.getenv("INTENTS_JWT")) as client:
        response = await client.get_any_input_withdrawals(
            deposit_address=DEPOSIT_ADDRESS,
            limit=10,
            sort_order="desc",
        )

    print(f"Asset:     {response.asset}")
    print(f"Recipient: {response.recipient}")

    if response.withdrawals is None:
        print("No withdrawals found.")
        return

    w = response.withdrawals
    print(f"\nWithdrawal:")
    print(f"  Status:   {w.status}")
    print(f"  Amount:   {w.amount_out_formatted} (${w.amount_out_usd})")
    print(f"  Fee:      {w.withdraw_fee_formatted} (${w.withdraw_fee_usd})")
    print(f"  Time:     {w.timestamp}")
    print(f"  Tx hash:  {w.hash}")


if __name__ == "__main__":
    asyncio.run(main())
