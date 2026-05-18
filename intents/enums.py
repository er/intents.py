from __future__ import annotations

from enum import Enum


class SwapType(str, Enum):
    EXACT_INPUT = "EXACT_INPUT"
    EXACT_OUTPUT = "EXACT_OUTPUT"
    FLEX_INPUT = "FLEX_INPUT"
    ANY_INPUT = "ANY_INPUT"


class DepositType(str, Enum):
    ORIGIN_CHAIN = "ORIGIN_CHAIN"
    INTENTS = "INTENTS"


class RecipientType(str, Enum):
    DESTINATION_CHAIN = "DESTINATION_CHAIN"
    INTENTS = "INTENTS"


class DepositMode(str, Enum):
    SIMPLE = "SIMPLE"
    MEMO = "MEMO"


class RefundType(str, Enum):
    ORIGIN_CHAIN = "ORIGIN_CHAIN"
    INTENTS = "INTENTS"


class SwapStatus(str, Enum):
    KNOWN_DEPOSIT_TX = "KNOWN_DEPOSIT_TX"
    PENDING_DEPOSIT = "PENDING_DEPOSIT"
    INCOMPLETE_DEPOSIT = "INCOMPLETE_DEPOSIT"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    REFUNDED = "REFUNDED"
    FAILED = "FAILED"
