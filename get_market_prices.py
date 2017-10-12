#!/usr/bin/env python

'''get_market_prices.py: Fetch prices at regular intervals up to an event start.'''

import datetime
from os import rename
import time

import betfair
from betfair import Betfair
from betfair.models import MarketFilter
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

tab = []

with open('events_schedule', 'r') as f:
    for line in f:
        tab.append(line.split(","))
race_time = tab[0][0]
marketId = [[row[2][1:9], row[2][12:-1]] for row in tab]

with open('temp_schedule', 'w+') as f:
    del tab[0]
    for row in tab:
        f.write(row[0]+','+row[1]+','+row[2])
rename('temp_schedule',
          'events_schedule')

hardcoded = marketId[0][1]
runners = client.list_market_catalogue(MarketFilter(
                                market_ids = hardcoded,
                                market_type_codes = 'WIN'),
                                market_projection = [MarketProjection(6)])

selectionId = []
runnerName = []
for i in range(len(runners[0].serialize()['runners'])):
    selectionId.append(runners[0].serialize()['runners'][i]['selectionId'])
    runnerName.append(runners[0].serialize()['runners'][i]['runnerName'])

d = dict(zip(selectionId, runnerName))

level = 3
projection={'priceData':['EX_BEST_OFFERS', 'SP_AVAILABLE','SP_TRADED'],
            'virtualise':False,
            'exBestOffersOverrides':{'bestPricesDepth': level,
                                     'rollupModel':"STAKE",
                                     'rollupLimit':20},
            'rolloverStakes':False
}

# convert the race time from HH:MM to a digital format, e.g. 14:10 to 1410
race_time = int(race_time[0:2]+race_time[3:]+'00')
current_time = datetime.datetime.now().strftime('%H:%M')+'00'
current_time = int(current_time[0:2]+current_time[3:])

while(current_time < race_time):
    # wait 2 second before taking a snapshot of the market
    # this is our example time interval between each set of prices is captured
    time.sleep(2)
    lista = client.list_market_book(market_ids = [hardcoded], price_projection=projection, order_projection='ALL', match_projection='ROLLED_UP_BY_PRICE', currency_code='USD')
    for i in range(len(lista[0].serialize()['runners'])):
        if(lista[0].serialize()['runners'][i]['status'] != 'REMOVED'):
            lastprice = lista[0].serialize()['runners'][i]['lastPriceTraded']
            timestamp = datetime.datetime.now().strftime('%H:%M:%S')

            # capture 3 levels of prices and volumes for back and lay markets
            back_price1 = lista[0].serialize()['runners'][i]['ex']['availableToBack'][0]['price']
            back_vol1 = lista[0].serialize()['runners'][i]['ex']['availableToBack'][0]['size']
            
            if(len(lista[0].serialize()['runners'][i]['ex']['availableToLay'])):
                lay_price1 = lista[0].serialize()['runners'][i]['ex']['availableToLay'][0]['price']
                lay_vol1 = lista[0].serialize()['runners'][i]['ex']['availableToLay'][0]['size']
            else:
                lay_price1 = 0
                lay_vol1 = 0

            back_price2 = lista[0].serialize()['runners'][i]['ex']['availableToBack'][1]['price']
            back_vol2 = lista[0].serialize()['runners'][i]['ex']['availableToBack'][1]['size']
            
            if(len(lista[0].serialize()['runners'][i]['ex']['availableToLay']) == level-1):
                lay_price2 = lista[0].serialize()['runners'][i]['ex']['availableToLay'][1]['price']
                lay_vol2 = lista[0].serialize()['runners'][i]['ex']['availableToLay'][1]['size']
            else:
                lay_price2 = 0
                lay_vol2 = 0

            back_price3 = lista[0].serialize()['runners'][i]['ex']['availableToBack'][2]['price']
            back_vol3 = lista[0].serialize()['runners'][i]['ex']['availableToBack'][2]['size']
        
            if(len(lista[0].serialize()['runners'][i]['ex']['availableToLay']) == level):
                lay_price3 = lista[0].serialize()['runners'][i]['ex']['availableToLay'][2]['price']
                lay_vol3 = lista[0].serialize()['runners'][i]['ex']['availableToLay'][2]['size']
            else:
                lay_price3 = 0
                lay_vol3 = 0
                            
            # calculate weighted average prices, back and lay, and total back and lay volume
            total_back_vol = round(back_vol1 + back_vol2 + back_vol3, 2)
            total_lay_vol = round(lay_vol1 + lay_vol2 + lay_vol3, 2)
            wom = round(total_back_vol/(total_back_vol+total_lay_vol), 2)
            with connection.cursor() as cursor:
                cursor.execute("""INSERT INTO price VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                                (marketId[0][0]+' / '+marketId[0][1],
                                lista[0].serialize()['runners'][i]['selectionId'],
                                d[lista[0].serialize()['runners'][i]['selectionId']],
                                date_today,
                                timestamp,
                                back_price1,
                                back_vol1,
                                total_back_vol,
                                lastprice,
                                wom,
                                lay_price1,
                                lay_vol1,
                                total_lay_vol))
    current_time = datetime.datetime.now().strftime('%H:%M')+'00'
    current_time = int(current_time[0:2]+current_time[3:])
