__all__ = ["GateClient"]

from typing import Any, Optional, Dict, Literal

from ..abstract import AbstractClient
from ..enums import Timeframe, Exchange
from ..types import JsonLike


class GateClient(AbstractClient):
    _BASE_URL: str = "https://api.gateio.ws/api/v4"

    def _normalize_symbol(self, symbol: str) -> str:
        """Convert symbol to Gate format, e.g., BTCUSDT -> BTC_USDT."""
        if "_" in symbol:
            return symbol
        # Simple normalization for common quote assets like USDT
        if symbol.endswith("USDT"):
            return symbol.replace("USDT", "_USDT")
        return symbol

    async def klines(
        self,
        symbol: str,
        interval: Timeframe,
        limit: int = 500,
        start: Optional[int] = None,
        end: Optional[int] = None,
    ) -> JsonLike:
        """
        Получает свечи со spot рынка Gate.io

        GET /spot/candlesticks
        """
        url = f"{self._BASE_URL}/spot/candlesticks"
        params = self.filter_params(
            {
                "currency_pair": self._normalize_symbol(symbol),
                "interval": interval.to_exchange_format(Exchange.GATE),
                "limit": limit,
                "from": start,
                "to": end,
            }
        )
        return await self._make_request(method="GET", url=url, params=params)

    async def futures_klines(
        self,
        symbol: str,
        interval: Timeframe,
        start: Optional[int] = None,
        end: Optional[int] = None,
        limit: Optional[int] = 200,
        settle: Literal["btc", "usdt"] = "usdt",
    ) -> JsonLike:
        """
        Получает свечи с фьючерсного рынка Gate.io

        GET /futures/{settle}/candlesticks
        """
        url = f"{self._BASE_URL}/futures/{settle}/candlesticks"
        params = self.filter_params(
            {
                "contract": self._normalize_symbol(symbol),
                "interval": interval.to_exchange_format(Exchange.GATE),
                "limit": limit,
                "from": start,
                "to": end,
            }
        )
        return await self._make_request(method="GET", url=url, params=params)

    async def ticker(self, symbol: Optional[str] = None) -> JsonLike:
        """
        Получает 24-часовую статистику изменения цены и объема для спотового рынка.

        :param symbol: (опционально) Торговая пара, например 'BTCUSDT'. Если не указано, возвращает данные по всем парам.
        :return: JSON-ответ с данными статистики.
        :raises Exception: Если запрос не выполнен успешно.
        """
        url = f"{self._BASE_URL}/spot/tickers"
        params = {"currency_pair": symbol} if symbol else {}
        return await self._make_request(method="GET", url=url, params=params)

    async def futures_ticker(self, symbol: Optional[str] = None, settle: Literal["btc", "usdt"] = "usdt") -> JsonLike:
        """
        Получает 24-часовую статистику изменения цены и объема для фьючерсного рынка.

        :param symbol: (опционально) Торговая пара, например 'BTC_USDT'. Если не указано, возвращает данные по всем парам.
        :param settle: (опционально) Постфикс торговых пар для поиска. По умолчанию: usdt
        :return: JSON-ответ с данными статистики.
        :raises Exception: Если запрос не выполнен успешно.
        """
        url = f"{self._BASE_URL}/futures/{settle}/tickers"
        params = {"contract": symbol} if symbol else {}
        return await self._make_request(method="GET", url=url, params=params)

    async def depth(self, symbol: str, limit: int = 100) -> JsonLike:
        """
        Получает данные ордербука (глубины рынка) для спотового рынка.

        :param symbol: Торговая пара в формате 'BTC_USDT'
        :param limit: Количество уровней ордербука (доступные значения: 5, 10, 20, 50, 100, 200, 500, 1000)
        :return: JSON-ответ с ордерами на покупку и продажу.
        :raises Exception: Если запрос не выполнен успешно.
        """
        url = f"{self._BASE_URL}/spot/order_book"
        params = {"currency_pair": symbol, "limit": limit}
        return await self._make_request(method="GET", url=url, params=params)

    async def funding_rate(self) -> Dict[str, Any]:
        raise NotImplementedError()

    async def open_interest(self, symbol: Optional[str] = None) -> JsonLike:
        raise NotImplementedError()
