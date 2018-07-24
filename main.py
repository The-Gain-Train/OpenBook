from binance.client import Client
from collections import OrderedDict
import time
import requests
import hashlib
import hmac

TICK_INTERVAL = 60  # seconds


#TREX API INFO
API_KEY = 'my-api-key'
API_SECRET_KEY = 'my-secret-key'

#BINANCE API INFO
binance = Client('API_KEY', 'API_SECRET_KEY')


def main():
    print('Starting trader bot...')

    while True:
        start = time.time()
        tick()
        end = time.time()

        # Sleep the thread if needed
        if end - start < TICK_INTERVAL:
            time.sleep(TICK_INTERVAL - (end - start))


def tick():
    print('Running routine')
    print('BIDS' + '\t\t\t\t\t\t' + 'ASKS')
    print('QTY' + '\t\tBid' +'\t\tValue' + '\t\t' + 'Value' + '\t\tAsk' +'\t\tQTY')

    trexBidList={}  #declare our bid list, which will hold tuples of data (quantity, rate, btc sum)
    trexAskList={} #declare out ask list
    binanceBidList={} 
    binanceAskList={} 
    finalBidList={} #final aggregate bid list
    finalAskList={} #final aggregate ask list

    # BITTREX LOGIC
    # BID LOGIC
    bookData = simple_request('https://bittrex.com/api/v1.1/public/getorderbook?market=BTC-LTC&type=buy')

    i = 0
    while i < len(bookData['result']):  # i < BID DEPTH 
        qty = bookData['result'][i]['Quantity']
        rate = bookData['result'][i]['Rate']
        tot = qty*rate
        trexBidList["%.8f" % rate] ="%.8f" %  qty #add to bid dictionary

        i += 1

    # ASK LOGIC
    bookData = simple_request('https://bittrex.com/api/v1.1/public/getorderbook?market=BTC-LTC&type=sell')

    i = 0
    while i < len(bookData['result']):  # i < ASK DEPTH 
        qty = bookData['result'][i]['Quantity']
        rate = bookData['result'][i]['Rate']
        tot = qty*rate
        trexAskList["%.8f" % rate] ="%.8f" %  qty #add to ask dictionary

        i += 1



    # BINANCE LOGIC
    # BID LOGIC
    depth = binance.get_order_book(symbol='LTCBTC', limit=1000)

    i = 0
    while i < len(depth['bids']): # i < BID DEPTH
        bid = depth['bids'][i][0]
        qty = depth['bids'][i][1]
        rate = float(bid)
        qtyz = float(qty)
        tot = rate*qtyz
        binanceBidList["%.8f" % rate] ="%.8f" %  qtyz #add to bid dictionary

        i += 1

    # ASK LOGIC

    while i < len(depth['asks']): # i < ASK DEPTH
        ask = depth['asks'][i][0]
        qty = depth['asks'][i][1]
        rate = float(ask)
        qtyz = float(qty)
        binanceAskList["%.8f" % rate] = "%.8f" %  qtyz #add to ask dictionary

        i += 1

    for bid in trexBidList:
        sum = float(trexBidList[bid])
        if bid in binanceBidList:
            sum += float(binanceBidList[bid])
            del binanceBidList[bid]
        finalBidList[bid] = "%.8f" % sum

    for ask in trexAskList:
        sum = float(trexAskList[ask])
        if ask in binanceAskList:
            sum += float(binanceAskList[ask])
            del binanceAskList[ask]
        finalAskList[ask] = "%.8f" % sum

    for bid in binanceBidList:
        finalBidList[bid] = binanceBidList[bid]

    for ask in binanceAskList:
        finalAskList[ask] = binanceAskList[ask]

    finalSortedAskList = OrderedDict(sorted(finalAskList.items()))
    finalSortedBidList = OrderedDict(sorted(list(finalBidList.items())))

    for (bid, bidAmount), (ask, askAmount) in zip(reversed(finalSortedBidList.items()), finalSortedAskList.items()):
        print(bidAmount + '\t' + bid + '\t' + str("%.8f" % (float(bid) * float(bidAmount))) + '\t' + str("%.8f" % (float(ask) * float(askAmount))) + '\t' + ask + '\t' + askAmount)



def signed_request(url):
    now = time.time()
    url += '&nonce=' + str(now)
    signed = hmac.new(API_SECRET_KEY, url.encode('utf-8'), hashlib.sha512).hexdigest()
    headers = {'apisign': signed}
    r = requests.get(url, headers=headers)
    return r.json()

def simple_request(url):
    r = requests.get(url)
    return r.json()

def format_float(f):
    return "%.8f" % f

if __name__ == "__main__":
    main()