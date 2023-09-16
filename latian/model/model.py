'''
Abstract base for data models.
'''
from dataclasses import fields
from types import GenericAlias

class Model:

    @classmethod
    def collection_name(cls) -> str:
        raise NotImplementedError()

    @classmethod
    def schema(cls):
        attributes = fields(cls)
        schema = dict()
        for attribute in attributes:
            if isinstance(attribute.type, GenericAlias):
                schema[attribute.name] = (
                    list((attribute.type.__args__[0],))
                )
                continue

            schema[attribute.name] = attribute.type

        return schema
