"""Exercices OOP - Héritage (inheritance)."""

from __future__ import annotations


# --- Problem 1 : Vehicle / Car / Bicycle -----------------------------------
class Vehicle:
    def drive(self) -> str:
        return "Driving a vehicle"


class Car(Vehicle):
    def drive(self) -> str:
        return "Driving a car"


class Bicycle(Vehicle):
    def drive(self) -> str:
        return "Riding a bicycle"


# --- Problem 2 : Person / Student / Employee -------------------------------
class Person:
    def __init__(self, name: str, age: int, address: str) -> None:
        self.name = name
        self.age = age
        self.address = address

    def introduce(self) -> str:
        return f"Hi, I'm {self.name}, {self.age} years old, living at {self.address}."


class Student(Person):
    def __init__(self, name: str, age: int, address: str, field_of_study: str) -> None:
        super().__init__(name, age, address)
        self.field_of_study = field_of_study

    def introduce(self) -> str:
        return f"{super().introduce()} I study {self.field_of_study}."


class Employee(Person):
    def __init__(self, name: str, age: int, address: str, company: str) -> None:
        super().__init__(name, age, address)
        self.company = company

    def introduce(self) -> str:
        return f"{super().introduce()} I work at {self.company}."


# --- Problem 3 : BankAccount / SavingsAccount ------------------------------
class BankAccount:
    def __init__(self, account_number: str, balance: float = 0.0) -> None:
        self.account_number = account_number
        self.balance = balance

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Le montant doit être positif")
        self.balance += amount

    def withdraw(self, amount: float) -> bool:
        """Retire `amount` ; renvoie False si le solde est insuffisant."""
        if amount <= 0:
            raise ValueError("Le montant doit être positif")
        if amount > self.balance:
            return False
        self.balance -= amount
        return True

    def transfer(self, target: BankAccount, amount: float) -> bool:
        """Transfère vers `target` ; False si solde insuffisant, True sinon."""
        if not self.withdraw(amount):
            return False
        target.deposit(amount)
        return True

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.account_number!r}, balance={self.balance:.2f})"


class SavingsAccount(BankAccount):
    def __init__(self, account_number: str, balance: float = 0.0, interest_rate: float = 0.02) -> None:
        super().__init__(account_number, balance)
        self.interest_rate = interest_rate

    def add_interest(self) -> float:
        interest = self.balance * self.interest_rate
        self.balance += interest
        return interest

    def check_balance(self) -> float:
        return self.balance


if __name__ == "__main__":
    for v in (Vehicle(), Car(), Bicycle()):
        print("P1:", v.drive())
    assert Car().drive() == "Driving a car" and Bicycle().drive() == "Riding a bicycle"

    people = [
        Person("Alice", 40, "1 rue de Paris"),
        Student("Bob", 20, "2 rue de Lyon", "Data Science"),
        Employee("Chloé", 35, "3 rue de Lille", "ACME"),
    ]
    for p in people:  # polymorphisme : même appel, comportement différent
        print("P2:", p.introduce())

    a = BankAccount("FR-001", 100)
    s = SavingsAccount("FR-002", 1000, interest_rate=0.05)
    assert a.transfer(s, 50) is True and a.balance == 50 and s.balance == 1050
    assert a.transfer(s, 500) is False and a.balance == 50  # solde insuffisant
    s.add_interest()
    print("P3:", a, s, "| solde épargne :", s.check_balance())
    assert round(s.check_balance(), 2) == 1102.50

    print("Tous les tests passent.")
