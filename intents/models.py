from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from .enums import DepositMode, DepositType, RecipientType, RefundType, SwapStatus, SwapType

_camel = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class TokenResponse(BaseModel):
    model_config = _camel

    asset_id: str
    decimals: int
    blockchain: str
    symbol: str
    price: float
    price_updated_at: datetime
    contract_address: str | None = None


class AppFee(BaseModel):
    model_config = _camel

    recipient: str
    fee: int = Field(ge=0, description="Fee in basis points")


class QuoteRequest(BaseModel):
    model_config = _camel

    dry: bool
    swap_type: SwapType | str
    slippage_tolerance: int = Field(description="Slippage in basis points")
    origin_asset: str
    deposit_type: DepositType | str
    destination_asset: str
    amount: str
    refund_to: str
    refund_type: RefundType | str
    recipient: str
    recipient_type: RecipientType | str
    deadline: datetime
    deposit_mode: DepositMode | str = DepositMode.SIMPLE
    connected_wallets: list[str] | None = None
    session_id: str | None = None
    virtual_chain_recipient: str | None = None
    virtual_chain_refund_recipient: str | None = None
    custom_recipient_msg: str | None = None
    referral: str | None = None
    quote_waiting_time_ms: int = 3000
    app_fees: list[AppFee] | None = None

    def to_api_dict(self) -> dict:
        return self.model_dump(by_alias=True, exclude_none=True, mode="json")


class Quote(BaseModel):
    model_config = _camel

    amount_in: str
    amount_in_formatted: str
    amount_in_usd: str
    min_amount_in: str
    max_amount_in: str | None = None
    amount_out: str
    amount_out_formatted: str
    amount_out_usd: str
    min_amount_out: str
    time_estimate: int = Field(description="Estimated swap time in seconds")
    deposit_address: str | None = None
    deposit_memo: str | None = None
    deadline: datetime | None = None
    time_when_inactive: datetime | None = None
    virtual_chain_recipient: str | None = None
    virtual_chain_refund_recipient: str | None = None
    custom_recipient_msg: str | None = None
    refund_fee: str | None = None


class QuoteResponse(BaseModel):
    model_config = _camel

    correlation_id: str | None = None
    timestamp: datetime
    signature: str
    quote_request: QuoteRequest
    quote: Quote


class TransactionDetails(BaseModel):
    model_config = _camel

    hash: str
    explorer_url: str


class SwapDetails(BaseModel):
    model_config = _camel

    intent_hashes: list[str]
    near_tx_hashes: list[str]
    origin_chain_tx_hashes: list[TransactionDetails]
    destination_chain_tx_hashes: list[TransactionDetails]
    amount_in: str | None = None
    amount_in_formatted: str | None = None
    amount_in_usd: str | None = None
    amount_out: str | None = None
    amount_out_formatted: str | None = None
    amount_out_usd: str | None = None
    slippage: int | None = None
    refunded_amount: str | None = None
    refunded_amount_formatted: str | None = None
    refunded_amount_usd: str | None = None
    refund_reason: str | None = None
    deposited_amount: str | None = None
    deposited_amount_formatted: str | None = None
    deposited_amount_usd: str | None = None
    referral: str | None = None


class ExecutionStatusResponse(BaseModel):
    model_config = _camel

    correlation_id: str
    quote_response: QuoteResponse
    status: SwapStatus
    updated_at: datetime
    swap_details: SwapDetails


class AnyInputWithdrawal(BaseModel):
    model_config = _camel

    status: str
    amount_out_formatted: str
    amount_out_usd: str
    amount_out: str
    withdraw_fee_formatted: str
    withdraw_fee: str
    withdraw_fee_usd: str
    timestamp: str
    hash: str


class AnyInputWithdrawalsResponse(BaseModel):
    model_config = _camel

    asset: str
    recipient: str
    affiliate_recipient: str
    withdrawals: AnyInputWithdrawal | None = None


class SubmitDepositRequest(BaseModel):
    model_config = _camel

    tx_hash: str
    deposit_address: str
    near_sender_account: str | None = None
    memo: str | None = None

    def to_api_dict(self) -> dict:
        return self.model_dump(by_alias=True, exclude_none=True)


class SubmitDepositResponse(BaseModel):
    model_config = _camel

    correlation_id: str
    quote_response: QuoteResponse
    status: SwapStatus
    updated_at: datetime
    swap_details: SwapDetails
