# https://github.com/smatthews75-hub/kleinspass_kino

# by team Kino Cicak 5 Balon 5 Dinding Meledak :
# Stephen Matthews      252404175
# Neil Yapson           252407832
# Joshua Christopher    252302347

# SET DEFAULT GIFT SEATS
G_GIFTED_SEAT_COUNT:int = 5
# SET SEAT DIMENSIONS
G_SEAT_ROWS:int = 4
G_SEAT_COLS:int = 6

import sys # For command line argument sys.argv
from random import randint # For random gift seat assignment
from abc import ABC, abstractmethod # OOP specs

class Customer:
    """Simple Customer object for Seat occupant"""
    __id_counter:int = 0
    def __init__(self, name:str) -> None:
        self.__name:str = name
        self.__id:str = str(Customer.__id_counter) 
        Customer.__id_counter += 1
    # Read Only values
    def get_name(self) -> str:
        return self.__name
    def get_id(self) -> str:
        return self.__id


class Gift(ABC): # Actual demonstration of interface contracts
    """Interface for Gift implementations"""
    @abstractmethod # enables print(gift)
    def __str__(self) -> str: 
        pass
    @abstractmethod # consume actions differ 
    def consume(self) -> None:
        pass
        
    

class Seat(ABC): # Contracts for later IMAX seat implementations or smth
    """Interface for Seat implementations"""
    @abstractmethod # return booked status
    def is_booked(self) -> bool: 
        pass
    @abstractmethod # return Customer objects from seat array
    def get_customer(self) -> Customer | None: 
        pass
    @abstractmethod # action book a seat
    def book_seat(self, customer:Customer) -> None: 
        pass
    @abstractmethod # return if Seat has a Gift
    def has_gift(self) -> bool: 
        pass
    @abstractmethod # set the Seat's Gift
    def set_gift(self, gift:Gift) -> None: 
        pass
    @abstractmethod # return the Seat's Gift
    def claim_gift(self) -> Gift | None: 
        pass
    @abstractmethod # reset Seat
    def clear_seat(self) -> None: 
        pass


class SeatManager(ABC): # Contracts for later more storage effective 1D array seatmanager implementations
    """Interface for SeatManagers needed by Kino clasess"""
    @abstractmethod # return seat objects from seat array
    def get_seat(self, id:str) -> Seat: 
        pass
    @abstractmethod # handle booking a seat, get then book
    def book_seat(self, id:str, customer:Customer) -> None: 
        pass
    @abstractmethod # reset all seats
    def clear_seats(self) -> None:
        pass
    @abstractmethod # display booked unbooked for customers
    def customer_show_seats(self) -> None:
        pass
    @abstractmethod # display verbose seat data for admins
    def admin_show_seats(self) -> None:
        pass
    @abstractmethod # set the gifts can be used repeatedly
    def set_random_gifted_seats(self, gifted_seat_count:int) -> None:
        pass


# SET WHAT THE GIFT IS
class PopcornGift(Gift):
    def __str__(self) -> str:
        return "FREE POPCORN 🍿"
    def consume(self) -> None:
        print("Crunch " * 3)


class BeerGift(Gift):
    def __str__(self) -> str:
        return "FREE BEER 🍺"
    def consume(self) -> None:
        print("Slurp " * 3)


class KinoSeat(Seat):
    """A KinoSeat that itself stores the entirety of data relevant to a Seat""" 
    def __init__(self) -> None:
        self.__customer:Customer|None = None
        self.__gift:Gift|None = None

    def get_customer(self) -> Customer | None: 
        return self.__customer

    def is_booked(self) -> bool: 
        return self.__customer is not None

    def book_seat(self, customer:Customer) -> None: 
        """Book a seat, raise an error if seat already booked"""
        if not isinstance(customer, Customer):
            raise TypeError(f"!!! Customer must be a Customer instance.")
        if self.is_booked(): 
            raise ValueError(f"!!! Seat is already booked by {self.__customer.get_name()} #{self.__customer.get_id()}.")
        self.__customer = customer

    def has_gift(self) -> bool: 
        return self.__gift is not None

    def set_gift(self, gift:Gift) -> None:
        """Set the Gift, raise an error if not a Gift instance"""
        if not isinstance(gift, Gift): 
            raise TypeError(f"!!! gift must be a Gift instance.")
        self.__gift = gift
        
    def claim_gift(self) -> Gift | None:
        """Return whatever is in this KinoSeat's gift and dis-own the gift object"""
        if not self.has_gift(): 
            return None
        temp = self.__gift # Note python variables store the Gift object as mutable references
        self.__gift = None # KinoSeat object intentionally loses the reference to the Gift Object
        return temp # Gift reference stored in temp is returned, Gift ownership passed outside

    def clear_seat(self) -> None:
        """Reset KinoSeat"""
        self.__customer = None
        self.__gift = None


