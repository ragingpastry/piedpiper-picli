from marshmallow import fields
from marshmallow import Schema
from marshmallow import RAISE
from marshmallow import ValidationError


class PiSastPipeVarsSchema(Schema):
    run_pipe = fields.Bool(required=True)
    url = fields.Str(required=True)
    version = fields.Str(required=True)


class SastPipeConfigSchema(Schema):
    pi_sast_pipe_vars = fields.Nested(PiSastPipeVarsSchema)


def validate(config):
    schema = SastPipeConfigSchema(unknown=RAISE)
    try:
        _ = schema.load(config)
        result = None
    except ValidationError as err:
        result = err
    return result
