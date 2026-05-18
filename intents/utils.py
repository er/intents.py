from __future__ import annotations

from decimal import ROUND_DOWN, Decimal

from .models import TokenResponse


def to_atomic(amount: int | float | str | Decimal, decimals: int) -> str:
    """Convert a human-readable token amount to its atomic (smallest unit) string.

    Uses :class:`~decimal.Decimal` internally to avoid floating-point errors.

    Args:
        amount: Human-readable amount, e.g. ``0.1`` or ``"0.1"``.
        decimals: Number of decimals for the token (from :attr:`TokenResponse.decimals`).

    Returns:
        Atomic amount as a string, e.g. ``"100000000000000000"`` for 0.1 ETH.

    Raises:
        ValueError: If the amount is negative or has more decimal places than
            the token supports.

    Examples:
        >>> to_atomic("0.1", 18)   # 0.1 ETH → wei
        '100000000000000000'
        >>> to_atomic(1, 24)       # 1 NEAR → yoctoNEAR
        '1000000000000000000000000'
    """
    d = Decimal(str(amount))
    if d < 0:
        raise ValueError(f"Amount must be non-negative, got {amount!r}")

    scaled = d * Decimal(10) ** decimals

    if scaled != scaled.to_integral_value():
        raise ValueError(
            f"{amount!r} has more decimal places than the token supports ({decimals})"
        )

    return str(scaled.to_integral_value(rounding=ROUND_DOWN))


def from_atomic(amount: int | str, decimals: int) -> Decimal:
    """Convert an atomic (smallest unit) token amount to a human-readable :class:`~decimal.Decimal`.

    Args:
        amount: Atomic amount as returned by the API, e.g. ``"100000000000000000"``.
        decimals: Number of decimals for the token.

    Returns:
        Human-readable amount, e.g. ``Decimal("0.1")`` for 0.1 ETH.

    Examples:
        >>> from_atomic("100000000000000000", 18)
        Decimal('0.1')
        >>> from_atomic("1000000000000000000000000", 24)
        Decimal('1')
    """
    return Decimal(str(amount)) / Decimal(10) ** decimals


def token_to_atomic(amount: int | float | str | Decimal, token: TokenResponse) -> str:
    """Convert a human-readable amount to atomic units using a :class:`~intents.models.TokenResponse`.

    Convenience wrapper around :func:`to_atomic` that reads ``decimals`` directly
    from the token object.

    Args:
        amount: Human-readable amount, e.g. ``0.1``.
        token: Token metadata returned by :meth:`~intents.client.IntentsClient.get_tokens`.

    Returns:
        Atomic amount string ready to pass as ``amount`` in a
        :class:`~intents.models.QuoteRequest`.

    Examples:
        >>> tokens = await client.get_tokens()
        >>> eth = find_token(tokens, "eth", "ETH")
        >>> token_to_atomic(0.1, eth)
        '100000000000000000'
    """
    return to_atomic(amount, token.decimals)


def token_from_atomic(amount: int | str, token: TokenResponse) -> Decimal:
    """Convert an atomic amount to a human-readable :class:`~decimal.Decimal` using a :class:`~intents.models.TokenResponse`.

    Args:
        amount: Atomic amount string as returned by the API.
        token: Token metadata returned by :meth:`~intents.client.IntentsClient.get_tokens`.

    Returns:
        Human-readable :class:`~decimal.Decimal`.
    """
    return from_atomic(amount, token.decimals)


def pct_to_bps(percent: int | float | str | Decimal) -> int:
    """Convert a percentage to basis points.

    Args:
        percent: Percentage value, e.g. ``1`` for 1% or ``0.5`` for 0.5%.

    Returns:
        Basis points as an integer, e.g. ``100`` for 1%.

    Examples:
        >>> pct_to_bps(1)
        100
        >>> pct_to_bps(0.5)
        50
    """
    return int(Decimal(str(percent)) * 100)


def bps_to_pct(bps: int) -> Decimal:
    """Convert basis points to a percentage.

    Args:
        bps: Basis points, e.g. ``100`` for 1%.

    Returns:
        Percentage as a :class:`~decimal.Decimal`, e.g. ``Decimal("1")`` for 100 bps.

    Examples:
        >>> bps_to_pct(100)
        Decimal('1')
        >>> bps_to_pct(50)
        Decimal('0.50')
    """
    return Decimal(bps) / 100


def find_token(
    tokens: list[TokenResponse],
    blockchain: str,
    symbol: str,
) -> TokenResponse:
    """Look up a token by blockchain and symbol from a token list.

    Args:
        tokens: Token list returned by :meth:`~intents.client.IntentsClient.get_tokens`.
        blockchain: The chain to search on, e.g. ``"eth"``, ``"arb"``, ``"sol"``.
        symbol: Token symbol, e.g. ``"ETH"``, ``"USDC"``. Case-insensitive.

    Returns:
        The matching :class:`~intents.models.TokenResponse`.

    Raises:
        LookupError: If no token matches the given blockchain and symbol.

    Examples:
        >>> tokens = await client.get_tokens()
        >>> eth = find_token(tokens, "eth", "ETH")
        >>> eth.asset_id
        'nep141:eth.omft.near'
    """
    match = next(
        (t for t in tokens if t.blockchain == blockchain and t.symbol.upper() == symbol.upper()),
        None,
    )
    if match is None:
        raise LookupError(f"No token found for {symbol!r} on {blockchain!r}")
    return match
