from decimal import Decimal
from typing import TypeAlias, Union, Callable, Any

Ticker: TypeAlias = str
Figi: TypeAlias = str
Asset: TypeAlias = Union[int, Decimal]

FullyAppicatedFunc: TypeAlias = Callable[[], Any]
