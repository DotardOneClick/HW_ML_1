from datetime import datetime, timedelta, date
from collections import UserDict
import pickle


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        self.validate_phone()

    def validate_phone(self):
        if not self.value.isdigit() or len(self.value) != 10:
            raise ValueError('Invalid phone number format.')

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError('Invalid date format. Use DD.MM.YYYY')

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        phone_obj = Phone(phone)
        self.phones.append(phone_obj)

    def remove_phone(self, phone):
        for phone_obj in self.phones:
            if phone_obj.value == phone:
                self.phones.remove(phone_obj)
                return True
        return False

    def edit_phone(self, old_phone, new_phone):
        if not new_phone.isdigit() or len(new_phone) != 10:
            raise ValueError('Invalid phone number format.')
        for phone_obj in self.phones:
            if phone_obj.value == old_phone:
                phone_obj.value = new_phone
                return True
        return False

    def find_phone(self, phone):
        for phone_obj in self.phones:
            if phone_obj.value == phone:
                return phone_obj
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def show_birthday(self):
        if self.birthday:
            return str(self.birthday)
        else:
            return 'No birtday set.'

    def __str__(self):
        return f'Contact name: {self.name.value}, phones: {"; ".join(str(p) for p in self.phones)}, birthday: {self.show_birthday()}'

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        return self.data.pop(name, None)

    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = datetime.combine(date.today(), datetime.min.time())
        next_week = today + timedelta(days=days)

        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                if today <= birthday_this_year <= next_week:
                    congratulation_date_str = birthday_this_year.strftime('%d.%m.%Y')
                    upcoming_birthdays.append((record.name.value, congratulation_date_str))

        return upcoming_birthdays

def handle_command(command, args, book):
    if command in ['close', 'exit']:
        return "Goodbye!"

    elif command == 'hello':
        return "Hello! How can I assist you today?"

    elif command == 'add':
        if len(args) != 2:
            return 'Usage: add [name] [phone]'
        else:
            name, phone = args
            record = book.find(name)
            if record:
                record.add_phone(phone)
                return f'Phone number added to existing contact {name}.'
            else:
                new_record = Record(name)
                new_record.add_phone(phone)
                book.add_record(new_record)
                return f'New contact {name} added with phone number {phone}.'

    elif command == 'change':
        if len(args) != 2:
            return 'Usage: change [name] [new_phone]'
        else:
            name, new_phone = args
            record = book.find(name)
            if record:
                if record.edit_phone(record.phones[0].value, new_phone):
                    return f'Phone number changed for contact {name}.'
                else:
                    return f'No phone number found for contact {name}.'
            else:
                return f'Contact {name} not found.'

    elif command == 'phone':
        if len(args) != 1:
            return 'Usage: phone [name]'
        else:
            name = args[0]
            record = book.find(name)
            if record:
                return f'Phone numbers for contact {name}: {", ".join(str(phone) for phone in record.phones)}.'
            else:
                return f'Contact {name} not found.'

    elif command == 'all':
        if book:
            return '\n'.join(str(record) for record in book.data.values())
        else:
            return 'No contacts in the address book.'

    elif command == 'add-birthday':
        if len(args) != 2:
            return 'Usage: add-birthday [name] [birthday]'
        else:
            name, birthday = args
            record = book.find(name)
            if record:
                record.add_birthday(birthday)
                return f'Birthday added for contact {name}.'
            else:
                return f'Contact {name} not found.'

    elif command == 'show-birthday':
        if len(args) != 1:
            return 'Usage: show-birthday [name]'
        else:
            name = args[0]
            record = book.find(name)
            if record:
                return f'Birthday for contact {name}: {record.show_birthday()}.'
            else:
                return f'Contact {name} not found.'

    elif command == 'birthdays':
        upcoming_birthdays = book.get_upcoming_birthdays()
        if upcoming_birthdays:
            return 'Upcoming birthdays:\n' + '\n'.join(f'{name}: {date}' for name, date in upcoming_birthdays)
        else:
            return 'No upcoming birthdays.'

    else:
        return 'Invalid command.'
    
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main():
    book = load_data()
    print('Welcome to the assistant bot!')
    while True:
        user_input = input('Enter a command >>> ')
        command, *args = user_input.split()

        response = handle_command(command, args, book)
        print(response)

        if command in ['close', 'exit']:
            save_data(book)
            break

if __name__ == '__main__':
    main()
