def exceptions():
    # Custom exceptions
    class NotFoundException(Exception):
        def __init__(self, name: str):
            self._name = name

    class InvalidException(Exception):
        def __init__(self, name: str):
            self._name = name
