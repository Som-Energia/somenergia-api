from flask import Response, make_response
from .errors import (
    ValidateError,
)
from consolemsg import u
from yamlns import namespace as ns

implemented = ns(
    metric=['members', 'contracts'],
    geolevel=['ccaa','state'],
    )


def validateImplementation(data):
    for field, value in data:
        if value not in implemented[field]:
            raise ValidateImplementationMap(field=field, value=value)


class ValidateImplementationMap(ValidateError):
    def __init__(self, field, value):
        self.parameter = field
        self.value = value
        self.possibleValues = implemented[field]
        super(ValidateError, self).__init__("Not implemented "+field+" \'"+value+
            "\' try with "+u(self.possibleValues)
            )