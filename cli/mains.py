"""Command-line interface for the Library Inventory Manager."""
import logging
from library_manager.inventory import LibraryInventory
from library_manager.book import Book


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
    )


def prompt_nonempty(prompt: str) -> str:
    while True:
        val = input(prompt).strip()
        if val:
            return val
        print("Input cannot be empty. Try again.")


def confirm(prompt: str) -> bool:
    ans = input(prompt + " (y/n): ").strip().lower()
    return ans in ("y", "yes")


def main():
    setup_logging()
    inv = LibraryInventory("books.json")

    MENU = """
Library Menu:
1. Add Book
2. Issue Book
3. Return Book
4. View All Books
5. Search (Title / ISBN)
6. Exit
"""

    while True:
        print(MENU)
        choice = input("Choose an option (1-6): ").strip()
        try:
            if choice == "1":
                title = prompt_nonempty("Title: ")
                author = prompt_nonempty("Author: ")
                isbn = prompt_nonempty("ISBN: ")
                book = Book(title=title, author=author, isbn=isbn)
                try:
                    inv.add_book(book)
                    print("Book added successfully.")
                except ValueError as ve:
                    print(f"Cannot add book: {ve}")

            elif choice == "2":
                isbn = prompt_nonempty("ISBN to issue: ")
                book = inv.search_by_isbn(isbn)
                if not book:
                    print("No book found with that ISBN.")
                else:
                    print(book)
                    if not book.is_available():
                        print("Book already issued.")
                    else:
                        if confirm("Confirm issue?"):
                            try:
                                book.issue()
                                inv.save_to_file()
                                print("Book issued.")
                            except Exception as e:
                                print(f"Error issuing book: {e}")

            elif choice == "3":
                isbn = prompt_nonempty("ISBN to return: ")
                book = inv.search_by_isbn(isbn)
                if not book:
                    print("No book found with that ISBN.")
                else:
                    print(book)
                    if book.is_available():
                        print("Book is already available in inventory.")
                    else:
                        if confirm("Confirm return?"):
                            try:
                                book.return_book()
                                inv.save_to_file()
                                print("Book returned.")
                            except Exception as e:
                                print(f"Error returning book: {e}")

            elif choice == "4":
                books = inv.display_all()
                if not books:
                    print("No books in catalog.")
                else:
                    for b in books:
                        print(b)

            elif choice == "5":
                q = prompt_nonempty("Enter title part or ISBN to search: ")
                title_results = inv.search_by_title(q)
                isbn_result = inv.search_by_isbn(q)
                results = list(title_results)  # copy
                if isbn_result and isbn_result not in results:
                    results.append(isbn_result)
                if not results:
                    print("No results found.")
                else:
                    for b in results:
                        print(b)

            elif choice == "6":
                print("Goodbye!")
                break
            else:
                print("Invalid option — choose 1 to 6.")
        except Exception as e:
            logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()