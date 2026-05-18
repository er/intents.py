from __future__ import annotations

from datetime import datetime, timezone

import httpx
import pytest
import respx

from intents import (
    DepositType,
    IntentsAPIError,
    IntentsAuthError,
    IntentsClient,
    QuoteRequest,
    RecipientType,
    RefundType,
    SubmitDepositRequest,
    SwapStatus,
    SwapType,
)

BASE_URL = "https://1click.chaindefuser.com"


def _quote_request() -> QuoteRequest:
    return QuoteRequest(
        dry=True,
        swap_type=SwapType.EXACT_INPUT,
        slippage_tolerance=100,
        origin_asset="nep141:eth.omft.near",
        deposit_type=DepositType.ORIGIN_CHAIN,
        destination_asset="nep141:arb.omft.near",
        amount="10000000000000000",
        refund_to="0xabc",
        refund_type=RefundType.ORIGIN_CHAIN,
        recipient="0xabc",
        recipient_type=RecipientType.DESTINATION_CHAIN,
        deadline=datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
    )


class TestGetTokens:
    @respx.mock
    async def test_returns_parsed_tokens(self, client, tokens_payload):
        respx.get(f"{BASE_URL}/v0/tokens").mock(
            return_value=httpx.Response(200, json=tokens_payload)
        )

        tokens = await client.get_tokens()

        assert len(tokens) == 2
        assert tokens[0].symbol == "ETH"
        assert tokens[0].decimals == 18
        assert tokens[1].symbol == "USDC"
        assert tokens[1].contract_address == "0xaf88d065e77c8cc2239327c5edb3a432268e5831"

    @respx.mock
    async def test_no_auth_header_when_token_absent(self, client, tokens_payload):
        route = respx.get(f"{BASE_URL}/v0/tokens").mock(
            return_value=httpx.Response(200, json=tokens_payload)
        )

        await client.get_tokens()

        assert "Authorization" not in route.calls.last.request.headers


class TestGetQuote:
    @respx.mock
    async def test_posts_camel_case_body(self, client, quote_response_payload):
        route = respx.post(f"{BASE_URL}/v0/quote").mock(
            return_value=httpx.Response(200, json=quote_response_payload)
        )

        response = await client.get_quote(_quote_request())

        assert response.quote.deposit_address == "0xdepositaddr"
        assert response.correlation_id == "corr-123"

        sent = route.calls.last.request.read().decode()
        assert "swapType" in sent
        assert "originAsset" in sent
        assert "swap_type" not in sent

    @respx.mock
    async def test_400_raises_api_error(self, client, quote_response_payload):
        respx.post(f"{BASE_URL}/v0/quote").mock(
            return_value=httpx.Response(400, json={"message": "bad request"})
        )

        with pytest.raises(IntentsAPIError) as exc_info:
            await client.get_quote(_quote_request())

        assert exc_info.value.status_code == 400
        assert "bad request" in str(exc_info.value)

    @respx.mock
    async def test_401_raises_auth_error(self, client):
        respx.post(f"{BASE_URL}/v0/quote").mock(
            return_value=httpx.Response(401, json={"message": "unauthorized"})
        )

        with pytest.raises(IntentsAuthError):
            await client.get_quote(_quote_request())

    @respx.mock
    async def test_500_with_non_json_body(self, client):
        respx.post(f"{BASE_URL}/v0/quote").mock(
            return_value=httpx.Response(500, text="internal error")
        )

        with pytest.raises(IntentsAPIError) as exc_info:
            await client.get_quote(_quote_request())

        assert exc_info.value.status_code == 500
        assert "internal error" in str(exc_info.value)


class TestGetStatus:
    @respx.mock
    async def test_passes_deposit_address(self, client, status_response_payload):
        route = respx.get(f"{BASE_URL}/v0/status").mock(
            return_value=httpx.Response(200, json=status_response_payload)
        )

        response = await client.get_status("0xdepositaddr")

        assert response.status == SwapStatus.PROCESSING
        assert route.calls.last.request.url.params["depositAddress"] == "0xdepositaddr"
        assert "depositMemo" not in route.calls.last.request.url.params

    @respx.mock
    async def test_passes_memo_when_provided(self, client, status_response_payload):
        route = respx.get(f"{BASE_URL}/v0/status").mock(
            return_value=httpx.Response(200, json=status_response_payload)
        )

        await client.get_status("0xdepositaddr", "memo-abc")

        assert route.calls.last.request.url.params["depositMemo"] == "memo-abc"

    @respx.mock
    async def test_404_raises_api_error(self, client):
        respx.get(f"{BASE_URL}/v0/status").mock(
            return_value=httpx.Response(404, json={"message": "not found"})
        )

        with pytest.raises(IntentsAPIError) as exc_info:
            await client.get_status("0xdepositaddr")

        assert exc_info.value.status_code == 404


