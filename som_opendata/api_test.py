# -*- encoding: utf-8 -*-
import unittest
from dateutil.relativedelta import relativedelta as delta
from yamlns.dateutils import Date
from yamlns import namespace as ns
import b2btest
from .api import api, validateInputDates
from flask import Flask
from .common import (
    register_converters,
    register_handlers,
    )

from .csvSource import loadCsvSource
source = loadCsvSource()

headers = u"codi_pais\tpais\tcodi_ccaa\tcomunitat_autonoma\tcodi_provincia\tprovincia\tcodi_ine\tmunicipi\tcount_2018_01_01"
data_Adra = u"ES\tEspaña\t01\tAndalucía\t04\tAlmería\t04003\tAdra\t2"
data_Perignan = u"FR\tFrance\t76\tOccità\t66\tPyrénées-Orientales\t66136\tPerpignan\t10"
data_Girona = u"ES\tEspaña\t09\tCatalunya\t17\tGirona\t17079\tGirona\t20"
data_SantJoan = u"ES\tEspaña\t09\tCatalunya\t08\tBarcelona\t08217\tSant Joan Despí\t1000"
data_Amer = u"ES\tEspaña\t09\tCatalunya\t17\tGirona\t17007\tAmer\t2000"



class ApiHelpers_Test(unittest.TestCase):

    def test__validateInputDates__since_toDate(self):
        r = validateInputDates(since='2018-01-01', todate='2018-01-02')
        self.assertEqual(r, True)

    def test__validateInputDates__since(self):
        r = validateInputDates(since='2018-01-01')
        self.assertEqual(r, True)

    def test__validateInputDates__since_toDate_turnedDates(self):
        r = validateInputDates(since='2010-01-01', todate='2018-01-01')
        self.assertEqual(r, True)

    def test__validateInputDates__onDate(self):
        r = validateInputDates(ondate='2010-01-01')
        self.assertEqual(r, True)

    def test__validateInputDates__onDate_since(self):
        r = validateInputDates(ondate='2010-01-01', since='2018-01-01')
        self.assertEqual(r, False)

    def test__validateInputDates__onDate_toDate(self):
        r = validateInputDates(ondate='2010-01-01', todate='2018-01-01')
        self.assertEqual(r, False)


