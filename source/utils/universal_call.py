import asyncio
from collections.abc import Callable
from functools import partial


async def call_fn_universally(fn):
    if isinstance(fn, partial):
        fn_type_var = fn.func
    else:
        fn_type_var = fn
    if asyncio.iscoroutinefunction(fn_type_var):
        return await fn()
    elif isinstance(fn_type_var, Callable):
        return fn()
    raise TypeError(f'{fn=} is not sync/async func')
