# -*- coding: utf-8 -*-
from yamlns import namespace as ns
from yamlns.dateutils import Date as isoDate



def parse_tsv(tsv_data):
    """
        Parses a TSV file content into a header and a list of tuples.
        Ignores empty lines.
    """
    return [
        [item.strip() for item in line.split('\t')]
        for line in tsv_data.split('\n')
        if line.strip()
        ]

def tuples2objects(tuples):
    """
        Turns a list of tuples including the first one with the column names,
        into a list of entries (ns objects) having the colunm names as
        attribute names.
    """
    headers = tuples[0]
    data = tuples[1:]
    return [
        ns([
            (header, value)
            for header, value in zip(headers, item)
            ])
        for item in data
        ]


def state_dates(entry):
    """
        Returns the dates included in the entry
    """
    return [
        isoDate(k[len('count_'):].replace('_', ''))
        for k in entry.keys()
        if k.startswith('count_')
        ]


def aggregate(entries):
    """
        Aggregates a list of entries by geographical scopes:
        Country, CCAA, state, city.
    """

    entry = entries[0]
    dates = state_dates(entry)

    result = ns (
        dates = dates,
         level = 'countries',
         countries = ns()
    )

    for entry in entries:

        count = [
            int(entry['count_'+date.isoDate.replace('-','_')])
            for date in dates ]

        country = result.countries.setdefault(
            entry.codi_pais, ns(
                name=entry.pais,
                data=[0]*len(dates),
                ccaas=ns(),
            )
        )
        country.data = [a+b for a,b in zip(country.data, count)]

        ccaa = country.ccaas.setdefault(
            entry.codi_ccaa, ns(
                name=entry.comunitat_autonoma,
                data=[0]*len(dates),
                states=ns(),
            )
        )
        ccaa.data = [a+b for a,b in zip(ccaa.data, count)]

        provincia = ccaa.states.setdefault(
            entry.codi_provincia, ns(
                name=entry.provincia,
                data=[0]*len(dates),
                cities=ns(),
            )
        )
        provincia.data = [a+b for a,b in zip(provincia.data, count)]

        city = provincia.cities.setdefault(
            entry.codi_ine, ns(
                name=entry.municipi,
                data=count,
            )
        )

    return result






import copy             

def idem(tipus, elemA, elemB):
     return elemA[tipus] == elemB[tipus]


def eliminar(item, l):
    return list(
        filter(lambda e: not idem('codi_ine',item,e), l)
        )

def escollirINES(l):
    llista = []
    lTractar = copy.deepcopy(l)
    for item in lTractar:
        if not contains(item,llista):
            if esUnic(item,l):                              
                llista.append(item)
            else:
                itemAgregat = agregar(item,l)
                eliminar(item,lTractar)
                llista.append(itemAgregat)
    return llista


def esUnic(item, l):
    count = 0
    for e in l:
        if count == 0 and idem('codi_ine',item,e):
            count += 1
        elif count == 1 and idem('codi_ine',item,e):
            return False
    return True


def agregar(item, l):
    newItem = copy.deepcopy(item)
    newItem.quants = 0
    for e in l:
        if idem('codi_ine',item,e):
            newItem.quants += int(e.quants)
    return newItem


def contains(item, l):
    for e in l:
        if idem('codi_ine',item,e):
            return True
    return False




def packageCountries(l):
    d = ns()
    for e in l:
        if not e.codi_pais in d:
            d[e.codi_pais] = ns()
    return d


def packageCCAA(l, d):
    for e in l:
        if not e.codi_ccaa in d[e.codi_pais]:
            d[e.codi_pais][e.codi_ccaa] = ns()
    return d


def packageStates(l, d):
    for e in l:
        if not e.codi_provincia in d[e.codi_pais][e.codi_ccaa]:
            d[e.codi_pais][e.codi_ccaa][e.codi_provincia] = ns()
    return d


def packageCities(l, d):
    for e in l:
        if not e.codi_ine in d[e.codi_pais][e.codi_ccaa][e.codi_provincia]:
            d[e.codi_pais][e.codi_ccaa][e.codi_provincia][e.codi_ine] = e
    return d


def select_only_city(input, ine):
    r = tuples2objects(parse_tsv(input))
    return [item for item in r if item.codi_ine == ine]




# vim: et sw=4 ts=4
