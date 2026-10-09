# SET DEFAULT GIFT SEATS
G_GIFTED_SEAT_COUNT = 5 # temporarily set to 5
# SET SEAT DIMENSIONS
G_SEAT_ROWS = 4
G_SEAT_COLS = 6

import sys # For command line argument sys.argv
from random import randint # For random gift seat assignment
from abc import ABC, abstractmethod # OOP specs

class Customer:
    """Simple Customer object for Seat occupant"""
    id_counter:int = 0
    def __init__(self, name:str):
        self.name:str = name
        self.id:str = str(Customer.id_counter) 
        Customer.id_counter += 1

class Gift(ABC):
    """Interface for Gift implementations"""
    @abstractmethod # prinft(popcorn_gift)
    def __str__(self)->str: 
        pass  

class Seat(ABC):
    """Interface for Seat implementations"""
    @abstractmethod # return booked status
    def is_booked(self)->bool: 
        pass
    @abstractmethod # return Customer objects from seat array
    def get_customer(self)->Customer: 
        pass
    @abstractmethod # action book a seat
    def book_seat(self)->None: 
        pass
    @abstractmethod # return if Seat has a Gift
    def has_gift(self)->bool: 
        pass
    @abstractmethod # set the Seat's Gift
    def set_gift(self, gift:Gift)->None: 
        pass
    @abstractmethod # return the Seat's Gift
    def claim_gift(self)->Gift: 
        pass
    @abstractmethod # reset Seat
    def clear_seat(self)->None: 
        pass

class SeatManager(ABC):
    """Interface for SeatManagers needed by Kino clasess"""
    @abstractmethod # return seat objects from seat array
    def get_seat(self, id:str)->Seat: 
        pass
    @abstractmethod # handle booking a seat, get then book
    def book_seat(self, id:str, customer:Customer)->None: 
        pass
    @abstractmethod # reset all seats
    def clear_seats(self)->None:
        pass
    @abstractmethod # display booked unbooked for customers
    def customer_show_seats(self)->None:
        pass
    @abstractmethod # display verbose seat data for admins
    def admin_show_seats(self)->None:
        pass
    @abstractmethod # set the gifts can be used repeatedly
    def set_random_gifted_seats(self, gifted_seat_count:int)->None:
        pass

# SET WHAT THE GIFT IS
class PopcornGift(Gift):
    def __str__(self):
        return "FREE POPCORN 🍿"

class BeerGift(Gift):
    def __str__(self):
        return "FREE BEER 🍺"

class KinoSeat(Seat):
    """A KinoSeat that itself stores the entirety of data relevant to a Seat""" 
    def __init__(self):
        self.__customer:Customer = None
        self.__gift = None

    def get_customer(self): 
        return self.__customer

    def is_booked(self): 
        return self.__customer is not None

    def book_seat(self, customer:Customer): 
        """Book a seat, raise an error if seat already booked"""
        if not isinstance(customer, Customer):
            raise TypeError(f"!!! Customer must be a Customer instance.")
        if self.is_booked(): 
            raise ValueError(f"!!! Seat is already booked by {self.__customer.name} #{self.__customer.id}.")
        self.__customer = customer

    def has_gift(self): 
        return self.__gift is not None

    def set_gift(self, gift:Gift):
        """Set the Gift, raise an error if not a Gift instance"""
        if not isinstance(gift, Gift): 
            raise TypeError(f"!!! gift must be a Gift instance.")
        self.__gift = gift
        
    def claim_gift(self):
        """Return whatever is in this KinoSeat's gift and dis-own the gift object"""
        if not self.has_gift(): 
            return None
        temp = self.__gift # Note python variables store the Gift object as mutable references
        self.__gift = None # KinoSeat object intentionally loses the reference to the Gift Object
        return temp # Gift reference stored in temp is returned, Gift ownership passed outside

    def clear_seat(self):
        """Reset KinoSeat"""
        self.__customer = None
        self.__gift = None

