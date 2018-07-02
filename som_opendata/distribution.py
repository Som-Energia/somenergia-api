# -*- coding: utf-8 -*-
from yamlns import namespace as ns
from yamlns.dateutils import Date as isoDate



def parse_tsv(tsv_data):
    return [
        [item.strip() for item in line.split('\t')]
        for line in tsv_data.split('\n')
        if line.strip()
        ]


def tuples2objects(tuples):
    headers = tuples[0]
    data = tuples[1:]
    return [
        ns([
            (header, value)
            for header, value in zip(headers, item)
            ])
        for item in data
        ]


def state_dates(input):

    return [
            isoDate(k[len('quants_'):])
            for k in input.keys()
            if k.startswith('quants_')
           ]


def aggregate(input):

    linia = input[0]
    dates = state_dates(linia)

    

    result = ns (
        dates = dates,
         level = 'countries',
         countries = ns()
    )

    for linia in input:

        linia.quants = [ int(linia['quants_'+date.compact])
                    for date in dates
               ]
        
        result.countries.update({
                    linia.codi_pais:ns(
                        name=linia.pais,
                        data=linia.quants[:],
                        ccaas=ns()
                            )}
                        )

        country = result.countries[linia.codi_pais]
        #ccaa = country.ccaas[linia.codi_ccaa]

        '''
        country = linia.codi_pais:ns(
            name=linia.pais,
            data=linia.quants[:],
            ccaas=ns()
        )
        '''


        ccaa = country.ccaas.setdefault(linia.codi_ccaa, ns(
                name=linia.comunitat_autonoma,
                data=linia.quants[:],
                states=ns()
            )
        )

        


        provincia = ccaa.states.setdefault(linia.codi_provincia, ns(
                name=linia.provincia,
                data=linia.quants[:],
                cities=ns()
            )
        )
        

        city = provincia.cities.setdefault(linia.codi_ine, ns(
            name=linia.municipi,
            data=linia.quants[:]
        ))

        

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
