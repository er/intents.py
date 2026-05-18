from __future__ import annotations

import pytest

from intents import IntentsClient

BASE_URL = "https://1click.chaindefuser.com"


@pytest.fixture
async def client():
    async with IntentsClient() as c:
        yield c


@pytest.fixture
async def auth_client():
    async with IntentsClient(jwt_token="test-jwt") as c:
        yield c


@pytest.fixture
def tokens_payload() -> list[dict]:
    return [
        {
            "assetId": "nep141:eth.omft.near",
            "decimals": 18,
            "blockchain": "eth",
            "symbol": "ETH",
            "price": 3500.0,
            "priceUpdatedAt": "2026-01-01T00:00:00Z",
            "contractAddress": None,
        },
        {
            "assetId": "nep141:arb-0xaf88d065e77c8cc2239327c5edb3a432268e5831.omft.near",
            "decimals": 6,
            "blockchain": "arb",
            "symbol": "USDC",
            "price": 1.0,
            "priceUpdatedAt": "2026-01-01T00:00:00Z",
            "contractAddress": "0xaf88d065e77c8cc2239327c5edb3a432268e5831",
        },
    ]


@pytest.fixture
def quote_request_dict() -> dict:
    return {
        "dry": True,
        "swapType": "EXACT_INPUT",
        "slippageTolerance": 100,
        "originAsset": "nep141:eth.omft.near",
        "depositType": "ORIGIN_CHAIN",
        "destinationAsset": "nep141:arb.omft.near",
        "amount": "10000000000000000",
        "refundTo": "0xabc",
        "refundType": "ORIGIN_CHAIN",
        "recipient": "0xabc",
        "recipientType": "DESTINATION_CHAIN",
        "deadline": "2026-12-31T23:59:59Z",
        "depositMode": "SIMPLE",
        "quoteWaitingTimeMs": 3000,
    }


@pytest.fixture
def quote_response_payload(quote_request_dict) -> dict:
    return {
        "correlationId": "corr-123",
        "timestamp": "2026-01-01T00:00:00Z",
        "signature": "sig-xyz",
        "quoteRequest": quote_request_dict,
        "quote": {
            "amountIn": "10000000000000000",
            "amountInFormatted": "0.01",
            "amountInUsd": "35.00",
            "minAmountIn": "10000000000000000",
            "amountOut": "34500000",
            "amountOutFormatted": "34.5",
            "amountOutUsd": "34.50",
            "minAmountOut": "34000000",
            "timeEstimate": 60,
            "depositAddress": "0xdepositaddr",
            "deadline": "2026-12-31T23:59:59Z",
        },
    }


@pytest.fixture
def status_response_payload(quote_response_payload) -> dict:
    return {
        "correlationId": "corr-123",
        "quoteResponse": quote_response_payload,
        "status": "PROCESSING",
        "updatedAt": "2026-01-01T00:01:00Z",
        "swapDetails": {
            "intentHashes": [],
            "nearTxHashes": [],
            "originChainTxHashes": [],
            "destinationChainTxHashes": [],
        },
    }


@pytest.fixture
def submit_deposit_payload(status_response_payload) -> dict:
    return status_response_payload


@pytest.fixture
def any_input_withdrawals_payload() -> dict:
    return {
        "asset": "nep141:eth.omft.near",
        "recipient": "0xrecipient",
        "affiliateRecipient": "0xaffiliate",
        "withdrawals": None,
    }
