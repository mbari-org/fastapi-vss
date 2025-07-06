# fastapi-vss, Apache-2.0 license
# Filename: app/ops/__init__.py
# Description:  Custom exceptions for the app


def exceptions():
    # Custom exceptions
    class NotFoundException(Exception):
        def __init__(self, name: str):
            self._name = name

    class InvalidException(Exception):
        def __init__(self, name: str):
            self._name = name
