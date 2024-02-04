from typing import Any, Generic, Optional, Sequence, TypeVar

from fastapi import Query
from fastapi_pagination.bases import AbstractPage, AbstractParams, RawParams
from pydantic import BaseModel
from typing_extensions import Self


class JSONAPIParams(BaseModel, AbstractParams):
    offset: int = Query(0, ge=0, alias="offset")
    limit: int = Query(10, ge=1, le=100, alias="limit")

    def to_raw_params(self) -> RawParams:
        return RawParams(limit=self.limit, offset=self.offset)


class JSONAPIPageInfoMeta(BaseModel):
    total_count: int
    count: int
    offset: int
    limit: int


class JSONAPIPageMeta(BaseModel):
    page: JSONAPIPageInfoMeta


T = TypeVar("T")


class JSONAPIPage(AbstractPage[T], Generic[T]):
    data: Sequence[T]
    meta: JSONAPIPageMeta

    __params_type__ = JSONAPIParams

    @classmethod
    def create(
            cls,
            items: Sequence[T],
            params: AbstractParams,
            *,
            total: Optional[int] = None,
            **kwargs: Any,
    ) -> Self:
        assert isinstance(params, JSONAPIParams)
        assert total is not None

        return cls(
            data=items,
            meta={
                "page": {
                    "total_count": total,
                    "count": len(items),
                    "offset": params.offset,
                    "limit": params.limit,
                }
            },
            **kwargs,
        )


class JSONAPIResponse(BaseModel, Generic[T]):
    data: T

    @classmethod
    def create(cls, data: T) -> Self:
        return cls(data=data)


class JSONAPIError(BaseModel):
    status: str
    title: str
    detail: str
    code: Optional[str] = None
    source: Optional[dict[str, Any]] = None
    meta: Optional[dict[str, Any]] = None


class JSONAPIErrorResponse(BaseModel):
    errors: Sequence[JSONAPIError]

    @classmethod
    def create(cls, errors: Sequence[JSONAPIError]) -> Self:
        return cls(errors=errors)
