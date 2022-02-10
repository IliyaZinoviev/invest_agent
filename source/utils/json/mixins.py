import simplejson
from pydantic import BaseModel, parse_obj_as


class ReadJson:

    @staticmethod
    def read_json(path, *, serializer=None):
        with open(path, 'r') as file:
            data = simplejson.load(file)
            if serializer:
                if isinstance(data, dict):
                    res = parse_obj_as(serializer, data)
            else:
                res = data
            return res
