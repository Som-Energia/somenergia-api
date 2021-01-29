# -*- encoding: utf-8 -*-
import os
from dateutil.relativedelta import relativedelta as delta
from datetime import date, timedelta
from flask import Response, make_response, current_app, jsonify
from functools import wraps
from werkzeug.routing import BaseConverter, ValidationError
from yamlns.dateutils import Date
from yamlns import namespace as ns
from consolemsg import u
from flask_babel import lazy_gettext as _
from werkzeug.exceptions import HTTPException

metrics = ns(
    members=ns(
        text=_("Members"),
        timeaggregation='first',
        description=_(
            "Current cooperative members at the start of a given date.\n\n"
            "Members are taken from our current ERP data, so the following considerations apply:\n"
            "- Membership during the first months of the cooperative was stored in spreadsheets and is not included yet.\n"
            "- There is no historical record of member addresses. "
            "So, if a member has changed her home from Vigo to Cartagena, "
            "it counts as she has been been living all the time in Cartagena.\n"
            "- Only a single start date can be stored so, canceled and later renewed memberships are not properly recorded.\n"
        ),
    ),
    newmembers=ns(
        text=_("New members"),
        timeaggregation='sum',
        description=_(
            "New cooperative members during the month before a given date.\n\n"
            "Considerations for \"Members\" metric also apply in this one.\n"
        ),
    ),
    canceledmembers=ns(
        text=_("Canceled members"),
        timeaggregation='sum',
        description=_(
            "Members leaving the cooperative during in the month before a given date.\n\n"
            "Considerations for \"Members\" metric also apply in this one.\n"
        ),
    ),
    contracts=ns(
        text=_("Contracts"),
        timeaggregation='first',
        description=_(
            "Current active contracts at the start of a given date.\n\n"
            "Contract data is taken from activation and deactivation dates from ATR system.\n"
            "Old contracts were copied by hand from ATR files and may be less reliable.\n"
        ),
    ),
    newcontracts=ns(
        text=_("New contracts"),
        timeaggregation='sum',
        description=_(
            "Contracts starting during in the month before a given date.\n\n"
            "Considerations for \"Contracts\" metric also apply in this one.\n"
        ),
    ),
    canceledcontracts=ns(
        text=_("Canceled contracts"),
        timeaggregation='sum',
        description=_(
            "Contracts ending during in the month before a given date.\n\n"
            "Considerations for \"Contracts\" metric also apply in this one.\n"
        ),
    ),
)

aggregation_levels = [
    ('countries', 'country', 'codi_pais', 'pais'),
    ('ccaas', 'ccaa', 'codi_ccaa', 'comunitat_autonoma'),
    ('states', 'state', 'codi_provincia', 'provincia'),
    ('cities', 'city', 'codi_ine', 'municipi'),
    ]

geolevels = ns([
    ('world', ns(
        text = _('World'),
        mapable = False,
    )),
    ('country', ns(
        text = _('Country'),
        plural = 'countries',
        parent = 'world',
        mapable = False,
    )),
    ('ccaa', ns(
        text = _('CCAA'),
        plural = 'ccaas',
        parent = 'country',
    )),
    ('state', ns(
        text = _('State'),
        plural = 'states',
        parent = 'ccaa',
    )),
    ('city', ns(
        text = _('City'),
        plural = 'cities',
        parent = 'state',
        mapable = False,
    )),
    ('localgroup', ns(
        text = _('Local Group'),
        plural = 'localgroups',
        parent = 'world',
        detailed = False,
        mapable = False,
    )),
])

def previousFirstOfMonth(date):
    return str(Date(date).replace(day=1))

def getDates(first, last):
    first = Date(first or Date.today())
    return first, Date(last or first)


def dateSequenceMonths(first, last):
    first, last = getDates(first, last)
    if first.day != 1:
        first = first.replace(day=1)
    interval = delta(last, first)
    months = interval.months + interval.years * 12 + 1
    return [
        first + delta(months=n)
        for n in range(0, months)
    ]

def dateSequenceWeeks(first, last):
    first, last = getDates(first, last)
    if first.isoweekday() != 1:
        first = Date(first - timedelta(days=first.isoweekday()-1%7))
    weeks = (last - first).days // 7 + 1
    return [
        Date(first + delta(weeks=n))
        for n in range(0, weeks)
    ]

def dateSequenceWeeksMonths(first, last):
    m = dateSequenceMonths(first, last)
    w = dateSequenceWeeks(first, last)
    return set(m + w)



def dateSequenceYears(first, last):
    first, last = getDates(first, last)
    if first.day != 1 or first.month != 1:
        first = first.replace(day=1, month=1)
    years = (last - first).days // 365 + 1
    return [
        Date(first + delta(years=n))
        for n in range(0, years)
    ]

def caseFrequency(frequency):
    if frequency == 'weekly':
        return dateSequenceWeeks
    elif frequency == 'monthly':
        return dateSequenceMonths
    else:
        return dateSequenceYears


def requestDates(first=None, last=None, on=None, since=None, to=None, periodicity=None):
    """
    Returns a list of dates to be requested given the query parameters.
    @param periodicity: 'weekly', 'monthly', 'yearly' or None if single date
    @param first: First date in available history
    @param last: Last date in available history
    @param on: Single date to be retrieved or none if 
    @param since: Earlier date to be retrieved or none if first
    @param to: Later date to be retrieved or none if last
    """
    if periodicity:
        since = since or first
        to = to or last or str(Date.today())
        all_dates = caseFrequency(periodicity)(since, to)
        return [str(date) for date in all_dates]

    if on:
        return [previousFirstOfMonth(on)]

    return [last or str(Date.today())]



