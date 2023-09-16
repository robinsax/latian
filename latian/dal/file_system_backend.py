'''
Storage backend implementation using a JSON file.
'''
import io
import json
import os.path
from typing import Union, Type, Any
from datetime import datetime

from ..cli import CLIArgs
from ..model import Model
from .storage_backend import T, StorageBackend, storage_backends

DATETIME_FORMAT = '%d/%m/%Y %H:%M'

@storage_backends.implementation('file')
class FileSystemStorageBackend(StorageBackend):
    data: dict
    user: str

    def __init__(
        self, schema: dict[str, Type[Model]], args: CLIArgs
    ):
        super().__init__(schema, args)
        self.data = None
        self.user = None

    def _get_file_path(self):
        return '%s/%s.db.json'%(
            self.args.get('storage_dest'),
            self.user
        )

    def _hydrate_model(
        self, Type: Type[Model], model_data: dict[str, Any]
    ) -> Model:
        model = Type()
        model_schema = Type.schema()
        for key in model_schema:
            value = model_data[key]
            if type(model_schema[key]) is list:
                inner_type = model_schema[key][0]

                hydrated_value = list()
                for item in value:
                    if issubclass(inner_type, Model):
                        item = self._hydrate_model(
                            inner_type, item
                        )
                    
                    hydrated_value.append(item)
                value = hydrated_value

            if model_schema[key] is datetime:
                value = datetime.strptime(value, DATETIME_FORMAT)
            
            setattr(model, key, value)

        return model

    def _dehydrate_model(
        self, Type: Type[Model], model: Model
    ) -> dict[str, Any]:
        model_data = dict()
        model_schema = Type.schema()
        for key in model_schema:
            value = getattr(model, key)
            if type(model_schema[key]) is list:
                inner_type = model_schema[key][0]

                dehydrated_value = list()
                for item in value:
                    if issubclass(inner_type, Model):
                        item = self._dehydrate_model(
                            inner_type, item
                        )
                    
                    dehydrated_value.append(item)
                value = dehydrated_value
            if model_schema[key] is datetime:
                value = value.strftime(DATETIME_FORMAT)

            model_data[key] = value

        return model_data
    
    def _filter(
        self, models: list[Model], filter: dict[str, Any]
    ):
        result = list()
        for model in models:
            for key in filter:
                if getattr(model, key) != filter[key]:
                    break
            else:
                result.append(model)

        return result

    async def initialize(self):
        print('no initialization required')

    async def connect(self, user: str) -> bool:
        self.user = user

        file_path = self._get_file_path()
        if not os.path.isfile(file_path):
            self.data = dict()
            for collection_name in self.schema:
                self.data[collection_name] = list()

            return

        raw_data = dict()
        with io.open(file_path, encoding='utf-8') as file_io:
            raw_data = json.load(file_io)

        self.data = dict()
        for collection_name, Type in self.schema.items():
            models = list()
            for model_data in raw_data[collection_name]:
                models.append(
                    self._hydrate_model(Type, model_data)
                )

            self.data[collection_name] = models

    async def disconnect(self):
        pass

    async def commit(self):
        raw_data = dict()
        for collection_name, Type in self.schema.items():
            collection_data = list()
            for model in self.data[collection_name]:
                collection_data.append(
                    self._dehydrate_model(Type, model)
                )

            raw_data[collection_name] = collection_data

        file_path = self._get_file_path()
        with io.open(file_path, 'w', encoding='utf-8') as file_io:
            json.dump(raw_data, file_io)

    async def query(
        self,
        Target: Type[T],
        filter: dict[str, Any] = None
    ) -> Union[list[T], int]:
        collection_name = Target.collection_name()

        result = self.data[collection_name]
        if filter:
            result = self._filter(result, filter)

        return result
    
    async def create(self, model: Model):
        self.data[model.__class__.collection_name()].append(model)
    
    async def delete(
        self, Target: Type[T], filter: dict[str, Any] = None
    ):
        collection_name = Target.collection_name()
 
        retain = list()
        if filter:
            retain = self._filter(self.data[collection_name], filter)
        
        self.data[collection_name] = retain
