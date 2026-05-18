from decimal import Decimal

import pytest

from intents import (
    TokenResponse,
    bps_to_pct,
    find_token,
    from_atomic,
    pct_to_bps,
    to_atomic,
    token_from_atomic,
    token_to_atomic,
)


def _token(blockchain: str, symbol: str, decimals: int = 18) -> TokenResponse:
    return TokenResponse(
        asset_id=f"nep141:{symbol.lower()}.{blockchain}.omft.near",
        decimals=decimals,
        blockchain=blockchain,
        symbol=symbol,
        price=1.0,
        price_updated_at="2026-01-01T00:00:00Z",
    )


class TestToAtomic:
    def test_basic_eth(self):
        assert to_atomic("0.1", 18) == "100000000000000000"

    def test_basic_near(self):
        assert to_atomic(1, 24) == "1000000000000000000000000"

    def test_zero(self):
        assert to_atomic(0, 18) == "0"

    def test_accepts_decimal(self):
        assert to_atomic(Decimal("0.5"), 6) == "500000"

    def test_accepts_int(self):
        assert to_atomic(5, 6) == "5000000"

    def test_accepts_float(self):
        assert to_atomic(0.5, 6) == "500000"

    def test_rejects_negative(self):
        with pytest.raises(ValueError, match="non-negative"):
            to_atomic("-1", 18)

    def test_rejects_excess_precision(self):
        with pytest.raises(ValueError, match="more decimal places"):
            to_atomic("0.1234567", 6)

    def test_allows_exact_precision(self):
        assert to_atomic("0.123456", 6) == "123456"


class TestFromAtomic:
    def test_basic(self):
        assert from_atomic("100000000000000000", 18) == Decimal("0.1")

    def test_accepts_int(self):
        assert from_atomic(1_000_000, 6) == Decimal("1")

    def test_near_yocto(self):
        assert from_atomic("1000000000000000000000000", 24) == Decimal("1")

    def test_zero(self):
        assert from_atomic("0", 18) == Decimal("0")


class TestRoundTrip:
    @pytest.mark.parametrize("amount,decimals", [
        ("0.1", 18),
        ("1.5", 6),
        ("123.456", 8),
        ("0.000001", 6),
    ])
    def test_to_from_atomic(self, amount, decimals):
        atomic = to_atomic(amount, decimals)
        assert from_atomic(atomic, decimals) == Decimal(amount)


class TestTokenHelpers:
    def test_token_to_atomic(self):
        eth = _token("eth", "ETH", 18)
        assert token_to_atomic("0.1", eth) == "100000000000000000"

    def test_token_from_atomic(self):
        usdc = _token("arb", "USDC", 6)
        assert token_from_atomic("1500000", usdc) == Decimal("1.5")


class TestPctToBps:
    def test_one_percent(self):
        assert pct_to_bps(1) == 100

    def test_half_percent(self):
        assert pct_to_bps(0.5) == 50

    def test_string(self):
        assert pct_to_bps("0.25") == 25

    def test_zero(self):
        assert pct_to_bps(0) == 0


class TestBpsToPct:
    def test_hundred_bps(self):
        assert bps_to_pct(100) == Decimal("1")

    def test_fifty_bps(self):
        assert bps_to_pct(50) == Decimal("0.50")

    def test_zero(self):
        assert bps_to_pct(0) == Decimal("0")


class TestFindToken:
    def test_matches_symbol_and_chain(self):
        tokens = [_token("eth", "ETH"), _token("arb", "USDC", 6)]
        assert find_token(tokens, "arb", "USDC").symbol == "USDC"

    def test_case_insensitive_symbol(self):
        tokens = [_token("eth", "ETH")]
        assert find_token(tokens, "eth", "eth").symbol == "ETH"

    def test_chain_is_case_sensitive(self):
        tokens = [_token("eth", "ETH")]
        with pytest.raises(LookupError):
            find_token(tokens, "ETH", "ETH")

    def test_missing_raises(self):
        with pytest.raises(LookupError, match="No token found"):
            find_token([_token("eth", "ETH")], "sol", "SOL")

    def test_empty_list_raises(self):
        with pytest.raises(LookupError):
            find_token([], "eth", "ETH")