class TestGetAnyInputWithdrawals:
    @respx.mock
    async def test_required_param_only(self, client, any_input_withdrawals_payload):
        route = respx.get(f"{BASE_URL}/v0/any-input/withdrawals").mock(
            return_value=httpx.Response(200, json=any_input_withdrawals_payload)
        )

        await client.get_any_input_withdrawals("0xdepositaddr")

        params = route.calls.last.request.url.params
        assert params["depositAddress"] == "0xdepositaddr"
        assert list(params.keys()) == ["depositAddress"]

    @respx.mock
    async def test_all_params(self, client, any_input_withdrawals_payload):
        route = respx.get(f"{BASE_URL}/v0/any-input/withdrawals").mock(
            return_value=httpx.Response(200, json=any_input_withdrawals_payload)
        )

        await client.get_any_input_withdrawals(
            deposit_address="0xdepositaddr",
            deposit_memo="memo",
            timestamp_from="2026-01-01T00:00:00Z",
            page=2,
            limit=25,
            sort_order="desc",
        )

        params = route.calls.last.request.url.params
        assert params["depositAddress"] == "0xdepositaddr"
        assert params["depositMemo"] == "memo"
        assert params["timestampFrom"] == "2026-01-01T00:00:00Z"
        assert params["page"] == "2"
        assert params["limit"] == "25"
        assert params["sortOrder"] == "desc"


class TestSubmitDeposit:
    @respx.mock
    async def test_posts_camel_case_body(self, client, submit_deposit_payload):
        route = respx.post(f"{BASE_URL}/v0/deposit/submit").mock(
            return_value=httpx.Response(200, json=submit_deposit_payload)
        )

        response = await client.submit_deposit(
            SubmitDepositRequest(
                tx_hash="0xtxhash",
                deposit_address="0xdepositaddr",
                memo="memo-abc",
            )
        )

        assert response.status == SwapStatus.PROCESSING
        sent = route.calls.last.request.read().decode()
        assert "txHash" in sent
        assert "depositAddress" in sent
        assert "tx_hash" not in sent

    @respx.mock
    async def test_excludes_none_fields(self, client, submit_deposit_payload):
        route = respx.post(f"{BASE_URL}/v0/deposit/submit").mock(
            return_value=httpx.Response(200, json=submit_deposit_payload)
        )

        await client.submit_deposit(
            SubmitDepositRequest(tx_hash="0xtxhash", deposit_address="0xdepositaddr")
        )

        sent = route.calls.last.request.read().decode()
        assert "memo" not in sent
        assert "nearSenderAccount" not in sent


class TestAuthentication:
    @respx.mock
    async def test_jwt_token_sent_as_bearer(self, auth_client, tokens_payload):
        route = respx.get(f"{BASE_URL}/v0/tokens").mock(
            return_value=httpx.Response(200, json=tokens_payload)
        )

        await auth_client.get_tokens()

        assert route.calls.last.request.headers["Authorization"] == "Bearer test-jwt"

    @respx.mock
    async def test_custom_base_url(self, tokens_payload):
        respx.get("https://custom.example.com/v0/tokens").mock(
            return_value=httpx.Response(200, json=tokens_payload)
        )

        async with IntentsClient(base_url="https://custom.example.com") as c:
            tokens = await c.get_tokens()

        assert len(tokens) == 2


class TestContextManager:
    @respx.mock
    async def test_closes_on_exit(self, tokens_payload):
        respx.get(f"{BASE_URL}/v0/tokens").mock(
            return_value=httpx.Response(200, json=tokens_payload)
        )

        async with IntentsClient() as c:
            await c.get_tokens()

        assert c._http.is_closed
