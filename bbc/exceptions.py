class CategoryNotFound(Exception):
    """
    raises when the asked category is not found
    """

class APIError(Exception):
    """
    raises when API returned no news
    """