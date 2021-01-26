# coding=utf-8
import psycopg2
import dbconfig as config
from dbutils import csvTable
from yamlns import namespace as ns
from yamlns.dateutils import Date
from .common import readQuery

"""
This module contains functions to compute metrics.
Metrics have to be computed aggregated by city and month.
"""


def activeContractsCounter(adate):
    # TODO: Unsafe substitution, use mogrify
    return """
    count(CASE
        WHEN polissa.data_alta IS NULL THEN NULL
        WHEN polissa.data_alta > '{adate}'::date THEN NULL
        WHEN polissa.data_baixa is NULL then TRUE
        WHEN polissa.data_baixa > '{adate}'::date THEN TRUE
        ELSE NULL
        END) AS count_{adate:%Y_%m_%d}
""".format(adate=adate)

def activeContractsLister(adate):
    """Debug substitute for activeContractsCounter
    List ids instead of count them
    """
    # TODO: Unsafe substitution, use mogrify
    return """
    string_agg(CASE
        WHEN polissa.data_alta IS NULL THEN NULL
        WHEN polissa.data_alta > '{adate}'::date THEN NULL
        WHEN polissa.data_baixa is NULL then polissa.id::text
        WHEN polissa.data_baixa > '{adate}'::date THEN polissa.id::text
        ELSE NULL
        END, ',' ORDER BY polissa.id) AS ids_{adate:%Y_%m_%d}
""".format(adate=adate)

def newContractsCounter(adate):
    # TODO: Unsafe substitution, use mogrify
    return """
    count(CASE
        WHEN polissa.data_alta IS NULL THEN NULL
        WHEN polissa.data_alta > '{adate}'::date THEN NULL
        WHEN polissa.data_alta <= '{adate}'::date - INTERVAL '1 month' THEN NULL
        ELSE TRUE
        END) AS count_{adate:%Y_%m_%d}
""".format(adate=adate)

def newContractsLister(adate):
    # TODO: Unsafe substitution, use mogrify
    return """
    string_agg(CASE
        WHEN polissa.data_alta IS NULL THEN NULL
        WHEN polissa.data_alta > '{adate}'::date THEN NULL
        WHEN polissa.data_alta <= '{adate}'::date - INTERVAL '1 month' THEN NULL
        ELSE polissa.id::text
        END, ',' ORDER BY polissa.id) AS count_{adate:%Y_%m_%d}
""".format(adate=adate)

def canceledContractsCounter(adate):
    # TODO: Unsafe substitution, use mogrify
    return """
    count(CASE
        WHEN polissa.data_baixa is NULL then NULL
        WHEN polissa.data_baixa > '{adate}'::date THEN NULL
        WHEN polissa.data_baixa <= '{adate}'::date - INTERVAL '1 month' THEN NULL
        ELSE TRUE
        END) AS count_{adate:%Y_%m_%d}
""".format(adate=adate)

def canceledContractsLister(adate):
    # TODO: Unsafe substitution, use mogrify
    return """
    string_agg(CASE
        WHEN polissa.data_baixa is NULL then NULL
        WHEN polissa.data_baixa > '{adate}'::date THEN NULL
        WHEN polissa.data_baixa <= '{adate}'::date - INTERVAL '1 month' THEN NULL
        ELSE polissa.id::text
        END, ',' ORDER BY polissa.id) AS count_{adate:%Y_%m_%d}
""".format(adate=adate)


def contractsSparse(dates):
    db = psycopg2.connect(**config.psycopg)
    query = readQuery('contract_distribution_sparse')
    with db.cursor() as cursor :
        cursor.execute(query, dict(dates=[
            [Date(adate) for adate in dates]
        ]))
        return csvTable(cursor)

def contractsSeries(dates):
    db = psycopg2.connect(**config.psycopg)
    query = readQuery('contract_distribution')
    query = query.format(','.join(
        activeContractsCounter(Date(adate))
        for adate in dates
        ))
    with db.cursor() as cursor :
        cursor.execute(query)
        return csvTable(cursor)

def newContractsSeries(dates, dbhandler=csvTable, debug=False):
    db = psycopg2.connect(**config.psycopg)
    query = readQuery('contract_distribution')
    query = query.format(','.join(
        newContractsCounter(Date(adate))
        for adate in dates
        ))
    with db.cursor() as cursor :
        cursor.execute(query)
        return dbhandler(cursor)


