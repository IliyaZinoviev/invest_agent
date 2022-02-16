from typing import Any

import simplejson

from utils.json.encoder import EnhancedJSONEncoder
from utils.universal_call import call_fn_universally


class WriteJson:

    @classmethod
    async def _write_fn_res_to_json(cls, path: str, fn):
        res = await call_fn_universally(fn)
        cls.write_json(path, res)
        return res

    @staticmethod
    def write_json(path: str, data: Any):
        with open(path, 'w') as file:
            simplejson.dump(data, file, cls=EnhancedJSONEncoder, ensure_ascii=False)
