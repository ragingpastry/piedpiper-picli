from marshmallow import fields
from marshmallow import Schema
from marshmallow import RAISE
from marshmallow import ValidationError


class PiPolicyChecksSchema(Schema):
    enabled = fields.Bool(required=True)
    enforcing = fields.Bool(required=True)


class PiValidatePipeVarsSchema(Schema):
    run_pipe = fields.Bool(required=True)
    url = fields.Str(required=True)
    policy_checks = fields.Nested(PiPolicyChecksSchema)


class ValidatePipeConfigSchema(Schema):
    pi_validate_pipe_vars = fields.Nested(PiValidatePipeVarsSchema)


def validate(config):
    schema = ValidatePipeConfigSchema(unknown=RAISE)
    try:
       _ = schema.load(config)
       result = True
    except ValidationError as err:
        result = err
    return result
