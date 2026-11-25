# Exo 1 – Système de gestion hospitalière

Implémentation Python : [hospital.py](hospital.py)

## Tâche 1 + 2 + 3 : diagramme de classes

```mermaid
classDiagram
    class User {
        <<abstract>>
        +int id
        +str name
        -str password_hash
        +login(password) bool
        +logout()
        +role()* str
    }
    class Patient {
        +str birth_date
        +str phone
        +post_problem(organizer, description) HealthProblem
        +receive_prescription(prescription)
        +pay(organizer, prescription, method) Payment
    }
    class Doctor {
        +str specialty
        +float fee
        +float balance
        +examine(problem, medications, notes) Prescription
        +receive_payment(amount)
    }
    class Organizer {
        +str office
        +register_patient(patient)
        +add_doctor(doctor)
        +receive_problem(problem)
        +consult_doctor(problem, doctor) Prescription
        +send_prescription(prescription)
        +receive_payment(payment)
    }
    class HealthProblem {
        +int id
        +str description
        +ProblemStatus status
        +datetime created_at
    }
    class ProblemStatus {
        <<enumeration>>
        PENDING
        IN_REVIEW
        RESOLVED
    }
    class Prescription {
        +int id
        +list medications
        +str notes
        +float fee
        +datetime created_at
        +int renewals_left
        +renew() bool
    }
    class Payment {
        +float amount
        +datetime created_at
        +bool completed
        +process() bool
    }
    class PaymentMethod {
        <<interface>>
        +authorize(amount)* bool
    }
    class Cash
    class Check
    class CreditCard

    User <|-- Patient
    User <|-- Doctor
    User <|-- Organizer
    PaymentMethod <|.. Cash
    PaymentMethod <|.. Check
    PaymentMethod <|.. CreditCard

    Patient "1" *-- "0..*" HealthProblem : poste
    HealthProblem --> ProblemStatus
    HealthProblem "1" -- "0..*" Prescription : donne lieu à
    HealthProblem "0..*" -- "1..*" Doctor : examiné par
    Doctor "1" -- "0..*" Prescription : rédige
    Patient "1" -- "0..*" Prescription : historique
    Organizer "1" -- "0..*" HealthProblem : gère
    Organizer "1" -- "0..*" Doctor : consulte
    Patient "1" -- "0..*" Payment : effectue
    Payment "1" --> "1" Prescription : règle
    Payment "1" o-- "1" PaymentMethod : stratégie
```

## Tâche 2 : diagramme de séquence (un patient, de la soumission au paiement)

```mermaid
sequenceDiagram
    actor P as Patient
    participant O as Organizer
    participant D as Doctor
    participant Pay as Payment

    P->>O: post_problem(description)
    O->>O: receive_problem() (statut = PENDING)
    O->>D: consult_doctor(problem)
    D->>D: examine() (statut = IN_REVIEW)
    D-->>O: Prescription
    O->>P: send_prescription(prescription)
    P->>O: pay(prescription, CreditCard)
    O->>Pay: process()
    Pay-->>O: OK
    O->>D: receive_payment(amount)
    O->>O: statut = RESOLVED
```

## Tâche 3 : diagrammes de séquence système

### Inscription d'un patient

```mermaid
sequenceDiagram
    actor P as Patient
    participant S as Système
    actor O as Organizer (admin)
    P->>S: demande d'inscription(nom, mot de passe, infos)
    S->>O: nouvelle demande
    O->>S: register_patient(patient)
    S-->>P: compte créé (id)
    P->>S: login(mot de passe)
    S-->>P: connecté
```

### Consultation

```mermaid
sequenceDiagram
    actor P as Patient
    participant S as Système
    actor O as Organizer
    actor D as Doctor
    P->>S: post_problem(description)
    S-->>O: problème en attente (PENDING)
    O->>S: consult_doctor(problem, doctor)
    S-->>D: problème à examiner (IN_REVIEW)
    D->>S: examine() → Prescription
    S-->>O: ordonnance prête
    O->>S: send_prescription()
    S-->>P: ordonnance disponible
```

### Paiement

```mermaid
sequenceDiagram
    actor P as Patient
    participant S as Système
    actor O as Organizer
    actor D as Doctor
    P->>S: pay(prescription, méthode)
    alt Chèque / Espèces / Carte
        S->>S: method.authorize(amount)
    end
    alt autorisé
        S-->>O: paiement reçu
        O->>S: transfert au médecin
        S-->>D: receive_payment(amount)
        S-->>P: reçu, statut RESOLVED
    else refusé
        S-->>P: paiement refusé
    end
```

## Questions

1. **Un patient qui consulte plusieurs médecins ?** L'association `HealthProblem "0..*" -- "1..*" Doctor` (liste `doctors` dans `HealthProblem`) permet à un même problème d'être examiné par plusieurs médecins, et chaque médecin produit sa propre `Prescription`. Un patient a donc 0..* problèmes et 0..* ordonnances, venant de médecins différents.
2. **Les ordonnances sont-elles réutilisables ?** Oui, pour un traitement chronique. On le modélise avec un attribut `renewals_left` et une méthode `renew()`. Chaque renouvellement peut aussi créer une nouvelle `Prescription` qui référence l'originale.
3. **Quel design pattern pour le paiement ?** Le pattern **Strategy** : `Payment` délègue à une `PaymentMethod` abstraite (`Cash`, `Check`, `CreditCard`). On peut ajouter un mode de paiement sans modifier `Payment` (principe ouvert/fermé). Un pattern Factory peut créer la bonne stratégie.
4. **Intégrité des données de paiement ?** Un paiement ne peut être traité qu'une fois (`completed`), le montant vient de l'ordonnance et non du client, on ne stocke que les 4 derniers chiffres de la carte, le mot de passe est haché, et on garde l'horodatage pour l'audit. En production, on ajouterait des transactions en base de données, du chiffrement (TLS) et la conformité PCI-DSS.
