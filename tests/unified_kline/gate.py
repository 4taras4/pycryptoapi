import asyncio

from pycryptoapi.gate import GateSocketManager, GateAdapter
from pycryptoapi.enums import MarketType
from pycryptoapi.exceptions import AdapterException


async def callback(msg):
    try:
        k = GateAdapter.kline_message(raw_msg=msg)
        for i in k:
            print(f'i: kline response: {i["s"]} {i["o"]} {i["h"]} {i["l"]} {i["c"]} {i["v"]} closed={i["x"]} tf={i["i"]}')
    except AdapterException as e:
        print(f"Can not adapt message ({e}): {msg}")

async def main():
    socket = GateSocketManager.klines_socket(
        market_type=MarketType.FUTURES,
        timeframe='1m',
        tickers=['NEWT_USDT'],
        callback=callback
    )

    await socket.start()


asyncio.run(main())


'''

'''
