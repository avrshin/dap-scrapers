import requests
import lxml.html
import dl
import messytables
from collections import OrderedDict
import itertools
import orm

"""Value: dsID, region, indID, period, value, source, is_number
   DataSet: dsID, last_updated, last_scraped, name
   Indicator: indID, name, units
   """

NONVIOLENT = ['Headquarters or base established',
              'Non-violent activity by a conflict actor',
              'Non-violent transfer of territory']

dataset = {'dsID': 'acled',
           'name': 'ACLED (Armed conflict location and event dataset)',
           'last_updated': None,
           'last_scraped': orm.now()}

orm.DataSet(**dataset).save()

indicator = {'indID': 'PVX040',
             'name': 'Incidence of Conflict',
             'units': 'incidents per year'}

orm.Indicator(**indicator).save()


def parsesheet(url):
    rowset = messytables.excel.XLSTableSet(dl.grab(url)).tables[0]
    for i, row in enumerate(rowset):
        if i == 0:
            headers = [x.value for x in row]
            continue
        yield OrderedDict(list(zip(headers, [x.value for x in row])))


def geturls(baseurl='http://www.acleddata.com/data/conflict-by-type-and-actor/'):
    html = requests.get(baseurl).content
    print html
    root = lxml.html.fromstring(html)
    root.make_links_absolute(baseurl)
    links = root.xpath("//div[@id='content']//article//a[contains(text(),'xls')]/@href")
    assert links
    print links
    return links

def keyfunc(item):
    return (item['YEAR'], item['COUNTRY'])

events = []
for url in geturls():
    print url
    _parsesheet = list(parsesheet(url))
    print len(_parsesheet)
    for row in _parsesheet:
        if row['EVENT_TYPE'].strip() in NONVIOLENT:
            print row['EVENT_TYPE'] ## TODO: not working!!!!
            continue
        events.append(row)
    print "E", len(events)
sorted_e = sorted(events, key=keyfunc)

print "HERE"

for item in itertools.groupby(sorted_e, keyfunc):
    print "item"
    value_item = {'dsID': 'acled',
                  'indID': 'PVX040',
                  'period': item[0][0],
                  'region': item[0][1],
                  'value': len(list(item[1])),
                  'source': 'http://www.acleddata.com/data/types-and-groups/'}
    orm.Value(**value_item).save()
