from collections import UserDict
from datetime import datetime, timedelta
import re
import pickle


class Field:
    def __init__(self, value) -> None:
        self.value = value

    def __str__(self): 
        return str(self.value)

class Name(Field): 
    def __init__(self, name=None):
        if not name: 
            raise ValueError
        super().__init__(name) 

class Phone(Field):
    def __init__(self, phone):
        pattern = '^\d{10}$'
        is_phone = re.match(pattern, phone)
 
        if not is_phone:
            raise ValueError
        super().__init__(phone)	

class Birthday(Field):
    def __init__(self, birthday):
        try:
            self.value = datetime.strptime(birthday, "%d.%m.%Y")
            
        except ValueError:
            raise ValueError ("Please, input date in correct format \
                              DD.MM.YYYY")
        
class Record: 
    def __init__(self, name) -> None:
        self.name = Name(name)
        self.birthday = None
        self.phones = []

    def add_phone(self, phone):
        for ph in self.phones: 
            if ph.value == phone:
                return
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for ph in self.phones: 
            if ph.value == phone:
                self.phones.remove(ph)
                return
        raise ValueError 
    
    def edit_phone(self, old_phone, new_phone):
        for ph in self.phones: 
            if ph.value == old_phone:
                ph.value = new_phone
                return
        raise ValueError
    
    def find_phone(self, phone):
        for ph in self.phones: 
            if ph.value == phone:
                return ph.value
        raise ValueError
    
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def show_birthday(self):
        return self.birthday

    def __str__(self):
        return f"Contact name: {self.name}, phones: {'; '.join(ph.value for ph in self.phones)}"

class AddressBook(UserDict):
    def add_record(self, record: Record):
        name = record.name.value
        self.data[name] = record

    def find(self, name) -> Record:
        return self.get(name) 
    
    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        check_period = 7
        bdays = {}

        for name in self.data:
            record = self.find(name)

            if not record.birthday:
                continue
            birthday = record.birthday.value.replace(year=today.year).date()

            if birthday < today:
                birthday = record.birthday.value.replace(year=today.year + 1).date()

            if (birthday - today).days > check_period:
                continue

            if birthday.weekday() < 5:
                bdays[name] = birthday.strftime("%d.%m.%Y")

            elif birthday.weekday() == 5:
                bdays[name] = (birthday + timedelta(2)).strftime("%d.%m.%Y")

            elif birthday.weekday() == 6:
                bdays[name] = (birthday + timedelta(1)).strftime("%d.%m.%Y")

        return bdays
    
    def delete(self, name):
        del self.data[name]

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()
        
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "The contact exists"
        except ValueError:
            return "Please enter the correct arguments"
        except IndexError:
            return "No such contacts"
    return inner

@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."

    if phone:
        record.add_phone(phone)

    return message


@input_error
def change_contact(args, book: AddressBook):

    if not args or len(args) != 2:
        raise ValueError
    
    name, new_phone = args

    record = book.find(name)
    if record:
        phones = record.phones

        if len(phones) == 1:
            phone = phones[0].value

        elif len(phones) > 1:
            print(f"The contact {name} has following phones:")

            indexes = []
            for i, number in enumerate(phones):
                print(f'{i}: {number}')
                indexes.append(str(i))

            msg = "Choose the number of phone to edit (" + ", ".join(indexes) + "): "
            key = int(input(msg))
            phone = phones[key].value
        
        else:
            return "No phones to edit"
        
        record.edit_phone(phone, new_phone)
        return f"Contact updated successfully. Number {phone} was replaced with {new_phone}."
    
    else:
        raise KeyError

@input_error
def show_contact(args, book: AddressBook):
    name = args[0]
    record = book.find(name)

    if record:
        phones = record.phones

        print_text = f"The contact {name} hase following phones:\n"

        for phone in phones:
            print_text += str(phone) + '\n'

        return print_text
    
    else:
        raise IndexError

@input_error
def show_all(book: AddressBook):
    if not book.data:
        raise IndexError
        
    print_text = ''

    for name in book.data:
        print_text += name + ':\n'

        for phone in book.data[name].phones:
            print_text += str(phone) + '\n'

    return print_text

@input_error
def add_birthday(args, book):

    if not args or len(args) != 2:
        raise ValueError
    
    name = args[0]
    birthday = args[1]
    record = book.find(name)

    if record:
        record.add_birthday(birthday)
        return "Date of birth added."
    
    else:
        raise IndexError

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    return record.birthday.value.strftime("%d.%m.%Y")

@input_error
def birthdays(book):
    birthdays = book.get_upcoming_birthdays()

    if not birthdays:
        return "No birthdays"
    
    next_bdays = [] 
    for name in birthdays:
        next_bdays.append(f'{name}: {birthdays[name]}')
        
    return '\n'.join(next_bdays)

def main():
    book = load_data()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book) 
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_contact(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
           print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Invalid command")

if __name__ == "__main__":
    main()