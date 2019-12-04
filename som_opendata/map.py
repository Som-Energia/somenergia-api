from yamlns import namespace as ns
from .scale import LinearScale, LogScale
from .colorscale import Gradient
from .distribution import aggregate
from pathlib import Path

months = (
        "Enero Febrero Marzo Abril Mayo Junio "
        "Julio Agosto Septiembre Octubre Noviembre Diciembre"
        ).split()

def percentRegion(value, total):
    if not total:
        return '0,0%'
    return '{:.1f}%'.format(value * 100. / total).replace('.',',')

def dataToTemplateDict(data, colors, titol, subtitol, colorScale='Log', locations=[]):
    date = data.dates[0]
    result = ns(
            titol = titol,
            subtitol = subtitol,
            year = date.year,
            month = months[date.month-1],
        )

    scales = dict(
        Linear = LinearScale,
        Log = LogScale,
    )
    totalValue = data["values"][0]

    scale = scales[colorScale](higher=totalValue or 1)

    for code, ccaa in data.countries.ES.ccaas.items():
        value = ccaa["values"][0]
        result.update({
            'number_' + code: value,
            'percent_' + code: percentRegion(value, totalValue),
            'color_' + code: colors(scale(value)),
            })
    restWorld = data["values"][0] - data.countries.ES["values"][0]
    result.update({
        'number_00': restWorld,
        'percent_00': percentRegion(restWorld,totalValue),
        })

    for code in locations:
        if not result.get('number_{}'.format(code)):
            result.update({
            'number_' + code: 0,
            'percent_' + code: percentRegion(0, totalValue),
            'color_' + code: colors(scale(0)),
                })
    return result


def fillMap(data, template, gradient, title, subtitle='', scale='Log', locations=[]):

    dataDict = dataToTemplateDict(
        data=data, colors=gradient,
        colorScale=scale, titol=title, subtitol=subtitle, locations=locations
    )

    return template.format(**dataDict)

def renderMap(source, metric, date):
    geolevel = 'ccaa'
    filtered_objects = source.get(metric, [date], [])
    data = aggregate(filtered_objects, geolevel)
    template = Path('ccaaMap.svg').read_text(encoding='utf8')
    gradient = Gradient('#e0ecbb','#384413')
    return fillMap(data=data, template=template, gradient=gradient, title=metric)


# map{Country}{ES}by{States}.svg
# map{Province}{01}by{Counties}.svg

# map.templateName(scope, code, subscope)
# map.subdivisions(scope, code, subscope)
