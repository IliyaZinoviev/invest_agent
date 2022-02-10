import dataclasses

from pydantic import BaseModel
from simplejson import JSONEncoder


class EnhancedJSONEncoder(JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, BaseModel):
            return o.dict()
        return super().default(o)