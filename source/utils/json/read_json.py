from typing import Any

import simplejson
from pydantic import parse_obj_as


class ReadJson:

    @staticmethod
    def read_json(path, *, serializer=None) -> Any:
        with open(path, 'r') as file:
            data = simplejson.load(file)
            if serializer:
                res = parse_obj_as(serializer, data)
            else:
                res = data
            return res
