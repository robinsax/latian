'''
Abstract base for data models.
'''
from dataclasses import asdict, fields

class Model:

    @classmethod
    def collection_name(cls) -> str:
        raise NotImplementedError()

    @classmethod
    def schema(cls):
        attributes = fields(cls)
        schema = dict()
        for attribute in attributes:
            schema[attribute.name] = attribute.type

        return schema
