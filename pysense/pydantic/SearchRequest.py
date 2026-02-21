from pysense.pydantic.pydantic_base import UIAwareMixin


class SearchRequest(UIAwareMixin):
    current: int
    rowCount: int
    sort: dict
    searchPhrase: str

    @staticmethod
    def search(searchPhrase: str, current: int = 1, rowCount: int=1000, sort:dict=None) -> 'SearchRequest':
        if sort is None:
            sort = {}
        return SearchRequest(current=current, rowCount=rowCount, sort=sort, searchPhrase=searchPhrase)
