"""Book class definition."""
from dataclasses import dataclass, asdict


@dataclass
class Book:
    title: str
    author: str
    isbn: str
    status: str = "available"  # either "available" or "issued"

    def __str__(self):
        return f"{self.title} by {self.author} (ISBN: {self.isbn}) - {self.status}"

    def to_dict(self):
        return asdict(self)

    def is_available(self):
        return self.status == "available"

    def issue(self):
        if not self.is_available():
            raise ValueError("Book already issued")
        self.status = "issued"

    def return_book(self):
        if self.is_available():
            raise ValueError("Book is not issued")
        self.status = "available"