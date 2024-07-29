# fastapi-vss, Apache-2.0 license
# Filename: app/ops/utils.py
# Description: miscellaneous utility functions for ops

global projects


# Custom exceptions
class NotFoundException(Exception):
    def __init__(self, name: str):
        self._name = name
        super().__init__(f"{name} not found")


class InvalidException(Exception):
    def __init__(self, name: str):
        self._name = name
