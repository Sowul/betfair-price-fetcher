#!/usr/bin/env python

'''get_betfair_races.py: Capture daily racing event data (UK win markets).'''

import time

import betfair
from betfair import Betfair
from betfair.models import MarketFilter, MarketCatalogue
from betfair.constants import MarketProjection
import pymysql.cursors

client = Betfair('APP_KEY', ('certs/api.crt', 'certs/api.key'))
client.login('BF_USERNAME', 'BF_PASSWORD')
client.keep_alive()

date_today = time.strftime("%Y-%m-%d")

connection = pymysql.connect(host='localhost',
                             user='USERNAME',
                             password='YOUR DATABASE PASSWORD',
                             db='DATABASE NAME',
                             charset='utf8mb4',
                             autocommit=True,
                             cursorclass=pymysql.cursors.DictCursor)


marketFilter={'eventTypeIds':[7],
              'marketCountries':['GB'],
              'marketTypeCodes':["WIN"]}
                  
markets_hash = client.list_events(marketFilter)
markets = []

print("WRITING TO DB")
for market in markets_hash:
    if ((market.serialize()['event']['openDate'][:10] == date_today)):
        markets.append(client.list_market_catalogue(MarketFilter(
                                event_ids = market.serialize()['event']['id'],
                                market_type_codes = 'WIN'),
                                market_projection = [MarketProjection(3), MarketProjection(7)]))
        for event in markets:
            for race in event:  
                with connection.cursor() as cursor:
                    cursor.execute("""INSERT IGNORE INTO races VALUES (%s,%s,%s,%s,%s,%s)""",
                                (date_today,
                                race.serialize()['event']['countryCode'],
                                race.serialize()['event']['venue'],
                                race.serialize()['marketStartTime'][11:19],
                                race.serialize()['event']['id']+' / '+race.serialize()['marketId'],
                                race.serialize()['marketName']))
print("DONE")