class Kino2DSeatManager(SeatManager):
    """Manage Seats for Kino classes with 2D lists for storage"""
    def __init__(self, rows_:int, cols_:int):
        self.__rows:int = rows_
        self.__cols:int = cols_ 
        self.__seat_count:int = self.__rows * self.__cols
        self.__seat_list:list = [[KinoSeat() for _ in range(self.__cols)] for _ in range(self.__rows)]
        self.__gift_count:int = 0
    
    def __map_seat(self, key:str):
        if not isinstance(key, str):
            raise TypeError(f"!!! Seat ID must be a string.")
        
        key = key.strip().upper()
        split_at = next((i for i, char in enumerate(key) if char.isdigit()), -1)
        if split_at <= 0 or not key[:split_at].isalpha() or not key[split_at:].isdigit():
            raise ValueError(f"!!! Invalid seat ID {key}; expected letters followed by a number, e.g. 'A1'.")
        
        alphabet = key[:split_at]
        numeric = "0" + key[split_at:]
        
        row = 0
        # A is 0, Z is 25, AA is 26 ...
        # A < Z < AA < AZ < BA < BZ ...
        for a in alphabet:
            row = (row*26) + (ord(a) - ord("A") + 1)
        row -= 1 # make it 0 indexed
        col = int(numeric) - 1
        return row, col

    def __seat_coord_to_string_id(self, row:int, col:int):
        num = row + 1 # temporary offset to prevent num -= 1 going out of idx
        alphabet = ""
        # 0 is A, 25 is Z, 26 is AA ...
        # A < Z < AA < AZ < BA < BZ ...
        while num > 0:
            num -= 1 # there is no "0" character, just A to Z 26 characters
            alphabet = chr(num % 26 + ord("A")) + alphabet
            num //= 26
        return alphabet + str(col + 1)
        
    def get_seat(self, id:str):
        """Return the reference to a Seat object, what is returned is mutable so be careful"""
        row, col = self.__map_seat(id)
        if not (0 <= row < self.__rows and 0 <= col < self.__cols):
            raise ValueError(f"!!! Seat ID {id} is outside the seating area ({self.__rows} rows x {self.__cols} columns).")
        return self.__seat_list[row][col]

    def book_seat(self, id:str, customer:Customer):
        """Book a seat; booking errors are handled by the caller."""
        seat:KinoSeat = self.get_seat(id)
        seat.book_seat(customer)
        print(f"Successfully booked seat {id} for {customer.name} #{customer.id}.")

    def clear_seats(self):
        for row in self.__seat_list:
            for seat in row: 
                seat.clear_seat()
        print("Successfully cleared all seats.")
        
    def set_random_gifted_seats(self, gifted_seat_count:int):
        """Set the randomized gifted seats"""
        if not isinstance(gifted_seat_count, int):
            raise TypeError(f"!!! gifted_seat_count must be an integer.")
        gifted_seat_count = min(gifted_seat_count, self.__seat_count)
        self.__gift_count = gifted_seat_count
        while gifted_seat_count > 0:
            row = randint(0, self.__rows - 1)
            col = randint(0, self.__cols - 1)
            seat:KinoSeat = self.__seat_list[row][col]
            if not seat.has_gift():
                gift = PopcornGift() if (row + col) % 2 == 0 else BeerGift()
                seat.set_gift(gift)
                gifted_seat_count -= 1
    
    def __print_kinoleinwand(self):
        total_grid_width = 1 + (9 * self.__cols)
        inner_width = total_grid_width - 2
        
        top = "┌" + "─" * inner_width + "┐"
        mid = "│" + "KINOLEINWAND".center(inner_width) + "│"
        bot = "└" + "─" * inner_width + "┘"
        
        print(f"{top}\n{mid}\n{bot}")
        
    def customer_show_seats(self):
        """Display seats config for customers, simply booked or unbooked"""
        self.__print_kinoleinwand()

        top = "┌" + "┬".join(["────────"] * self.__cols) + "┐" 
        mid = "├" + "┼".join(["────────"] * self.__cols) + "┤" 
        bot = "└" + "┴".join(["────────"] * self.__cols) + "┘" 
        for row in range(self.__rows):
            print(top if row == 0 else mid)
            print("│", end="")
            for col in range(self.__cols):
                seat:Seat = self.__seat_list[row][col]
                txt = "booked" if seat.is_booked() else self.__seat_coord_to_string_id(row, col)
                print(f" {txt:^6} │", end="")
            print()
        print(bot)

    def admin_show_seats(self):
        """Display seats config for admins, verbose"""
        self.__print_kinoleinwand()

        top = "┌" + "┬".join(["────────"] * self.__cols) + "┐"
        mid = "├" + "┼".join(["────────"] * self.__cols) + "┤"
        bot = "└" + "┴".join(["────────"] * self.__cols) + "┘"
        booked_seats = 0
        gifted_seats = 0
        for row in range(self.__rows):
            print(top if row == 0 else mid)
            print("│", end="")
            for col in range(self.__cols):
                seat:Seat = self.__seat_list[row][col]
                booked_string = ""
                if seat.is_booked():
                    booked_seats += 1
                    booked_string = "booked"
                print(f" {booked_string:^6} │", end="")
            print()

            print("│", end="")
            for col in range(self.__cols):
                print(f" {self.__seat_coord_to_string_id(row, col):^6} │", end="")
            print()

            print("│", end="")
            for col in range(self.__cols):
                seat:Seat = self.__seat_list[row][col]
                gifted_string = ""
                if seat.has_gift():
                    gifted_seats += 1
                    gifted_string = "=GIFT="
                print(f" {gifted_string:^6} │", end="")
            print()
        print(bot)
        print(f"Booked/Total Seats    : {booked_seats}/{self.__seat_count}")
        print(f"Unclaimed/Total Gifts : {gifted_seats}/{self.__gift_count}")

