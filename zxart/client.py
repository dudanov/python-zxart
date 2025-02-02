from __future__ import annotations

import logging
from typing import TYPE_CHECKING, overload

import aiohttp
import yarl

from .common import Language, Sorting, process_filters
from .models import Response

if TYPE_CHECKING:
    from typing import Any, Literal, Unpack

    from .common import CommonOptions, Entity, SortingSettings
    from .models import Author, AuthorAlias, Image, ProductCategory, Tune
    from .music import ImageParams, TuneParams

_LOGGER = logging.getLogger(__name__)

# Опции по-умолчанию
_DEFAULT_SORTING = Sorting.MOST_RECENT
_DEFAULT_LANGUAGE = Language.RUSSIAN
_DEFAULT_LIMIT = 60

_BASE_URL = yarl.URL("https://zxart.ee/api/")
"""Базовый URL API"""


class ZXArtClient:
    _cli: aiohttp.ClientSession
    _language: Language
    _limit: int
    _sorting: Sorting | SortingSettings

    def __init__(
        self,
        *,
        language: Language | None = None,
        limit: int | None = None,
        sorting: Sorting | SortingSettings | None = None,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        self._language = language or _DEFAULT_LANGUAGE
        self._limit = limit or _DEFAULT_LIMIT
        self._sorting = sorting or _DEFAULT_SORTING
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
    ) -> list[Author]: ...

    @overload
    async def api(
        self,
        entity: Literal[Entity.AUTHOR_ALIAS],
        **kwargs: Unpack[CommonOptions],
    ) -> list[AuthorAlias]: ...

    @overload
    async def api(
        self,
        entity: Literal[Entity.PRODUCT_CATEGORY],
        **kwargs: Unpack[CommonOptions],
    ) -> list[ProductCategory]: ...

    @overload
    async def api(
        self,
        entity: Literal[Entity.TUNE],
        **kwargs: Unpack[TuneParams],
    ) -> list[Tune]: ...

    @overload
    async def api(
        self,
        entity: Literal[Entity.IMAGE],
        **kwargs: Unpack[ImageParams],
    ) -> list[Image]: ...

    async def api(self, entity: Entity, **kwargs: Any) -> list[Any]:
        if kwargs:
            process_filters(entity, kwargs)

        kwargs.setdefault("language", self._language)
        kwargs.setdefault("limit", self._limit)
        kwargs.setdefault("order", self._sorting)
        kwargs["export"] = entity

        url = _BASE_URL.joinpath(*(f"{k}:{v}" for k, v in kwargs.items()))

        _LOGGER.debug("API request URL: %s", url)

        async with self._cli.get(url) as x:
            raw_data = await x.read()

        response = Response.from_json(raw_data)

        return getattr(response.data, entity)