class Kino2DSeatManager(SeatManager):
    """Manage Seats for Kino classes with 2D lists for storage"""
    def __init__(self, rows_:int, cols_:int) -> None:
        self.__rows:int = rows_
        self.__cols:int = cols_ 
        self.__seat_count:int = self.__rows * self.__cols
        self.__seat_list: list[list[KinoSeat]] = [[KinoSeat() for _ in range(self.__cols)] for _ in range(self.__rows)]
        self.__gift_count:int = 0
    
    def __map_seat(self, key: str) -> tuple[int, int]:
        if not isinstance(key, str):
            raise TypeError("!!! Seat ID must be a string.")
        key = key.strip().upper()
        
        split_at = 0
        for char in key:
            if char.isdigit(): 
                break
            split_at += 1
        else:
            # 'else' triggers if loop finishes without hitting 'break' (case: no digits found)
            raise ValueError(f"!!! Invalid seat ID '{key}'; expected letters followed by a number, e.g. 'A1'.")
        
        alphabet = key[:split_at]
        numeric = key[split_at:]
        
        if not alphabet.isalpha() or not numeric.isdigit():
            raise ValueError(f"!!! Invalid seat ID '{key}'; expected letters followed by a number, e.g. 'A1'.")
        
        row = 0
        # A is 0, Z is 25, AA is 26 ...
        # A < Z < AA < AZ < BA < BZ ...
        for a in alphabet:
            row = (row*26) + (ord(a) - ord("A") + 1)
        # - 1 to make row, col 0 indexed
        return row - 1, int(numeric) - 1

    def __seat_coord_to_string_id(self, row:int, col:int) -> str:
        num = row + 1 # temporary offset to prevent num -= 1 going out of idx
        alphabet = ""
        # 0 is A, 25 is Z, 26 is AA ...
        # A < Z < AA < AZ < BA < BZ ...
        while num > 0:
            num -= 1 # there is no "0" character, just A to Z 26 characters
            alphabet = chr(num % 26 + ord("A")) + alphabet
            num //= 26
        return alphabet + str(col + 1)
        
    def get_seat(self, id:str) -> KinoSeat:
        """Return the reference to a Seat object, what is returned is mutable so be careful"""
        row, col = self.__map_seat(id)
        if not (0 <= row < self.__rows and 0 <= col < self.__cols):
            raise ValueError(f"!!! Seat ID {id} is outside the seating area ({self.__rows} rows x {self.__cols} columns).")
        return self.__seat_list[row][col]

    def book_seat(self, id:str, customer:Customer) -> None:
        """Book a seat; booking errors are handled by the caller."""
        seat:KinoSeat = self.get_seat(id)
        seat.book_seat(customer)
        print(f"Successfully booked seat {id} for {customer.get_name()} #{customer.get_id()}.")

    def clear_seats(self) -> None:
        for row in self.__seat_list:
            for seat in row: 
                seat.clear_seat()
        print("Successfully cleared all seats.")
        
    def set_random_gifted_seats(self, gifted_seat_count:int) -> None:
        """Set the randomized gifted seats"""
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
    
    def __print_kinoleinwand(self) -> None:
        total_grid_width = 1 + (9 * self.__cols)
        inner_width = total_grid_width - 2
        top = "┌" + "─" * inner_width + "┐"
        mid = "│" + "KINOLEINWAND".center(inner_width) + "│"
        bot = "└" + "─" * inner_width + "┘"
        print(f"{top}\n{mid}\n{bot}")
        
    def customer_show_seats(self) -> None:
        """Display seats config for customers, simply booked or unbooked"""
        self.__print_kinoleinwand()

        top = "┌" + "┬".join(["────────"] * self.__cols) + "┐" 
        mid = "├" + "┼".join(["────────"] * self.__cols) + "┤" 
        bot = "└" + "┴".join(["────────"] * self.__cols) + "┘" 
        for row in range(self.__rows):
            print(top if row == 0 else mid)
            print("│", end="")
            for col in range(self.__cols):
                seat:KinoSeat = self.__seat_list[row][col]
                txt = "booked" if seat.is_booked() else self.__seat_coord_to_string_id(row, col)
                print(f" {txt:^6} │", end="")
            print()
        print(bot)

    def admin_show_seats(self) -> None:
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
                seat:KinoSeat = self.__seat_list[row][col]
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
                seat:KinoSeat = self.__seat_list[row][col]
                gifted_string = ""
                if seat.has_gift():
                    gifted_seats += 1
                    gifted_string = "=GIFT="
                print(f" {gifted_string:^6} │", end="")
            print()
        print(bot)
        print(f"Booked/Total Seats    : {booked_seats}/{self.__seat_count}")
        print(f"Unclaimed/Total Gifts : {gifted_seats}/{self.__gift_count}")


