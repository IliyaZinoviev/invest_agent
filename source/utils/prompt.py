from utils.universal_call import call_fn_universally


class Prompt:

    @classmethod
    async def prompt(cls, on_reading_fn, on_writing_fn, fn, input_msg: str):
        while True:
            try:
                command = input(input_msg)
                assert command in ['r', 'w', 'i'], 'Only [r/w/i] are available!'
            except Exception:
                pass
            else:
                return await cls.exec_command(on_reading_fn, on_writing_fn, fn, command)

    @staticmethod
    async def exec_command(on_reading_fn, on_writing_fn, fn, command: str):
        if command == 'r':
            return on_reading_fn()
        elif command == 'w':
            return await on_writing_fn()
        elif command == 'i':
            return await call_fn_universally(fn)
