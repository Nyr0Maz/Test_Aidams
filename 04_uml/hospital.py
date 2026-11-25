"""Exo 1 UML - Système de gestion hospitalière (implémentation du diagramme de classes).

Voir hospital_uml.md pour les diagrammes.
Patron de conception utilisé pour le paiement : Strategy (PaymentMethod abstrait).
"""

from __future__ import annotations

import hashlib
import itertools
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

_ids = itertools.count(1)


# --------------------------------------------------------------------------
# Utilisateurs
# --------------------------------------------------------------------------
class User(ABC):
    """Superclasse abstraite : id, name, password, login/logout."""

    def __init__(self, name: str, password: str) -> None:
        self.id = next(_ids)
        self.name = name
        self._password_hash = self._hash(password)  # on ne stocke jamais le mot de passe en clair
        self.logged_in = False

    @staticmethod
    def _hash(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self, password: str) -> bool:
        self.logged_in = self._hash(password) == self._password_hash
        return self.logged_in

    def logout(self) -> None:
        self.logged_in = False

    @abstractmethod
    def role(self) -> str: ...


class Patient(User):
    def __init__(self, name: str, password: str, birth_date: str, phone: str) -> None:
        super().__init__(name, password)
        self.birth_date = birth_date
        self.phone = phone
        self.problems: list[HealthProblem] = []
        self.prescriptions: list[Prescription] = []  # historique des ordonnances

    def role(self) -> str:
        return "patient"

    def post_problem(self, organizer: Organizer, description: str) -> HealthProblem:
        problem = HealthProblem(self, description)
        self.problems.append(problem)
        organizer.receive_problem(problem)
        return problem

    def receive_prescription(self, prescription: Prescription) -> None:
        self.prescriptions.append(prescription)

    def pay(self, organizer: Organizer, prescription: Prescription, method: PaymentMethod) -> Payment:
        payment = Payment(prescription.fee, method, self, prescription)
        organizer.receive_payment(payment)
        return payment


class Doctor(User):
    def __init__(self, name: str, password: str, specialty: str, fee: float) -> None:
        super().__init__(name, password)
        self.specialty = specialty
        self.fee = fee
        self.balance = 0.0
        self.prescriptions_written: list[Prescription] = []

    def role(self) -> str:
        return "doctor"

    def examine(self, problem: HealthProblem, medications: list[str], notes: str) -> Prescription:
        problem.status = ProblemStatus.IN_REVIEW
        prescription = Prescription(self, problem, medications, notes, self.fee)
        self.prescriptions_written.append(prescription)
        return prescription

    def receive_payment(self, amount: float) -> None:
        self.balance += amount


class Organizer(User):
    """Organisateur, qui joue aussi le rôle d'administrateur."""

    def __init__(self, name: str, password: str, office: str) -> None:
        super().__init__(name, password)
        self.office = office
        self.pending: list[HealthProblem] = []
        self.registered_patients: list[Patient] = []
        self.doctors: list[Doctor] = []

    def role(self) -> str:
        return "organizer/admin"

    # -- administration
    def register_patient(self, patient: Patient) -> None:
        self.registered_patients.append(patient)

    def add_doctor(self, doctor: Doctor) -> None:
        self.doctors.append(doctor)

    # -- workflow
    def receive_problem(self, problem: HealthProblem) -> None:
        if problem.patient not in self.registered_patients:
            raise PermissionError("Patient non enregistré")
        self.pending.append(problem)

    def consult_doctor(self, problem: HealthProblem, doctor: Doctor,
                       medications: list[str], notes: str) -> Prescription:
        problem.doctors.append(doctor)  # un problème peut être vu par plusieurs médecins
        prescription = doctor.examine(problem, medications, notes)
        self.send_prescription(prescription)
        return prescription

    def send_prescription(self, prescription: Prescription) -> None:
        prescription.problem.patient.receive_prescription(prescription)

    def receive_payment(self, payment: Payment) -> None:
        if not payment.process():
            raise ValueError("Paiement refusé")
        payment.prescription.doctor.receive_payment(payment.amount)
        payment.prescription.problem.status = ProblemStatus.RESOLVED
        if payment.prescription.problem in self.pending:
            self.pending.remove(payment.prescription.problem)


# --------------------------------------------------------------------------
# Problème, ordonnance
# --------------------------------------------------------------------------
class ProblemStatus(Enum):
    PENDING = "pending"
    IN_REVIEW = "in-review"
    RESOLVED = "resolved"


@dataclass(eq=False)
class HealthProblem:
    patient: Patient
    description: str
    status: ProblemStatus = ProblemStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    doctors: list[Doctor] = field(default_factory=list)
    id: int = field(default_factory=lambda: next(_ids))


@dataclass(eq=False)
class Prescription:
    doctor: Doctor
    problem: HealthProblem
    medications: list[str]
    notes: str
    fee: float
    created_at: datetime = field(default_factory=datetime.now)
    renewals_left: int = 0  # une ordonnance peut être renouvelable
    id: int = field(default_factory=lambda: next(_ids))

    def renew(self) -> bool:
        if self.renewals_left <= 0:
            return False
        self.renewals_left -= 1
        return True


# --------------------------------------------------------------------------
# Paiement : pattern Strategy
# --------------------------------------------------------------------------
class PaymentMethod(ABC):
    @abstractmethod
    def authorize(self, amount: float) -> bool: ...


class Cash(PaymentMethod):
    def __init__(self, amount_given: float) -> None:
        self.amount_given = amount_given

    def authorize(self, amount: float) -> bool:
        return self.amount_given >= amount


class Check(PaymentMethod):
    def __init__(self, check_number: str, bank: str) -> None:
        self.check_number = check_number
        self.bank = bank

    def authorize(self, amount: float) -> bool:
        return bool(self.check_number and self.bank)


class CreditCard(PaymentMethod):
    def __init__(self, card_number: str, expiry: str) -> None:
        if not (card_number.isdigit() and len(card_number) == 16):
            raise ValueError("Numéro de carte invalide")
        self.masked = "**** **** **** " + card_number[-4:]  # on ne garde que les 4 derniers chiffres
        self.expiry = expiry

    def authorize(self, amount: float) -> bool:
        return amount > 0


@dataclass(eq=False)
class Payment:
    amount: float
    method: PaymentMethod
    patient: Patient
    prescription: Prescription
    created_at: datetime = field(default_factory=datetime.now)
    completed: bool = False

    def process(self) -> bool:
        if self.completed:  # intégrité : pas de double paiement
            return False
        self.completed = self.method.authorize(self.amount)
        return self.completed


if __name__ == "__main__":
    org = Organizer("Admin", "admin-pw", "Bureau 1")
    doc = Doctor("Dr House", "doc-pw", "Diagnostic", fee=50.0)
    pat = Patient("Jean", "pat-pw", "1990-01-01", "0600000000")
    org.add_doctor(doc)
    org.register_patient(pat)

    assert pat.login("pat-pw") and not doc.login("wrong")

    problem = pat.post_problem(org, "Maux de tête persistants")
    assert problem.status is ProblemStatus.PENDING
    presc = org.consult_doctor(problem, doc, ["Paracétamol"], "3 fois par jour")
    assert presc in pat.prescriptions and problem.status is ProblemStatus.IN_REVIEW

    pat.pay(org, presc, CreditCard("1234567812345678", "12/28"))
    assert doc.balance == 50.0 and problem.status is ProblemStatus.RESOLVED
    print(f"{pat.name} -> {problem.description!r} -> {presc.medications} -> "
          f"{doc.name} payé {doc.balance} € ; statut : {problem.status.value}")
    print("Scénario hôpital OK.")
