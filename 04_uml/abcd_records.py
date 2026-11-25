"""Exo 2 UML - ABCD Records (implémentation du diagramme de classes).

Voir abcd_records_uml.md pour les diagrammes.
"""

from __future__ import annotations

import itertools
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date

_ids = itertools.count(1)


# --------------------------------------------------------------------------
# Membres
# --------------------------------------------------------------------------
class Member(ABC):
    def __init__(self, name: str, address: str) -> None:
        self.member_id = next(_ids)
        self.name = name
        self.address = address
        self.orders: list[Order] = []

    @property
    @abstractmethod
    def discount_rate(self) -> float: ...

    @property
    def can_order_unavailable(self) -> bool:
        return False

    @property
    def priority(self) -> bool:
        return False

    def place_order(self, clerk: OrderProcessingClerk, lines: list[tuple[Item, int]]) -> Order:
        order = Order(self, [OrderLine(item, qty) for item, qty in lines])
        self.orders.append(order)
        clerk.process_order(order)
        return order


class RegularMember(Member):
    @property
    def discount_rate(self) -> float:
        return 0.0


class RoyalMember(Member):
    @property
    def discount_rate(self) -> float:
        return 0.10

    @property
    def can_order_unavailable(self) -> bool:
        return True

    @property
    def priority(self) -> bool:
        return True


class NonMember:
    def __init__(self, name: str, address: str) -> None:
        self.name = name
        self.address = address

    def place_order(self, clerk: OrderProcessingClerk, lines) -> MembershipApplication:
        # Un non-membre ne peut pas commander : on lui envoie un formulaire d'adhésion
        return clerk.send_membership_application(self)


@dataclass
class MembershipApplication:
    applicant: NonMember
    sent_on: date = field(default_factory=date.today)
    approved: bool = False

    def approve(self, royal: bool = False) -> Member:
        self.approved = True
        cls = RoyalMember if royal else RegularMember
        return cls(self.applicant.name, self.applicant.address)


# --------------------------------------------------------------------------
# Articles
# --------------------------------------------------------------------------
class Item(ABC):
    def __init__(self, code: str, title: str, price: float, stock: int) -> None:
        self.code = code
        self.title = title
        self.price = price
        self.stock = stock

    def is_available(self, qty: int = 1) -> bool:
        return self.stock >= qty

    @abstractmethod
    def kind(self) -> str: ...


class CD(Item):
    def kind(self) -> str:
        return "CD"


class Tape(Item):
    def kind(self) -> str:
        return "Tape"


# --------------------------------------------------------------------------
# Commande
# --------------------------------------------------------------------------
@dataclass
class OrderLine:
    item: Item
    quantity: int
    backordered: bool = False

    @property
    def subtotal(self) -> float:
        return self.item.price * self.quantity


@dataclass(eq=False)
class Order:
    member: Member
    lines: list[OrderLine]
    order_date: date = field(default_factory=date.today)
    status: str = "new"
    order_id: int = field(default_factory=lambda: next(_ids))
    invoice: Invoice | None = None
    shipping_list: ShippingList | None = None

    def total(self) -> float:
        gross = sum(line.subtotal for line in self.lines)
        return round(gross * (1 - self.member.discount_rate), 2)


@dataclass
class Invoice:
    order: Order
    amount: float
    paid: bool = False

    def print(self) -> str:
        return f"INVOICE #{self.order.order_id} - {self.order.member.name} - {self.amount:.2f} €"


@dataclass
class ShippingList:
    order: Order
    lines: list[OrderLine]

    def print(self) -> str:
        items = ", ".join(f"{l.quantity}x {l.item.title}" for l in self.lines)
        return f"SHIPPING #{self.order.order_id} -> {self.order.member.address}: {items}"


# --------------------------------------------------------------------------
# Paiement
# --------------------------------------------------------------------------
class Payment(ABC):
    def __init__(self, amount: float) -> None:
        self.amount = amount

    @abstractmethod
    def validate(self) -> bool: ...


