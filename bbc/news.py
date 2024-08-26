import bbc
import requests
import bbc.exceptions
import typing

HEADERS = {
    "User-Agent": "BBC News Wrapper (PY)"
}

class News():
    def __init__(self, response: dict) -> None:
        self.raw_response = response
    
    def news_category(self, category_name: str) -> list[dict]:
        """
        Returns news from specified category.

        :param category_name: Specific category name
        :raise CategoryNotFound: When specified category cannot be found
        """
        category = category_name
        if category in self.raw_response:
            return self.raw_response[category]
        else:
            raise bbc.exceptions.CategoryNotFound(f"Cannot find the '{category}' category.")
    
    def news_categories(self) -> list:
        """
        Returns all the category titles.

        :param category_name: Specific category name
        """
        categories = list(self.raw_response.keys())

        return categories

def get_news(language: typing.Union[str, bbc.Languages]) -> News:
    """
    Returns all news of a language.

    :param language: Language name (`str`, `bbc.Languages`)

    :raise AttributeError: raises when on language  mismatch 
    :raise bbc.exceptions.APIError: raises on API related error
    :return: :class:`News <bbc.news.News>` object
    :rtype: bbc.news.News
    """
    if type(language) != str:
        raise AttributeError(f"Language cannot be a `{type(language).__name__}`, please use `bbc.Languages` for choosing language!")
    if language.title() not in bbc.languages.__languages__:
        raise AttributeError(f"Invalid language `{type(language).__name__}`, please use `bbc.Languages` for choosing language!")
    
    _res = requests.get(f"https://bbc-api.vercel.app/news?lang={language}", headers=HEADERS)
    if _res.status_code != 200:
        raise bbc.exceptions.APIError("API didn't respond properly!")
    _res = _res.json()
    _res.pop("status") if "status" in _res else _res
    _res.pop("elapsed time") if "elapsed time" in _res else _res
    _res.pop("timestamp") if "timestamp" in _res else _res
    if not _res:
        raise bbc.exceptions.APIError(f"API didn't respond with any news! Please create an issue at {bbc.__bug_report__} or mail at {bbc.__author_email__}")
    return News(_res)


def get_latest_news(language: typing.Union[str, bbc.Languages]) -> list[dict]:
    """
    Returns all latest news of a language.

    :param language: Language name (`str`, `bbc.Languages`)
    
    :raise AttributeError: raises when on language type mismatch 
    :raise bbc.exceptions.APIError: raises on API related error
    :return: list[dict]
    """
    if type(language) != str:
        raise AttributeError(f"Language cannot be a `{type(language).__name__}`, please use `bbc.Languages` for choosing language!")
    if language.title() not in bbc.languages.__languages__:
        raise AttributeError(f"Invalid language `{type(language).__name__}`, please use `bbc.Languages` for choosing language!")
    
    _res = requests.get(f"https://bbc-api.vercel.app/latest?lang={language}", headers=HEADERS)
    if _res.status_code != 200:
        raise bbc.exceptions.APIError("API didn't respond properly!")
    _res = _res.json()
    _res.pop("status") if "status" in _res else _res
    _res.pop("elapsed time") if "elapsed time" in _res else _res
    _res.pop("timestamp") if "timestamp" in _res else _res
    if not _res:
        raise bbc.exceptions.APIError(f"API didn't respond with any news! Please create an issue at {bbc.__bug_report__} or mail at {bbc.__author_email__}")
    
    return _res[list(_res.keys())[0]]