def relative(path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), path))


def readQuery(query):
    with open(relative(query + '.sql'), 'r') as queryfile:
        return queryfile.read().rstrip()

def tsv_response(f):
    @wraps(f)
    def wrapper(*args, **kwd):
        filename, result = f(*args, **kwd)

        if type(result) is Response:
            return result
        if type(result) in (type(b''), type(u'')):
            response = make_response(result)
            response.mimetype='text/tab-separated-values'
            response.headers["Content-Disposition"] = "filename={}".format(filename or 'file.tsv')
            return response

        response = make_response('\n'.join(
            '\t'.join(
                u(x)
                    .replace('\t',' ')
                    .replace('\n',' ')
                for x in line)
            for line in result
        ))
        response.mimetype='text/tab-separated-values'
        response.charset='utf-8'
        response.headers["Content-Disposition"] = "attachment; filename=myplot.tsv"
        return response
    return wrapper


def yaml_response(f):
    @wraps(f)
    def wrapper(*args, **kwd):
        result = f(*args, **kwd)

        if type(result) is Response:
            return result

        response = make_response(ns(result).dump())
        response.mimetype = 'application/yaml'
        return response
    return wrapper


class IsoDateConverter(BaseConverter):

    def to_python(self, value):
        try:
            return Date(value)
        except ValueError:
            raise ValidationError(value)

    def to_url(self, value):
        return str(value)

# Errors

class MissingDateError(HTTPException):

    missingDates = []
    code = 500

    def __init__(self, missingDates):
        super(MissingDateError, self).__init__("Missing Dates " + u(missingDates))
        self.missingDates = missingDates


class ValidateError(HTTPException):
    from . import common
    valors = ns(
        # TODO: Construct this from source metadata
        metric=list(metrics),
        frequency=['monthly', 'yearly'],
        geolevel=['country', 'ccaa', 'state', 'city']
        )

    code = 400

    parameter = ''
    value = ''
    possibleValues = []

    def __init__(self, field, value):
        self.parameter = field
        self.value = value
        self.possibleValues = self.valors[field]
        super(ValidateError, self).__init__(
            "Incorrect {} '{}' try with {}".format(
                field, value, u(self.possibleValues))
            )

class AliasNotFoundError(HTTPException):
    code = 400
    def __init__(self, alias, value):
        super(AliasNotFoundError, self).__init__(
            "{} '{}' not found".format(alias, value))


# None i world son valors por defecto de los parametros
allowedParamsValues = ns(
    metric=list(metrics),
    frequency=['monthly', 'yearly', None],
    geolevel=[k for k,v in geolevels.items() if v.get('aggregation', True) ],
    relativemetric=['population', None],
)

def validateParams(**params):
    for field, value in params.items():
        if value in allowedParamsValues[field]:
            continue
        raise ValidateError(field, value)

mapAllowedValues = ns(
    metric=list(metrics),
    frequency=['monthly', 'yearly', None],
    geolevel=[k for k,v in geolevels.items() if v.get('mapable', True) ],
    relativemetric=['population', None],
)


class ValidateImplementationMap(ValidateError):
    def __init__(self, field, value):
        self.parameter = field
        self.value = value
        self.possibleValues = mapAllowedValues[field]
        super(ValidateError, self).__init__(
            u"Not implemented {} '{}' try with {}"
            .format(field, value, self.possibleValues))

def validateImplementation(**params):
    for field, value in params.items():
        if value in mapAllowedValues[field]:
            continue
        raise ValidateImplementationMap(field=field, value=value)


def register_converters(app):
    app.url_map.converters['isodate'] = IsoDateConverter

@yaml_response
def handle_request_not_found(e):
    response = make_response('Request not found!', 404)
    response.mimetype = 'application/yaml'
    return response


@yaml_response
def handle_bad_request(self):
    if current_app.errors == None:
        response =  make_response('Bad Request', 400)
    else:
        # TODO: Which use case is this addressing? Why catalan?
        response = make_response(
            '\'{}\' no existeix/en'.format(', '.join([str(x) for x in current_app.errors])), 400
        )
        current_app.errors = None
    response.mimetype = 'application/yaml'
    return response

@yaml_response
def handle_customErrorValidation(error):
    return make_response(
        jsonify(ns(message=error.description,
            parameter=error.parameter,
            valueRequest=error.value,
            possibleValues=error.possibleValues
            )), error.code
    )

@yaml_response
def handle_missingDatesError(error):
    return make_response(
        jsonify(ns(message=error.description)), error.code
    )

@yaml_response
def handle_aliasNotFoundError(error):
    return make_response(
        jsonify(ns(message=error.description)), error.code
    )

def register_handlers(app):
    app.register_error_handler(404, handle_request_not_found)
    app.register_error_handler(400, handle_bad_request)
    app.register_error_handler(MissingDateError, handle_missingDatesError)
    app.register_error_handler(ValidateError, handle_customErrorValidation)
    app.register_error_handler(AliasNotFoundError, handle_aliasNotFoundError)

def enable_cors(app):
    # In production and testing servers, CORS is managed by the server,
    # Call this just for development server
    from flask_cors import CORS
    CORS(app, resources={
        r'/*': dict(
            origins = '*',
            supports_credentials = True, # Send cookies, requires no '*' origin
            send_wildcard = False, # So, instead of '*' copy 'Origin' from request header
        )})



# vim: et ts=4 sw=4
