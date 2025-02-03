from __future__ import annotations

import logging
from typing import TYPE_CHECKING, overload

import aiohttp
import orjson
import yarl

from .common import Language, Order, process_filters
from .models import ApiResponse

if TYPE_CHECKING:
    from typing import Any, Literal, Unpack

    from .common import CommonOptions, Entity, OrderSettings
    from .image import ImageParams
    from .models import Author, AuthorAlias, Image, ProductCategory, Tune
    from .tune import TuneParams

_LOGGER = logging.getLogger(__name__)

# Опции по-умолчанию
_DEFAULT_SORTING = Order.MOST_RECENT
_DEFAULT_LANGUAGE = Language.RUSSIAN
_DEFAULT_LIMIT = 60

_BASE_URL = yarl.URL("https://zxart.ee/api/")
"""Базовый URL API"""


class ZXArtApiError(Exception):
    pass


class ZXArtClient:
    _cli: aiohttp.ClientSession
    _language: Language
    _limit: int
    _order: Order | OrderSettings

    def __init__(
        self,
        *,
        language: Language | None = None,
        limit: int | None = None,
        order: Order | OrderSettings | None = None,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        self._language = language or _DEFAULT_LANGUAGE
        self._limit = limit or _DEFAULT_LIMIT
        self._order = order or _DEFAULT_SORTING
        self._cli = session or aiohttp.ClientSession()
        self._close_connector = not session

    async def __aenter__(self):
        return self

    def __aexit__(self, exc_type, exc_value, traceback):
        return self.close()

    async def close(self):
        if self._close_connector:
            await self._cli.close()

    @overload
    async def api(
        self,
        entity: Literal[Entity.AUTHOR],
        **kwargs: Unpack[CommonOptions],
    ) -> ApiResponse[Author]: ...

    @overload
    async def api(
        self,
        entity: Literal[Entity.AUTHOR_ALIAS],
        **kwargs: Unpack[CommonOptions],
    ) -> ApiResponse[AuthorAlias]: ...

    @overload
    async def api(
        self,
        entity: Literal[Entity.PRODUCT_CATEGORY],
        **kwargs: Unpack[CommonOptions],
    ) -> ApiResponse[ProductCategory]: ...

    @overload
    async def api(
        self,
        entity: Literal[Entity.TUNE],
        **kwargs: Unpack[TuneParams],
    ) -> ApiResponse[Tune]: ...

    @overload
    async def api(
        self,
        entity: Literal[Entity.IMAGE],
        **kwargs: Unpack[ImageParams],
    ) -> ApiResponse[Image]: ...

    async def api(self, entity: Entity, **kwargs: Any) -> ApiResponse:
        if kwargs:
            process_filters(entity, kwargs)

        kwargs.setdefault("language", self._language)
        kwargs.setdefault("limit", self._limit)
        kwargs.setdefault("order", self._order)
        kwargs["export"] = entity

        url = _BASE_URL.joinpath(*(f"{k}:{v}" for k, v in kwargs.items()))

        _LOGGER.debug("API request URL: %s", url)

        async with self._cli.get(url) as x:
            raw_data = await x.read()

        json: dict[str, Any] = orjson.loads(raw_data)

        if json.pop("responseStatus") != "success":
            raise ZXArtApiError("API request error!")

        json["result"] = json.pop("responseData")[entity]
        json["entity"] = entity

        return ApiResponse.from_dict(json)
