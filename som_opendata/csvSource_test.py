# -*- coding: utf-8 -*-
import b2btest
import unittest
from yamlns.dateutils import Date as isoDate
from yamlns import namespace as ns
from csvSource import CsvSource
from missingDataError import MissingDataError



headers = u"codi_pais\tpais\tcodi_ccaa\tcomunitat_autonoma\tcodi_provincia\tprovincia\tcodi_ine\tmunicipi\tcount_2018_01_01"
data_Adra = u"ES\tEspaña\t01\tAndalucía\t04\tAlmería\t04003\tAdra\t2"
data_Perignan = u"FR\tFrance\t76\tOccità\t66\tPyrénées-Orientales\t66136\tPerpignan\t10"
data_Girona = u"ES\tEspaña\t09\tCatalunya\t17\tGirona\t17079\tGirona\t20"
data_SantJoan = u"ES\tEspaña\t09\tCatalunya\t08\tBarcelona\t08217\tSant Joan Despí\t1000"
data_Amer = u"ES\tEspaña\t09\tCatalunya\t17\tGirona\t17007\tAmer\t2000"



class CsvSource_Test(unittest.TestCase):

    from testutils import assertNsEqual

    def setUp(self):
        self.maxDiff=None

    def createSource(self, datums):

        content = ns()
        for datum, lines in datums.iteritems():
            content[datum] = '\n'.join(lines)

        return CsvSource(content)

    def raisesAssertion(self, source, request, expected, missedDates, missedLocations):
        with self.assertRaises(MissingDataError) as ctx:
            source.get(*request)

        self.assertNsEqual(ns(data=ctx.exception.data), expected)
        self. assertEquals(ctx.exception.missedDates, missedDates)
        self. assertEquals(ctx.exception.missedLocations, missedLocations)


    def test__get__oneDateRequestExist(self):
        source = self.createSource(
            ns(members=[headers,
            data_SantJoan])
            )
        self.assertNsEqual(
            ns(data=source.get('members', ['2018-01-01'], ns())), """\
            data:
            - codi_pais: ES
              pais: 'España'
              codi_ccaa: '09'
              comunitat_autonoma: Catalunya
              codi_provincia: '08'
              provincia: Barcelona
              codi_ine: '08217'
              municipi: Sant Joan Despí
              count_2018_01_01: '1000'
        """)

    def test__get__oneDateRequestNoExist(self):
        source = self.createSource(
            ns(members=[headers,
            data_SantJoan])
            )
        self.raisesAssertion(
            source=source,
            request=['members', ['2018-02-01'], ns()],
            expected=ns(data=[]),
            missedDates=['2018-02-01'],
            missedLocations=None
            )

    def test__get__twoDatesRequestOneExist(self):
        source = self.createSource(
            ns(members=[headers,
            data_SantJoan])
            )
        self.raisesAssertion(
            source=source,
            request=['members', ['2018-01-01','2018-02-01'], ns()],
            expected='''
                data:
                - codi_pais: ES
                  pais: 'España'
                  codi_ccaa: '09'
                  comunitat_autonoma: Catalunya
                  codi_provincia: '08'
                  provincia: Barcelona
                  codi_ine: '08217'
                  municipi: Sant Joan Despí
                  count_2018_01_01: '1000'
                  ''',
            missedDates=['2018-02-01'],
            missedLocations=None
            )

    def test__get__filterNoExist(self):
        source = self.createSource(
            ns(members=[headers,
            data_SantJoan])
            )
        self.raisesAssertion(
            source=source,
            request=['members', ['2018-01-01'], ns(codi_ccaa=['05'])],
            expected=ns(data=[]),
            missedDates=None,
            missedLocations=None
            )

    def test__get__filterExist(self):
        source = self.createSource(
            ns(members=[headers,
            data_SantJoan])
            )
        self.assertNsEqual(
            ns(data=source.get('members', ['2018-01-01'], ns(codi_pais=['ES']))), """\
            data:
            - codi_pais: ES
              pais: 'España'
              codi_ccaa: '09'
              comunitat_autonoma: Catalunya
              codi_provincia: '08'
              provincia: Barcelona
              codi_ine: '08217'
              municipi: Sant Joan Despí
              count_2018_01_01: '1000'
        """)


    def test__set__oneDate(self):
        source = self.createSource(
            ns(members=[headers,
            data_SantJoan])
            )
        source.set('members',
            [ns(codi_pais=u'ES',
                pais=u'España',
                codi_ccaa=u'09',
                comunitat_autonoma=u'Catalunya',
                codi_provincia=u'08',
                provincia=u'Barcelona',
                codi_ine=u'08217',
                municipi=u'Sant Joan Despí',
                count_2018_01_01=u'1000',
                count_2018_02_01=u'201')]
        )
        self.assertEqual(source.data['members'],
            u'''codi_pais\tpais\tcodi_ccaa\tcomunitat_autonoma\tcodi_provincia\tprovincia\tcodi_ine\tmunicipi\tcount_2018_01_01\tcount_2018_02_01\n''' +
            u'''ES\tEspaña\t09\tCatalunya\t08\tBarcelona\t08217\tSant Joan Despí\t1000\t201'''
        )