class CashPayment(Payment):
    def validate(self) -> bool:
        return self.amount > 0


class CheckPayment(Payment):
    def __init__(self, amount: float, check_number: str) -> None:
        super().__init__(amount)
        self.check_number = check_number

    def validate(self) -> bool:
        return bool(self.check_number)


class BankDraftPayment(Payment):
    def __init__(self, amount: float, draft_number: str, bank: str) -> None:
        super().__init__(amount)
        self.draft_number = draft_number
        self.bank = bank

    def validate(self) -> bool:
        return bool(self.draft_number and self.bank)


# --------------------------------------------------------------------------
# Employés
# --------------------------------------------------------------------------
class DailyRecordsFile:
    def __init__(self) -> None:
        self.entries: list[str] = []

    def record(self, order: Order) -> None:
        self.entries.append(f"{order.order_date} #{order.order_id} {order.member.name} {order.status}")


class OrderProcessingClerk:
    def __init__(self, name: str, members: list[Member], records: DailyRecordsFile) -> None:
        self.name = name
        self.members = members
        self.records = records

    def verify_membership(self, person) -> bool:
        return isinstance(person, Member) and person in self.members

    def send_membership_application(self, person: NonMember) -> MembershipApplication:
        return MembershipApplication(person)

    def process_order(self, order: Order) -> None:
        if not self.verify_membership(order.member):
            order.status = "rejected"
            self.records.record(order)
            raise PermissionError("Seuls les membres peuvent commander")

        to_ship: list[OrderLine] = []
        for line in order.lines:
            if line.item.is_available(line.quantity):
                line.item.stock -= line.quantity
                to_ship.append(line)
            elif order.member.can_order_unavailable:
                line.backordered = True  # commande d'article indisponible (Royal uniquement)
            else:
                raise ValueError(f"Article indisponible : {line.item.title}")

        order.invoice = Invoice(order, order.total())
        order.shipping_list = ShippingList(order, to_ship)
        order.status = "awaiting payment"
        self.records.record(order)


class CollectionDepartmentClerk:
    def __init__(self, name: str) -> None:
        self.name = name

    def collect_payment(self, order: Order, payment: Payment) -> bool:
        if order.invoice is None or order.invoice.paid:
            return False
        if payment.amount < order.invoice.amount or not payment.validate():
            return False
        order.invoice.paid = True
        order.status = "paid"
        return True


if __name__ == "__main__":
    records = DailyRecordsFile()
    royal = RoyalMember("Reine", "1 Palace Road")
    clerk = OrderProcessingClerk("Opal", [royal], records)
    collector = CollectionDepartmentClerk("Colin")

    cd1 = CD("CD-01", "Abbey Road", 20.0, stock=5)
    cd2 = CD("CD-02", "Rare Pressing", 30.0, stock=0)  # indisponible

    # Scénario : un membre Royal commande 2 CD (dont 1 indisponible) et paie par chèque
    order = royal.place_order(clerk, [(cd1, 1), (cd2, 1)])
    assert order.total() == 45.0  # (20 + 30) - 10 %
    assert order.lines[1].backordered and cd1.stock == 4
    print(order.invoice.print())
    print(order.shipping_list.print())
    assert collector.collect_payment(order, CheckPayment(45.0, "CHK-123"))
    assert order.status == "paid"

    # Un non-membre reçoit un formulaire d'adhésion
    app = NonMember("Paul", "2 rue X").place_order(clerk, [(cd1, 1)])
    assert isinstance(app, MembershipApplication)

    # Un membre régulier ne peut pas commander un article indisponible
    reg = RegularMember("Rita", "3 rue Y")
    clerk.members.append(reg)
    try:
        reg.place_order(clerk, [(cd2, 1)])
    except ValueError as e:
        print("Regular :", e)

    print("Daily records :", records.entries)
    print("Scénario ABCD Records OK.")
