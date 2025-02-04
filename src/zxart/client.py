from __future__ import annotations

import logging
from typing import TYPE_CHECKING, overload

import aiohttp
import orjson
import yarl

from .common import Entity, Language, Order, process_filters
from .models import ApiResponse

if TYPE_CHECKING:
    from typing import Any, Literal, Unpack

    from .common import CommonOptions, OrderSettings
    from .image import ImageParams
    from .models import Author, AuthorAlias, Image, ProductCategory, Tune
    from .tune import TuneParams

_LOGGER = logging.getLogger(__name__)

# Опции по-умолчанию
_DEFAULT_ORDER = Order.MOST_RECENT
_DEFAULT_LANGUAGE = Language.RUSSIAN
_DEFAULT_LIMIT = 60

_BASE_URL = yarl.URL("https://zxart.ee/api/")
"""Базовый URL API"""


class ZXArtApiError(Exception):
    """Ошибка API"""


class ZXArtClient:
    """Клиент ZXArt"""

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
        """
        Инициализирует клиент параметрами запроса `по-умолчанию`.

        Параметры:
        - `language`: язык переводимых полей сущностей. По-умолчанию: `русский`.
        - `limit`: ограничение по количеству записей. По-умолчанию: `60`.
        - `order`: порядок сортировки результата. По-умолчанию: `сначала последние`.
        - `session`: пользовательская сессия `aiohttp.ClientSession`.
        """

        self._language = language or _DEFAULT_LANGUAGE
        self._limit = limit or _DEFAULT_LIMIT
        self._order = order or _DEFAULT_ORDER
        self._cli = session or aiohttp.ClientSession()
        self._close_connector = not session

    async def __aenter__(self):
        return self

    def __aexit__(self, exc_type, exc_value, traceback):
        return self.close()

    async def close(self):
        """Закрытие"""

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
    ) -> ApiResponse[Tune]:
        """
        Запрос мелодий по параметрам:

        Общие параметры (значения по-умолчанию из клиента):
        - `language`: язык переводимых полей сущностей.
        - `start`: стартовая позиция курсора запроса.
        - `limit`: ограничение по количеству записей.
        - `order`: порядок сортировки результата.

        Фильтры:
        - `id`: идентификатор.
        - `author_id`: идентификатор автора.
        - `title`: контекст наименования.
        - `years`: год(а) издания (поддерживает `Iterable`).
        - `min_rating`: минимальный рейтинг.
        - `min_party_place`: минимальное место на мероприятии.
        - `tags_include`: включает тег(и) (поддерживает `Iterable`).
        - `tags_exclude`: не включает тег(и) (поддерживает `Iterable`).
        - `format`: формат мелодии.
        - `format_group`: формат группы мелодии.
        """

    @overload
    async def api(
        self,
        entity: Literal[Entity.IMAGE],
        **kwargs: Unpack[ImageParams],
    ) -> ApiResponse[Image]:
        """
        Запрос изображений по параметрам:

        Общие параметры (значения по-умолчанию из клиента):
        - `language`: язык переводимых полей сущностей.
        - `start`: стартовая позиция курсора запроса.
        - `limit`: ограничение по количеству записей.
        - `order`: порядок сортировки результата.

        Фильтры:
        - `id`: идентификатор.
        - `author_id`: идентификатор автора.
        - `title`: контекст наименования.
        - `years`: год(а) издания (поддерживает `Iterable`).
        - `min_rating`: минимальный рейтинг.
        - `min_party_place`: минимальное место на мероприятии.
        - `tags_include`: включает тег(и) (поддерживает `Iterable`).
        - `tags_exclude`: не включает тег(и) (поддерживает `Iterable`).
        """

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
            json: dict[str, Any] = await x.json(loads=orjson.loads)

        if json.pop("responseStatus") != "success":
            raise ZXArtApiError("API request error.")

        json["result"] = json.pop("responseData")[entity]
        json["entity"] = entity

        return ApiResponse.from_dict(json)

    async def author(self, author_id: int) -> Author | None:
        """Запрос автора по идентификатору."""

        if x := (await self.api(Entity.AUTHOR, id=author_id)).result:
            return x[0]
