from marshmallow import fields
from marshmallow import Schema
from marshmallow import RAISE
from marshmallow import ValidationError


class PiLintPipeVarsSchema(Schema):
    run_pipe = fields.Bool(required=True)
    url = fields.Str(required=True)


class LintPipeConfigSchema(Schema):
    pi_lint_pipe_vars = fields.Nested(PiLintPipeVarsSchema)


def validate(config):
    schema = LintPipeConfigSchema(unknown=RAISE)
    try:
       _ = schema.load(config)
       result = True
    except ValidationError as err:
        result = err
    return result
