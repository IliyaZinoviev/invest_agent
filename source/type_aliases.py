from collections.abc import Callable, Coroutine
from decimal import Decimal
from typing import TypeAlias, Any, Protocol

Ticker: TypeAlias = str
Figi: TypeAlias = str
Asset: TypeAlias = int | Decimal


class FullyAppliedFn(Protocol):
    func: Callable[[], Coroutine[None, None, Any] | Any]
    def __call__(self): ...
