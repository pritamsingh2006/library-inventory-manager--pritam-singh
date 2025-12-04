"""LibraryInventory: manages list of Book objects and JSON persistence."""
import json
from pathlib import Path
from typing import List, Union
import logging
from .book import Book

logger = logging.getLogger(__name__)


class LibraryInventory:
    def __init__(self, json_path: Union[str, Path] = "books.json"):
        self.json_path = Path(json_path)
        self.books: List[Book] = []
        self.load_from_file()

    def add_book(self, book: Book):
        if any(b.isbn == book.isbn for b in self.books):
            raise ValueError("A book with this ISBN already exists.")
        self.books.append(book)
        logger.info(f"Added book: {book.title} (ISBN: {book.isbn})")
        self.save_to_file()

    def search_by_title(self, title_part: str):
        title_part = title_part.lower().strip()
        return [b for b in self.books if title_part in b.title.lower()]

    def search_by_isbn(self, isbn: str):
        isbn = isbn.strip()
        for b in self.books:
            if b.isbn == isbn:
                return b
        return None

    def display_all(self):
        return list(self.books)

    def save_to_file(self):
        """Save catalog to JSON safely (write temp then replace)."""
        try:
            data = [b.to_dict() for b in self.books]
            parent = self.json_path.parent
            if not parent.exists():
                parent.mkdir(parents=True, exist_ok=True)

            tmp_path = self.json_path.with_suffix(self.json_path.suffix + ".tmp")
            tmp_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

            # If original exists, create a backup before replacing
            if self.json_path.exists():
                backup = self.json_path.with_suffix(self.json_path.suffix + ".bak")
                # remove old backup if present
                if backup.exists():
                    backup.unlink()
                self.json_path.replace(backup)  # move original -> backup

            # move tmp -> original (atomic on same filesystem)
            tmp_path.replace(self.json_path)

            # remove backup after successful write (optional; comment out if you want to keep backups)
            if 'backup' in locals() and backup.exists():
                backup.unlink()

            logger.info("Catalog saved to file.")
        except Exception as e:
            logger.error(f"Failed to save catalog: {e}")

    def load_from_file(self):
        """Load catalog from JSON. Handle missing/corrupted files gracefully."""
        try:
            if not self.json_path.exists():
                self.books = []
                return
            content = self.json_path.read_text(encoding="utf-8")
            data = json.loads(content)
            # validate items are mappings with required keys
            self.books = [Book(**item) for item in data]
            logger.info("Catalog loaded from file.")
        except json.JSONDecodeError:
            logger.error("JSON file corrupted — starting with empty catalog.")
            # keep a corrupted copy for manual inspection
            try:
                corrupted = self.json_path.with_suffix(self.json_path.suffix + ".corrupt")
                if not corrupted.exists():
                    self.json_path.replace(corrupted)
            except Exception:
                # ignore backup failure
                pass
            self.books = []
        except Exception as e:
            logger.error(f"Unexpected error while loading catalog: {e}")
            self.books = []