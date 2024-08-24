import pickle
from collections import UserDict
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Please use DD.MM.YYYY.")
        self.value = value

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def set_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def add_phone(self, phone_value):
        phone = Phone(phone_value)
        self.phones.append(phone)

    def delete_phone(self, phone_value):
        self.phones = [phone for phone in self.phones if phone.value != phone_value]

    def update_phone(self, old_phone, new_phone):
        for idx, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[idx] = Phone(new_phone)
                return True
        raise ValueError(f"Phone number {old_phone} not found.")

    def __str__(self):
        phones = ', '.join(phone.value for phone in self.phones)
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Name: {self.name.value}, phones: {phones}{birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def search(self, name):
        return self.data.get(name)

    def remove_record(self, name):
        return self.data.pop(name, None)

    def upcoming_birthdays(self):
        today = datetime.now().date()
        result = []
        for record in self.data.values():
            if record.birthday:
                birthday_this_year = datetime.strptime(record.birthday.value, "%d.%m.%Y").replace(year=today.year).date()
                if today <= birthday_this_year <= today + timedelta(days=7):
                    if birthday_this_year.weekday() >= 5:
                        birthday_this_year += timedelta(days=(7 - birthday_this_year.weekday()))
                    result.append({
                        "name": record.name.value,
                        "birthday": birthday_this_year.strftime("%d.%m.%Y")
                    })
        return result

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())

def input_error(handler):
    def wrapper(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except (IndexError, ValueError) as error:
            return f"Error: {str(error)}"
    return wrapper

@input_error
def add_contact(args, book: AddressBook):
    name, phone = args[:2]
    record = book.search(name)
    if record:
        record.add_phone(phone)
        return f"Phone added to {name}."
    else:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return f"Contact {name} created."

@input_error
def change_phone(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.search(name)
    if record and record.update_phone(old_phone, new_phone):
        return f"Phone number updated for {name}."
    return "Contact or phone not found."

@input_error
def show_phones(args, book: AddressBook):
    name = args[0]
    record = book.search(name)
    if record:
        return f"{name}: {', '.join(phone.value for phone in record.phones)}"
    return "Contact not found."

@input_error
def display_all(book: AddressBook):
    return str(book) if book.data else "Address book is empty."

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.search(name)
    if record:
        record.set_birthday(birthday)
        return f"Birthday set for {name}."
    return "Contact not found."

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.search(name)
    if record:
        return f"{name}'s birthday: {record.birthday.value}" if record.birthday else "Birthday not set."
    return "Contact not found."

@input_error
def birthdays(book: AddressBook):
    upcoming = book.upcoming_birthdays()
    if upcoming:
        return "\n".join(f"{item['name']}: {item['birthday']}" for item in upcoming)
    return "No upcoming birthdays."

def parse_command(input_str):
    parts = input_str.split()
    return parts[0], parts[1:]

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернуть новую адресную книгу, если файл не найден

def main():
    book = load_data()

    print("Welcome to the AddressBook Assistant!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_command(user_input)

        if command in ["exit", "close"]:
            save_data(book)
            print("Goodbye!")
            break

        elif command == "hello":
            print("How can I assist you today?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_phone(args, book))

        elif command == "phone":
            print(show_phones(args, book))

        elif command == "all":
            print(display_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Unknown command. Please try again.")

if __name__ == "__main__":
    main()

