import dataclasses as dc
from enum import Enum, StrEnum
from typing import Any, Iterable, Literal, TypedDict


@dc.dataclass(frozen=True, slots=True)
class OrderSettings:
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


class Order(Enum):
    """Часто использованные шаблоны сортировки."""

    TOP_RATED = OrderSettings("votes")
    """Самые рейтинговые"""
    MOST_PLAYED = OrderSettings("plays")
    """Самые прослушиваемые"""
    MOST_RECENT = OrderSettings("date")
    """Недавно загруженные"""
    TOP_PLACED = OrderSettings("place", "asc")
    """Самые оцененные на мероприятиях"""
    MOST_COMMENTED = OrderSettings("commentsAmount")
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
    IMAGE = "zxPicture"
    """Изображение"""
    TUNE = "zxMusic"
    """Мелодия"""


class CommonOptions(TypedDict, total=False):
    """Общие опции запроса"""

    language: Language
    """Язык переводимых полей ответа."""
    limit: int
    """Ограничение ответа."""
    order: OrderSettings | Order
    """Порядок сортировки."""
    start: int
    """Индекс начальной записи выборки."""
    id: int
    """Фильтр: идентификатор сущности"""


class MediaParams(CommonOptions, total=False):
    """Опции фильтра"""

    author_id: int
    """Фильтр: идентификатор автора"""
    title: str
    """Фильтр: содержание наименования"""
    years: Iterable[int] | int
    """Фильтр: годы публикации"""
    min_rating: float
    """Фильтр: минимальный рейтинг"""
    min_party_place: int
    """Фильтр: минимальное место на мероприятии"""
    tags_include: Iterable[str] | str
    """Фильтр: с тегами"""
    tags_exclude: Iterable[str] | str
    """Фильтр: без тегов"""


_FILTER_MAP = {
    "author_id": "authorId",
    "compo": "Compo",
    "format_group": "FormatGroup",
    "format": "Format",
    "has_inspiration": "Inspiration",
    "has_stages": "Stages",
    "id": "Id",
    "min_party_place": "MinPartyPlace",
    "min_rating": "MinRating",
    "tags_exclude": "TagsExclude",
    "tags_include": "TagsInclude",
    "title": "TitleSearch",
    "type": "Type",
    "years": "Year",
}


def process_filters(entity: Entity, kwargs: dict[str, Any]) -> None:
    """Обработка параметров фильтров"""

    filters: list[str] = []

    for arg in tuple(kwargs):
        if (k := _FILTER_MAP.get(arg)) is None:
            continue

        v = kwargs.pop(arg)

        if not isinstance(v, str) and isinstance(v, Iterable):
            v = ",".join(map(str, v))

        if k[0].isupper():
            k = entity + k

        filters.append(f"{k}={v}")

    if filters:
        kwargs["filter"] = ";".join(filters)
