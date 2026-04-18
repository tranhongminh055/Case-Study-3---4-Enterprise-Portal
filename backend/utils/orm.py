from datetime import date
from decimal import Decimal


def serialize_model(instance):
    payload = {}
    for key, value in vars(instance).items():
        if key.startswith("_"):
            continue
        if isinstance(value, date):
            payload[key] = value.isoformat()
        elif isinstance(value, Decimal):
            payload[key] = float(value)
        else:
            payload[key] = value
    return payload


def serialize_list(instances):
    return [serialize_model(instance) for instance in instances]
