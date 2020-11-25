# somenergia-opendata

[![Build Status](https://travis-ci.org/Som-Energia/somenergia-opendata.svg?branch=master)](https://travis-ci.org/Som-Energia/somenergia-opendata)

Public API to access open data information about the cooperative

- API UI: https://opendata.somenergia.coop/ui/
- API Documentation: https://opendata.somenergia.coop/docs/

## Example queries


### Geographical distributions


- `/contracts`
    All current contracts

- `/members`
    All current members (instead of contracts)

- `/contracts/on/2018-02-03`
    Contracts on a given date

- `/contracts/by/city`
    Current contracts aggregated by city

- `/contracts/by/city/on/2018-02-03`
    Contracts aggregated by city at a given date

- `/contracts/by/city/weekly`
    Contracts aggregated by city every available week

- `/contracts/by/state/monthly`
    Contracts aggregated by state every available month

- `/contracts/by/ccaa/yearly`
    Contracts aggregated by CCAA every available year

- `/contracts/by/city/weekly/from/2018-02-03`
    Contracts aggregated by state every week from a date

- `/contracts/by/city/weekly/from/2018-02-03/to/2018-05-05`
    Contracts aggregated by city every week from a date until a date

- `/contracts/by/city/weekly/to/2018-05-05`
    Contracts aggregated by city every week until a date


#### Using filters


- `/contracts/by/city?city=23423&city=89545`
    Include just cities with INE code 23423 and 89545

- `/contracts/by/city?city=23423&city=89545&ccaa=04`
    Include just cities with INE code 23423 and 89545 and also all cities from CCAA 04 (Catalonia)

- `/contracts/by/city?state=04`
    Include just cities in state 04

#### Response format

TODO

### Maps

- `/map/contracts`
    All current contracts by ccaa

- `/map/contracts?lang=es`
    All current contracts by ccaa in Spanish

- `/map/members`
    All current members by ccaa

- `/map/contracts/on/2018-02-03`
    Contracts on a given date

- `/map/contracts/by/state`
    Current contracts aggregated by state

- `/map/contracts/per/population/by/state`
    Current contracts relatives to population aggregated by state

- `/map/contracts/by/state/on/2018-02-03`
    Contracts aggregated by state at a given date

- `/map/contracts/by/state/monthly`
    Gif animation with contracts by state every available month

- `/map/contracts/by/ccaa/yearly`
    Gif animation with contracts aggregated by CCAA every available year

- `/map/contracts/by/state/monthly/from/2018-02-01`
    Gif animation with contracts aggregated by state every month from a date

- `/map/contracts/by/state/monthly/from/2018-02-03/to/2018-05-01`
    Gif animation with contracts aggregated by state every month from a date until a date

- `/map/contracts/by/state/monthly/to/2018-05-01`
    Gif animation with contracts aggregated by state every month until a date


### Discovery

- `/discover/metrics`
    Shows all suported metrics as a list named `metrics` with
    - `id` the id used to refer the metric
    - `text` the translated text to display users

- `/discover/geolevel`
    Returns a list `geolevels` with the supported geolevels and related info
    - `id` is the id used to refer it (its a mnemonic id)
    - `text` is the translated text to display users
    - `plural` is the pluralization of id used in yaml's as key when many are given
    - `parent` tells which other geolevel fully contains its subdivisions.
    - `detailable: false` tells that a geolevel is not supported as statistics detail level
    - `mapable: false` tells that a geolevel is not supported as map detail level

- `/discover/geolevel/ccaa`
    Returns a list of divisions at the `ccaa` level as a map `options` with id -> text

- `/discover/geolevel/city?localgroup=BaixLlobregat`
    Limits the list of cities to the ones included in the localgroup `BaixLlobregat`

- `/discover/geolevel/localgroup?ccaa=09`
    Lists all the localgroups working on areas covering cities in Catalonia (09)



### Language

Whenever human readable strings are returned,
browser language is used by default (accept-language http header).
Language can be forced by using `lang` query parameter.

If the language is not specified in either form or the one selected is not supported, spanish is chosen.
But that could be changed in the future to english.
So, if you want spanish, please, specify it.

Supported languages are:

- Catalan (ca)
- Spanish (es)
- Euskara (eu)
- Galician (gl)

## Deploy

### Requirements

```bash
sudo apt install libmagickwand-dev inkscape
python setup.py develop
```

### Compile Language Translations

```bash
pybabel compile -f -d som_opendata/translations
```

### Generate documentation

```bash
npm install
npm run docs
```

## External data sources

### Could be used in the future

- For counties (comarques) and city population in Catalonia
        - https://analisi.transparenciacatalunya.cat/Sector-P-blic/Caps-de-municipi-de-Catalunya-georeferenciats/wpyq-we8x
                        - wget https://analisi.transparenciacatalunya.cat/resource/wpyq-we8x.csv -O Caps_de_municipi_de_Catalunya_georeferenciats.csv