class Ticket():
    def __init__(self, customer:Customer, booked_seats:dict):
        self.__customer = customer
        self.__booked_seats = booked_seats
        
    def get_customer(self):
        return self.__customer

    def get_booked_seats(self):
        return self.__booked_seats

    def print_ticket(self):
        title_str    = "KinoKleinSpass"
        customer_str = f"Customer name : {self.__customer.name} #{self.__customer.id}"
        seat_str     = f"Seat number   : {', '.join(str(key) for key in self.__booked_seats.keys())}"

        gift_str = []
        for seat_id, seat in self.__booked_seats.items():
            gift = seat.claim_gift()
            if gift is None: continue
            gift_str.append(f"CONGRATS you got {gift} x1 from seat {seat_id} !")

        print("#" * 60)
        print(f"## {title_str:<54} ##")
        print(f"## {customer_str:<54} ##")
        print(f"## {seat_str:<54} ##")
        if gift_str:
            for s in gift_str:
                print(f"## {s:^54} ##")
        print("#" * 60)

class Kino:
    def __init__(self, seat_rows:int, seat_cols:int):
        self.seat_manager = Kino2DSeatManager(seat_rows, seat_cols)

    def start(self, gifted_seat_count: int):
        self.seat_manager.set_random_gifted_seats(gifted_seat_count)
        self.seat_manager.customer_show_seats()

        while True:
            print("\nMain Menu:")
            print("1. Buy Ticket")
            print("2. Admin View")
            print("3. Start Film")
            print("4. Exit")

            choice = input("Choose menu: ").strip()

            if choice == "1":
                customer = Customer(input("Customer name: ").strip())
                self.seat_manager.customer_show_seats()
                seats_to_book = input("Choose your seats (example A1): ").strip().upper().split(",")

                # collect the seats to book to make a ticket
                booked_seats = {}

                for seat_str in seats_to_book:
                    seat_id = seat_str.strip()
                    try:
                        if seat_id in booked_seats:
                            raise ValueError(f"!!! Cannot book seat {seat_id} repeatedly.")
                        
                        seat = self.seat_manager.get_seat(seat_id) 
                        if seat.is_booked():
                            booked_by = seat.get_customer()
                            raise ValueError(f"!!! Seat {seat_id} is already booked by {booked_by.name} #{booked_by.id}.")
                        self.seat_manager.book_seat(seat_id, customer)
                        # if successfully booked a seat
                        booked_seats[seat_id] = seat
                    except (TypeError, ValueError) as err: 
                        print(err)
                        continue

                # Create a ticket
                if not booked_seats:
                    print("No valid seats booked; ticket not issued.")
                    continue
                ticket = Ticket(customer, booked_seats)
                ticket.print_ticket()

            elif choice == "2":
                self.seat_manager.admin_show_seats()

            elif choice == "3":
                print(f"\n!!! FILM STARTS !!! *ceritanya filmnya mulai ...*")
                print(f"\n!!! FILM ENDS !!! *kemudian ceritanya filmnya beres ...*")
                self.seat_manager.clear_seats()
                print(f"\n!!! CINEMA OPENS !!! *cinema berulang ...*")
                self.seat_manager.set_random_gifted_seats(gifted_seat_count)

            elif choice == "4":
                print("End of session.")
                break

            else:
                print("Choose from 1 to 4.")

if __name__ == "__main__":
    kino = Kino(G_SEAT_ROWS, G_SEAT_COLS)
    # COMMAND LINE ARGUMENTS ex: "... kleinspass_kino.py <int>"
    # whatever is in ... this program only gets the arguments :
    # "kleinspass_kino.py" at idx 0 of sys.argv list
    # <int> at idx 1 of sys.argv list
    # try get and convert argument string at sys.argv[1] to integer
    try: G_GIFTED_SEAT_COUNT = int(sys.argv[1])
    # ignore IndexError when sys.argv[1] doesn't exist ex: "... kleinspass_kino.py"
    # ignore ValueError when sys.argv[1] is not convertible to int
    except Exception: pass

    # majority of program runtime is in the start method ... 
    kino.start(G_GIFTED_SEAT_COUNT)
