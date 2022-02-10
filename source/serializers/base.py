from pydantic import BaseModel


class AliasModel(BaseModel):

    def dict(self, *args, **kwargs):
        if 'by_alias' not in kwargs:
            kwargs['by_alias'] = True
        return super().dict(*args, **kwargs)

    def json(self, *args, **kwargs):
        if 'by_alias' not in kwargs:
            kwargs['by_alias'] = True
        return super().dict(*args, **kwargs)

    class Config:
        allow_population_by_field_name = True