class Ticket:
    def __init__(self, customer_name:str, customer_id:str, booked_seats:dict[str, Seat]) -> None:
        self.__customer_name:str = customer_name
        self.__customer_id:str = customer_id
        self.__booked_seats:dict[str, Seat] = dict(booked_seats) # copy to get full ownership

    def print_ticket(self) -> None:
        title_str    = "KinoKleinSpass"
        customer_str = f"Customer name : {self.__customer_name} #{self.__customer_id}"
        seat_str     = f"Seat number   : {', '.join(str(key) for key in self.__booked_seats.keys())}"

        gift_str:list[str] = []
        claimed_gifts:list[Gift] = []
        for seat_id, seat in self.__booked_seats.items():
            gift:Gift|None = seat.claim_gift()
            if gift is None: 
                continue # continue for loop
            claimed_gifts.append(gift)
            gift_str.append(f"CONGRATS you got {gift} x1 from seat {seat_id} !")

        print("#" * 60)
        print(f"## {title_str:<54} ##")
        print(f"## {customer_str:<54} ##")
        print(f"## {seat_str:<54} ##")
        if gift_str:
            for s in gift_str:
                # emoji is displayed as 2 characters worth of space
                print(f"## {s:^53} ##")
        print("#" * 60)
        for gift in claimed_gifts:
            gift.consume()


class Kino:
    def __init__(self, seat_rows:int, seat_cols:int) -> None:
        self.__seat_manager = Kino2DSeatManager(seat_rows, seat_cols)

    def start(self, gifted_seat_count: int) -> None:
        self.__seat_manager.set_random_gifted_seats(gifted_seat_count)
        self.__seat_manager.customer_show_seats()

        while True:
            print("\nMain Menu:")
            print("1. Buy Ticket")
            print("2. Admin View")
            print("3. Start Film")
            print("4. Exit")

            choice = input("Choose menu: ").strip()

            if choice == "1":
                customer = Customer(input("Customer name: ").strip())
                self.__seat_manager.customer_show_seats()
                seats_to_book = input("Choose your seats (example A1): ").strip().upper().split(",")

                booked_seats:dict[str, Seat] = {}
                cancel_booking = False
                for seat_str in seats_to_book:
                    seat_id = seat_str.strip()
                    try:
                        seat = self.__seat_manager.get_seat(seat_id)
                        if seat in booked_seats.values():
                            raise ValueError(f"!!! Seat {seat_id} was selected repeatedly.")
                        if seat.is_booked():
                            booked_by = seat.get_customer()
                            raise ValueError(f"!!! Seat {seat_id} is already booked by {booked_by.get_name()} #{booked_by.get_id()}.")
                        booked_seats[seat_id] = seat  # Validate only; do not booked yet
                    except (TypeError, ValueError) as err:
                        print(err)
                        if input("Cancel entire booking? (y/n): ").strip().lower() == "y":
                            cancel_booking = True
                            break # break from for loop

                if cancel_booking:
                    print("Booking cancelled; no seats were reserved.")
                    continue # continue while loop
                if not booked_seats:
                    print("No valid seats selected; ticket not issued.")
                    continue # continue while loop

                for seat_id in booked_seats:
                    self.__seat_manager.book_seat(seat_id, customer)
                ticket = Ticket(customer.get_name(), customer.get_id(), booked_seats)
                ticket.print_ticket()

            elif choice == "2":
                self.__seat_manager.admin_show_seats()

            elif choice == "3":
                print(f"\n!!! FILM STARTS !!! *ceritanya filmnya mulai ...*")
                print(f"\n!!! FILM ENDS !!! *kemudian ceritanya filmnya beres ...*")
                self.__seat_manager.clear_seats()
                print(f"\n!!! CINEMA OPENS !!! *cinema berulang ...*")
                self.__seat_manager.set_random_gifted_seats(gifted_seat_count)

            elif choice == "4":
                print("End of session.")
                break # break while loop

            else:
                print("Choose from 1 to 4.")

if __name__ == "__main__":
    kino = Kino(G_SEAT_ROWS, G_SEAT_COLS)
    # COMMAND LINE ARGUMENTS ex: "... kleinspass_kino.py <int>"
    # whatever is in ... this program only gets the arguments :
    # "" at idx 0 of sys.argv list
    # <int> at idx 1 okleinspass_kino.pyf sys.argv list
    # try get and convert argument string at sys.argv[1] to integer
    try: G_GIFTED_SEAT_COUNT = int(sys.argv[1])
    # ignore IndexError when sys.argv[1] doesn't exist ex: "... kleinspass_kino.py"
    # ignore ValueError when sys.argv[1] is not convertible to int
    except Exception: print(f"!!! Default gift count to {G_GIFTED_SEAT_COUNT} gifts.")
    # majority of program runtime is in the start method ... 
    kino.start(G_GIFTED_SEAT_COUNT)