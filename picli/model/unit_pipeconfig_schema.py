from marshmallow import fields
from marshmallow import Schema
from marshmallow import RAISE
from marshmallow import ValidationError


class PiUnitPipeVarsSchema(Schema):
    run_pipe = fields.Bool(required=True)
    url = fields.Str(required=True)
    version = fields.Str(required=True)


class UnitPipeConfigSchema(Schema):
    pi_unit_pipe_vars = fields.Nested(PiUnitPipeVarsSchema)


def validate(config):
    schema = UnitPipeConfigSchema(unknown=RAISE)
    try:
        _ = schema.load(config)
        result = None
    except ValidationError as err:
        result = err
    return result
