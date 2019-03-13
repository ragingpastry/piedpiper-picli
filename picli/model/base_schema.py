from marshmallow import fields
from marshmallow import Schema
from marshmallow import RAISE
from marshmallow import ValidationError
from marshmallow import validates


class PiGlobalVarsSchema(Schema):
    project_name = fields.Str(required=True)
    ci_provider = fields.Str(required=True)
    vars_dir = fields.Str(required=True)
    version = fields.Str(required=True)

    @validates
    def validate_ci_provider(self, value):
        supported_ci_providers = [
            'gitlab-ci'
        ]
        if value not in supported_ci_providers:
            raise ValueError(f'ci_provider must be one of {supported_ci_providers}. You supplied {value}')


class BaseSchema(Schema):
    pi_global_vars = fields.Nested(PiGlobalVarsSchema)


def validate(config):
    schema = BaseSchema(unknown=RAISE)
    try:
        _ = schema.load(config)
        result = None
    except ValidationError as err:
        result = err
    return result
