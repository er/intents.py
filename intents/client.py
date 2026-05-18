from __future__ import annotations

from types import TracebackType
from typing import Literal

import httpx

from .exceptions import IntentsAPIError, IntentsAuthError
from .models import (
    AnyInputWithdrawalsResponse,
    ExecutionStatusResponse,
    QuoteRequest,
    QuoteResponse,
    SubmitDepositRequest,
    SubmitDepositResponse,
    TokenResponse,
)

_BASE_URL = "https://1click.chaindefuser.com"


class IntentsClient:
    """Async client for the NEAR Intents 1Click Swap API.

    Can be used as an async context manager or standalone. When used standalone,
    call :meth:`aclose` when finished.

    Args:
        jwt_token: Optional Bearer JWT token for authenticated endpoints.
        base_url: Override the default API base URL.
        timeout: Request timeout in seconds (default: 30).
    """

    def __init__(
        self,
        jwt_token: str | None = None,
        base_url: str = _BASE_URL,
        timeout: float = 30.0,
    ) -> None:
        headers: dict[str, str] = {"Accept": "application/json", "Content-Type": "application/json"}
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"

        self._http = httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            timeout=timeout,
        )

    async def __aenter__(self) -> IntentsClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._http.aclose()

    async def _raise_for_status(self, response: httpx.Response) -> None:
        if response.status_code == 401:
            raise IntentsAuthError(401, "Unauthorized — JWT token is missing or invalid")
        if response.is_error:
            try:
                message = self._parse_json(response).get("message", response.text)
            except Exception:
                message = response.text
            raise IntentsAPIError(response.status_code, message)

    def _parse_json(self, response: httpx.Response) -> object:
        if not response.content:
            raise IntentsAPIError(response.status_code, "Empty response body")
        return response.json()

    async def get_tokens(self) -> list[TokenResponse]:
        """Retrieve all tokens supported by the 1Click API.

        Returns:
            List of :class:`~intents.models.TokenResponse` objects.
        """
        response = await self._http.get("/v0/tokens")
        await self._raise_for_status(response)
        return [TokenResponse.model_validate(item) for item in self._parse_json(response)]  # type: ignore[union-attr]

    async def get_quote(self, request: QuoteRequest) -> QuoteResponse:
        """Request a swap quote.

        Pass ``dry=True`` on the request to simulate the quote without
        generating a deposit address.

        Args:
            request: Swap parameters as a :class:`~intents.models.QuoteRequest`.

        Returns:
            :class:`~intents.models.QuoteResponse` with the deposit address
            and expected output amounts.

        Raises:
            IntentsAPIError: On HTTP 400 (bad request).
            IntentsAuthError: On HTTP 401 (invalid JWT).
        """
        response = await self._http.post(
            "/v0/quote",
            json=request.to_api_dict(),

        )
        await self._raise_for_status(response)
        return QuoteResponse.model_validate(self._parse_json(response))

    async def get_status(
        self,
        deposit_address: str,
        deposit_memo: str | None = None,
    ) -> ExecutionStatusResponse:
        """Check the execution status of a swap.

        Args:
            deposit_address: The deposit address returned by :meth:`get_quote`.
            deposit_memo: Required for chains that use memo-based deposits.

        Returns:
            :class:`~intents.models.ExecutionStatusResponse`.

        Raises:
            IntentsAPIError: On HTTP 404 (deposit address not found).
            IntentsAuthError: On HTTP 401 (invalid JWT).
        """
        params: dict[str, str] = {"depositAddress": deposit_address}
        if deposit_memo is not None:
            params["depositMemo"] = deposit_memo

        response = await self._http.get(
            "/v0/status",
            params=params,

        )
        await self._raise_for_status(response)
        return ExecutionStatusResponse.model_validate(self._parse_json(response))

    async def get_any_input_withdrawals(
        self,
        deposit_address: str,
        deposit_memo: str | None = None,
        timestamp_from: str | None = None,
        page: int | None = None,
        limit: int | None = None,
        sort_order: Literal["asc", "desc"] | None = None,
    ) -> AnyInputWithdrawalsResponse:
        """Retrieve withdrawals for an ``ANY_INPUT`` quote.

        Args:
            deposit_address: The deposit address for the quote.
            deposit_memo: Memo used with the deposit, if applicable.
            timestamp_from: ISO timestamp to filter withdrawals from.
            page: Page number for pagination (default: 1).
            limit: Withdrawals per page (max 50, default: 50).
            sort_order: ``"asc"`` or ``"desc"``.

        Returns:
            :class:`~intents.models.AnyInputWithdrawalsResponse`.
        """
        params: dict[str, str | int] = {"depositAddress": deposit_address}
        if deposit_memo is not None:
            params["depositMemo"] = deposit_memo
        if timestamp_from is not None:
            params["timestampFrom"] = timestamp_from
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if sort_order is not None:
            params["sortOrder"] = sort_order

        response = await self._http.get(
            "/v0/any-input/withdrawals",
            params=params,

        )
        await self._raise_for_status(response)
        return AnyInputWithdrawalsResponse.model_validate(self._parse_json(response))

    async def submit_deposit(self, request: SubmitDepositRequest) -> SubmitDepositResponse:
        """Notify the 1Click service that a deposit transaction has been sent.

        This is optional but can speed up swap processing by allowing the
        service to preemptively verify the deposit.

        Args:
            request: Deposit details as a :class:`~intents.models.SubmitDepositRequest`.

        Returns:
            :class:`~intents.models.SubmitDepositResponse`.

        Raises:
            IntentsAPIError: On HTTP 400 (bad request).
            IntentsAuthError: On HTTP 401 (invalid JWT).
        """
        response = await self._http.post(
            "/v0/deposit/submit",
            json=request.to_api_dict(),

        )
        await self._raise_for_status(response)
        return SubmitDepositResponse.model_validate(self._parse_json(response))