class Api_Test(unittest.TestCase):

    @staticmethod
    def setUpClass():
        Api_Test.maxDiff=100000
        Api_Test.app = app = Flask(__name__)
        register_converters(app)
        register_handlers(app)
        app.register_blueprint(api, url_prefix='')
        app.config['TESTING']=True

    def setUp(self):
        self.client = self.app.test_client()
        self.b2bdatapath = 'b2bdata'
        self.oldsource = api.source
        api.source = source
        api.firstDate = '2010-01-01'

    def tearDown(self):
        api.source = self.oldsource

    def get(self, uri, *args, **kwds):
        return self.client.get(uri,*args,**kwds)

    from .testutils import assertNsEqual

    def assertYamlResponse(self, response, expected):
        self.assertNsEqual(response.data, expected)

    def assertTsvResponse(self, response):
        self.assertB2BEqual(response.data)


    def test__version(self):
        r = self.get('/version')
        self.assertYamlResponse(r, """\
            version: '0.2.2'
            compat: '0.2.1'
            """)


    def test__onDate__exists(self):
        r = self.get('/members/on/2018-01-01')
        self.assertTsvResponse(r)

    def test__onDate_aggregateLevel__exist(self):
        r = self.get('/members/by/world/on/2018-01-01')
        self.assertEqual(r.status, '200 OK')    # En cas de ser NO OK petaria en el següent assert
        self.assertTsvResponse(r)

    @unittest.skip('NOT IMPLEMENTED YET')
    def test__aggregateLevel__existToday(self):
        self.setupSource(
            headers+'\tcount_'+str(Date.today()).replace('-','_'),
            data_Adra+'\t123',
            )
        r = self.get('/members/by/city')
        self.assertEqual(r.status, '200 OK')    # En cas de ser NO OK petaria en el següent assert
        self.assertYamlResponse(r, """\
            dates: ["""+str(Date.today())+"""]
            values: [123]
            countries:
              ES:
                name: España
                values: [123]
                ccaas:
                  '01':
                    name: Andalucía
                    values: [123]
                    states:
                      '04':
                        name: Almería
                        values: [123]
                        cities:
                          '04003':
                            name: Adra
                            values: [123]
            """)

    @unittest.skip('NOT IMPLEMENTED YET')
    def test__basicUrl__exist(self):
        self.setupSource(
            headers+'\tcount_'+str(Date.today()).replace('-','_'),
            data_Adra+'\t123',
            )
        r = self.get('/members')
        self.assertEqual(r.status, '200 OK')    # En cas de ser NO OK petaria en el següent assert
        self.assertYamlResponse(r, """\
            dates: ["""+str(Date.today())+"""]
            values: [123]
            """)

    def test__aggregateLevel_frequency__exist(self):
        r = self.get('/members/by/country/yearly')
        self.assertEqual(r.status, '200 OK')    # En cas de ser NO OK petaria en el següent assert
        self.assertTsvResponse(r)

    def test__aggregateLevel_frequency_fromDate__exist(self):
        r = self.get('/members/by/world/yearly/from/2017-01-01')
        self.assertEqual(r.status, '200 OK')    # En cas de ser NO OK petaria en el següent assert
        self.assertTsvResponse(r)

    def test__aggregateLevel_frequency_fromDate_toDate__exist(self):
        r = self.get('/members/by/world/monthly/from/2018-01-01/to/2018-03-01')
        self.assertEqual(r.status, '200 OK')    # En cas de ser NO OK petaria en el següent assert
        self.assertTsvResponse(r)

    def test__aggregateLevel_frequency_toDate__exist(self):
        api.firstDate = '2018-02-01'
        r = self.get('/members/by/world/monthly/to/2018-03-01')
        self.assertEqual(r.status, '200 OK')    # En cas de ser NO OK petaria en el següent assert
        self.assertTsvResponse(r)

    @unittest.skip('NOT IMPLEMENTED YET')
    def test__frequency_formDate__exist(self):
        self.setupSource(
            headers+'\tcount_'+str(Date.today()-delta(weeks=1)).replace('-','_')+'\tcount_'+str(Date.today()).replace('-','_'),
            data_Adra+'\t123\t1234567',
            )
        r = self.get('/members/weekly/from/'+str(Date.today()-delta(weeks=1)))
        self.assertEqual(r.status, '200 OK')    # En cas de ser NO OK petaria en el següent assert
        self.assertYamlResponse(r, """\
            dates: ["""+str(Date.today()-delta(weeks=1))+""", """+str(Date.today())+"""]
            values: [123, 1234567]
            """)

    def test__frequency_fromDate_toDate__exist(self):
        r = self.get('/members/monthly/from/2018-01-01/to/2018-02-01')
        self.assertEqual(r.status, '200 OK')    # En cas de ser NO OK petaria en el següent assert
        self.assertTsvResponse(r)

    def test__urlBaseFrequency__exist(self):
        r = self.get('/members/yearly')
        self.assertEqual(r.status, '200 OK')    # En cas de ser NO OK petaria en el següent assert
        self.assertTsvResponse(r)

    def test__onDate_aggregateLevel_queryParams__exist(self):
        r = self.get('/members/by/city/on/2018-01-01?city=17007')
        self.assertEqual(r.status, '200 OK')    # En cas de ser NO OK petaria en el següent assert
        self.assertTsvResponse(r)

    def test__urlBase(self):
        r = self.get('/members')
        self.assertTsvResponse(r)

    def test__printerError__datesNotExist(self):
        r = self.get('/members/on/1994-09-01')
        self.assertEqual(r.status_code, 500)
        self.assertYamlResponse(r, """\
            message: Missing Dates ['1994-08-29']
            """)

    def test__printerError__URLparamsNotExist_piolin(self):
        r = self.get('/members/by/piolin')
        self.assertEqual(r.status_code, 400)
        self.assertYamlResponse(r, """\
            metric: geolevel
            valueRequest: piolin
            possibleValues: ['country', 'ccaa', 'state', 'city']
            message: Incorrect geolevel 'piolin' try with ['country', 'ccaa', 'state', 'city']
            """)

    def test__printerError__URLparamsNotExist_frequency(self):
        r = self.get('/members/piolin')
        self.assertEqual(r.status_code, 400)
        self.assertYamlResponse(r, """\
            metric: frequency
            valueRequest: piolin
            possibleValues: ['monthly', 'yearly']
            message: Incorrect frequency 'piolin' try with ['monthly', 'yearly']
            """)

    @unittest.skip("Not implemented yet | Caldria retocar el converter de Date")
    def test__printerError__URLparamsNotExist_date(self):
        r = self.get('/members/on/piolin')
        self.assertEqual(r.status_code, 404)

    def test__printerError__queryParamsNotExist(self):
        r = self.get('/members/by/city/on/2018-01-01?city=9999999')
        self.assertYamlResponse(r, ns())

    def test__printerError__incorrectFormatDates(self):
        r = self.get('/members/by/city/on/2018-01-01/from/2018-02-02')
        self.assertEqual(r.status_code, 404)

    def test__printerError_frequency_toDate__exist_NoExactFirstDate(self):
        r = self.get('/members/monthly/from/2018-03-15/to/2018-04-15')
        self.assertEqual(r.status, '200 OK')    # En cas de ser NO OK petaria en el següent assert
        self.assertTsvResponse(r)

    def test__printerError_incorrectMetric(self):
        r = self.get('/incorrectMetric')
        self.assertEqual(r.status_code, 400)
        self.assertYamlResponse(r, """\
            metric: metric
            valueRequest: incorrectMetric
            possibleValues: ['members', 'contracts']
            message: Incorrect metric 'incorrectMetric' try with ['members', 'contracts']
            """)



# vim: et ts=4 sw=4
