import time
import requests
import hashlib
import hmac
import sys,os

TICK_INTERVAL = 20  # seconds

def main():

    print("BITTREX ORDER BOOK")

    market = input("Get book for: ")

    print(getBittrexBook(market))
    

def getBittrexBook(market):
    url = "https://bittrex.com/api/v1.1/public/getorderbook?market=BTC-" + market + "&type=both"
    return simple_request(url)

def simple_request(url):
    r = requests.get(url)
    return r.json()


def format_float(f):
    return "%.8f" % f


if __name__ == "__main__":
    main()
