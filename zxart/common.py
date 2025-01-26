import dataclasses as dc
from enum import Enum, StrEnum
from types import MappingProxyType
from typing import Any, Literal, TypedDict

import yarl

_BASE_URL = yarl.URL("https://zxart.ee/api/")
"""Базовый URL API"""


@dc.dataclass(frozen=True, slots=True)
class SortingSettings:
    """Параметры сортировки."""

    field: Literal[
        "year",
        "plays",
        "title",
        "place",
        "date",
        "votes",
        "commentsAmount",
    ]
    """Поле сортировки."""

    order: Literal["asc", "desc", "rand"] = "desc"
    """Порядок сортировки. По-умолчанию: убывающий."""

    def __str__(self):
        return f"{self.field},{self.order}"


class Sorting(Enum):
    """Часто использованные шаблоны сортировки."""

    TOP_RATED = SortingSettings("votes")
    """Самые рейтинговые"""
    MOST_PLAYED = SortingSettings("plays")
    """Самые прослушиваемые"""
    MOST_RECENT = SortingSettings("date")
    """Недавно загруженные"""
    TOP_PLACED = SortingSettings("place", "asc")
    """Самые оцененные на мероприятиях"""
    MOST_COMMENTED = SortingSettings("commentsAmount")
    """Самые комментируемые"""

    def __str__(self):
        return str(self.value)


class Language(StrEnum):
    """Предпочитаемый язык переводимых полей ответа."""

    ENGLISH = "eng"
    """Английский"""
    RUSSIAN = "rus"
    """Русский"""
    SPANISH = "spa"
    """Испанский"""


class Entity(StrEnum):
    """Сущности поддерживаемые API."""

    AUTHOR = "author"
    """Автор"""
    AUTHOR_ALIAS = "authorAlias"
    """Псевдоним автора"""
    GROUP = "group"
    """Группа"""
    GROUP_ALIAS = "groupAlias"
    """Псевдоним группы"""
    PRODUCT = "zxProd"
    """Продукт"""
    PRODUCT_CATEGORY = "zxProdCategory"
    """Категория продукта"""
    RELEASE = "zxRelease"
    """Релиз"""
    PICTURE = "zxPicture"
    """Изображение"""
    MUSIC = "zxMusic"
    """Музыка"""


class CommonOptions(TypedDict, total=False):
    """Общие опции запроса"""

    language: Language
    """Язык переводимых полей ответа."""
    order: SortingSettings | Sorting
    """Порядок сортировки."""
    start: int
    """Индекс начальной записи выборки."""
    limit: int
    """Ограничение ответа."""
    id: int
    """Фильтр: идентификатор сущности"""


class MediaOptions(CommonOptions, total=False):
    """Опции фильтра"""

    title: str
    """Фильтр: содержание наименования"""
    author_id: int
    """Фильтр: идентификатор автора"""
    years: list[int]
    """Фильтр: годы публикации"""
    min_rating: float
    """Фильтр: минимальный рейтинг"""
    min_party_place: int
    """Фильтр: минимальное место на мероприятии"""


_FILTER_MAP = MappingProxyType(
    {
        "author_id": "authorId",
        "format_group": "FormatGroup",
        "format": "Format",
        "id": "Id",
        "min_party_place": "MinPartyPlace",
        "min_rating": "MinRating",
        "title": "TitleSearch",
        "years": "Year",
        "compo": "Compo",
        "type": "Type",
        "has_inspiration": "Inspiration",
        "has_stages": "Stages",
    }
)


def url_from_options(**kwargs: Any):
    """Преобразует параметры в URL запроса к API."""

    entity, filters = kwargs["export"], []

    for k in tuple(kwargs):
        if (fk := _FILTER_MAP.get(k)) is None:
            continue

        if isinstance(v := kwargs.pop(k), (list, tuple)):
            v = ",".join(map(str, v))

        if k != "author_id":
            fk = f"{entity}{fk}"

        filters.append(f"{fk}={v}")

    if filters:
        kwargs["filter"] = ";".join(filters)

    return _BASE_URL.joinpath(*(f"{k}:{v}" for k, v in kwargs.items()))
