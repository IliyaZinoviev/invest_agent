from asyncio import iscoroutine

from type_aliases import FullyAppicatedFunc


class Prompt:

    @staticmethod
    async def prompt(
            on_reading_fn: FullyAppicatedFunc,
            on_writing_fn: FullyAppicatedFunc,
            fn: FullyAppicatedFunc,
            input_msg: str):
        while True:
            try:
                reading_flag = input(input_msg)
                assert reading_flag in ['r', 'w', 'i'], 'Only [r/w/i] are available!'
            except Exception:
                pass
            else:
                if reading_flag == 'r':
                    return on_reading_fn()
                elif reading_flag == 'w':
                    if iscoroutine(on_writing_fn):
                        return await on_writing_fn()
                elif reading_flag == 'i':
                    if iscoroutine(fn):
                        return iscoroutine(fn)
