import asyncio

from pycryptoapi.gate import GateSocketManager, GateAdapter
from pycryptoapi.enums import MarketType
from pycryptoapi.exceptions import AdapterException


async def callback(msg):
    try:
        print(msg)
        k = GateAdapter.kline_message(raw_msg=msg)
        for i in k:
            print(i)
    except AdapterException as e:
        print(f"Can not adapt message ({e}): {msg}")

async def main():
    socket = GateSocketManager.klines_socket(
        market_type=MarketType.SPOT,
        timeframe="1m",
        tickers=["BTCUSDT"],
        callback=callback
    )

    await socket.start()


asyncio.run(main())


'''

'''
