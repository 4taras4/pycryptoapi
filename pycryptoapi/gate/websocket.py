__all__ = ["GateWebsocket", "GateSocketManager", ]

import json
from typing import Optional, Union, List, Literal, Callable, Awaitable, Dict, Tuple
import time

from ..abstract import AbstractWebsocket, AbstractSocketManager
from ..enums import MarketType, Timeframe, Exchange
from ..exceptions import MarketException, TimeframeException


class GateWebsocket(AbstractWebsocket):

    @property
    def _connection_uri(self) -> str:
        if self._market_type == MarketType.SPOT:
            return "wss://api.gateio.ws/ws/v4/"
        elif self._market_type == MarketType.FUTURES:
            return "wss://fx-ws.gateio.ws/v4/ws/usdt"
        else:
            raise MarketException()

    def _normalize_ticker(self, ticker: str) -> str:
        """Convert ticker to Gate.io format (e.g., BTCUSDT -> BTC_USDT)"""
        return ticker if ticker.endswith("_USDT") else ticker.replace("USDT", "_USDT")

    def _create_message(self, payload) -> str:
        """Create standard Gate.io subscription message"""
        return json.dumps({
            "time": int(time.time()),
            "channel": self._topic,
            "event": "subscribe",
            "payload": payload,
        })

    @property
    def _subscribe_message(self) -> Union[str, List[str]]:
        # Handle tickers (no specific tickers needed)
        if self._topic.endswith(".tickers"):
            return self._create_message([])
        
        # Handle candlesticks (requires timeframe + ticker per message)
        if self._topic.endswith(".candlesticks"):
            if not self._timeframe:
                raise TimeframeException()
            return [
                self._create_message([self._timeframe, self._normalize_ticker(ticker)])
                for ticker in self._tickers
            ]
        
        # Handle trades (list of tickers)
        if self._topic.endswith(".trades"):
            normalized_tickers = [self._normalize_ticker(ticker) for ticker in self._tickers]
            return self._create_message(normalized_tickers)
        
        raise ValueError(f"Invalid topic: {self._topic}")

    @property
    def _ping_message(self) -> Optional[str]:
        channel = "spot.ping" if self._market_type == MarketType.SPOT else "futures.ping"
        return json.dumps({"time": int(time.time()), "channel": channel})


class GateSocketManager(AbstractSocketManager):

    # Topic mapping for different market types
    _TOPICS = {
        MarketType.SPOT: {
            "trades": "spot.trades",
            "candlesticks": "spot.candlesticks", 
            "tickers": "spot.tickers"
        },
        MarketType.FUTURES: {
            "trades": "futures.trades",
            "candlesticks": "futures.candlesticks",
            "tickers": "futures.tickers"
        }
    }

    @classmethod
    def _get_topic(cls, market_type: MarketType, topic_type: str) -> str:
        """Get topic string for given market type and topic type"""
        if market_type not in cls._TOPICS:
            raise MarketException()
        return cls._TOPICS[market_type][topic_type]

    @classmethod
    def aggtrades_socket(
            cls,
            market_type: MarketType,
            tickers: List[str] | Tuple[str, ...],
            callback: Callable[..., Awaitable],
            **kwargs
    ) -> GateWebsocket:
        return GateWebsocket(
            topic=cls._get_topic(market_type, "trades"),
            tickers=tickers,
            market_type=market_type,
            callback=callback,
            **kwargs
        )

    @classmethod
    def klines_socket(
            cls,
            tickers: List[str] | Tuple[str, ...],
            timeframe: Timeframe,
            market_type: MarketType,
            callback: Callable[..., Awaitable],
            **kwargs
    ) -> GateWebsocket:
        return GateWebsocket(
            topic=cls._get_topic(market_type, "candlesticks"),
            tickers=tickers,
            market_type=market_type,
            timeframe=timeframe.to_exchange_format(Exchange.GATE),
            callback=callback,
            **kwargs
        )

    @classmethod
    def tickers_socket(
            cls,
            market_type: MarketType,
            callback: Callable[..., Awaitable],
            timezone: Literal[""] = "+8",
            **kwargs
    ) -> GateWebsocket:
        return GateWebsocket(
            topic=cls._get_topic(market_type, "tickers"),
            market_type=market_type,
            callback=callback,
            **kwargs
        )

    @classmethod
    def liquidations_socket(cls) -> GateWebsocket:
        raise NotImplementedError()
