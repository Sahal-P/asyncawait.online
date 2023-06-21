import json
from uuid import UUID
import msgpack


class UUIDDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.dict_to_object, *args, **kwargs)

    def dict_to_object(self, d):
        for key, value in d.items():
            if isinstance(value, str) and self.is_valid_uuid(value):
                d[key] = UUID(value)
        return d

    @staticmethod
    def is_valid_uuid(uuid_string):
        try:
            UUID(uuid_string)
            return True
        except ValueError:
            return False


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)


# json_data = '{"uuid_field": "550e8400-e29b-41d4-a716-446655440000"}'
# data = json.loads(json_data, cls=UUIDDecoder)