def canceledContractsSeries(dates, dbhandler=csvTable, debug=False):
    db = psycopg2.connect(**config.psycopg)
    query = readQuery('contract_distribution')
    query = query.format(','.join(
        canceledContractsCounter(Date(adate))
        for adate in dates
        ))
    with db.cursor() as cursor :
        cursor.execute(query)
        return dbhandler(cursor)


def activeMembersCounter(adate):
    # TODO: Unsafe substitution, use mogrify
    return """
    count(CASE
        WHEN create_date IS NULL THEN NULL
        WHEN create_date > '{adate}'::date THEN NULL
        WHEN data_baixa_soci < '{adate}'::date THEN NULL
        WHEN create_date <= '{adate}'::date THEN TRUE
        WHEN active THEN TRUE
        ELSE NULL
            END) AS count_{adate:%Y_%m_%d}
        """.format(adate=adate)

def activeMembersLister(adate):
    # TODO: Unsafe substitution, use mogrify
    return """
    string_agg(CASE
        WHEN create_date IS NULL THEN NULL
        WHEN create_date > '{adate}'::date THEN NULL
        WHEN data_baixa_soci < '{adate}'::date THEN NULL
        WHEN create_date <= '{adate}'::date THEN soci_id::text
        WHEN active THEN soci_id::text
        ELSE NULL
        END, ',' ORDER BY soci_id) AS count_{adate:%Y_%m_%d}
        """.format(adate=adate)

def newMembersCounter(adate):
    # TODO: Unsafe substitution
    return """
    count(CASE
        WHEN create_date IS NULL THEN NULL
        WHEN create_date > '{adate}'::date THEN NULL
        WHEN create_date <= '{adate}'::date - INTERVAL '1 month' THEN NULL
        ELSE TRUE
            END) AS count_{adate:%Y_%m_%d}
        """.format(adate=adate)

def newMembersLister(adate):
    # TODO: Unsafe substitution
    return """
    string_agg(CASE
        WHEN create_date IS NULL THEN NULL
        WHEN create_date > '{adate}'::date THEN NULL
        WHEN create_date <= '{adate}'::date - INTERVAL '1 month' THEN NULL
        ELSE soci_id::text
            END, ',' ORDER BY soci_id) AS count_{adate:%Y_%m_%d}
        """.format(adate=adate)


def cancelledMembersCounter(adate):
    # TODO: Unsafe substitution
    return """
    count(CASE
        WHEN data_baixa_soci IS NULL THEN NULL
        WHEN data_baixa_soci > '{adate}'::date THEN NULL
        WHEN data_baixa_soci <= '{adate}'::date - INTERVAL '1 month' THEN NULL
        ELSE TRUE
            END) AS count_{adate:%Y_%m_%d}
        """.format(adate=adate)

def cancelledMembersLister(adate):
    # TODO: Unsafe substitution
    return """
    string_agg(CASE
        WHEN data_baixa_soci IS NULL THEN NULL
        WHEN data_baixa_soci > '{adate}'::date THEN NULL
        WHEN data_baixa_soci <= '{adate}'::date - INTERVAL '1 month' THEN NULL
        ELSE soci_id::text
            END, ',' ORDER BY soci_id) AS count_{adate:%Y_%m_%d}
        """.format(adate=adate)


def membersSparse(dates, dbhandler=csvTable, debug=False):
    db = psycopg2.connect(**config.psycopg)
    query = readQuery('members_distribution')
    query = query.format(','.join(
        activeMembersCounter(Date(adate))
        for adate in dates
        ))
    with db.cursor() as cursor :
        cursor.execute(query)
        return dbhandler(cursor)

def newMembersSeries(dates, dbhandler=csvTable, debug=False):
    db = psycopg2.connect(**config.psycopg)
    query = readQuery('members_distribution')
    query = query.format(','.join(
        newMembersCounter(Date(adate))
        for adate in dates
        ))
    with db.cursor() as cursor :
        cursor.execute(query)
        return dbhandler(cursor)


def canceledMembersSeries(dates, dbhandler=csvTable, debug=False):
    db = psycopg2.connect(**config.psycopg)
    query = readQuery('members_distribution')
    query = query.format(','.join(
        cancelledMembersCounter(Date(adate))
        for adate in dates
        ))
    with db.cursor() as cursor :
        cursor.execute(query)
        return dbhandler(cursor)



# vim: et sw=4 ts=4