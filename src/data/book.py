from dataclasses import dataclass


@dataclass
class Book:
    """ Novel book information """
    title: str
    author: str