# Exo 2 – ABCD Records

Implémentation Python : [abcd_records.py](abcd_records.py)

> Mermaid n'a pas de diagramme de cas d'utilisation natif. On le représente avec un `flowchart` : les acteurs sont à l'extérieur du cadre « Système » et les cas d'utilisation sont des ovales à l'intérieur.

## Niveau 1

### Tâche 1.1 : cas d'utilisation (base)

```mermaid
flowchart LR
    M([👤 Member])
    C([👤 Order Processing Clerk])
    subgraph Système ABCD Records
        UC1((Place Order))
        UC2((Verify Membership))
        UC3((Process Order))
        UC4((Make Payment))
    end
    M --- UC1
    M --- UC4
    C --- UC2
    C --- UC3
```

### Tâche 1.2 : diagramme de classes (base)

```mermaid
classDiagram
    class Member {
        +int member_id
        +str name
        +str address
        +place_order(clerk, lines) Order
    }
    class Order {
        +int order_id
        +date order_date
        +str status
        +total() float
    }
    class OrderProcessingClerk {
        +str name
        +verify_membership(person) bool
        +process_order(order)
        +send_membership_application(person)
    }
    Member "1" -- "0..*" Order : passe
    OrderProcessingClerk "1" -- "0..*" Order : traite
```

## Niveau 2

### Tâche 2.1 : cas d'utilisation complets

```mermaid
flowchart LR
    M([👤 Member])
    R([👤 Royal Member])
    N([👤 Non-Member])
    OC([👤 Order Processing Clerk])
    CC([👤 Collection Department Clerk])
    R -. hérite .-> M

    subgraph Système ABCD Records
        PO((Place Order))
        VM((Verify Membership))
        VA((Verify Item Availability))
        PR((Process Order))
        AD((Apply Discount))
        PI((Print Invoice))
        PS((Print Shipping List))
        OU((Order Unavailable Items))
        SM((Send Membership Application))
        MP((Make Payment))
    end

    M --- PO
    M --- MP
    R --- OU
    N --- PO
    OC --- PR
    CC --- MP

    PO -. "«include»" .-> VM
    PR -. "«include»" .-> VA
    PR -. "«include»" .-> PI
    PR -. "«include»" .-> PS
    AD -. "«extend» (Royal)" .-> PR
    OU -. "«extend» (Royal, article indisponible)" .-> PO
    SM -. "«extend» (non-membre)" .-> VM
```

### Tâche 2.2 : diagramme de classes complet

```mermaid
classDiagram
    class Member {
        <<abstract>>
        +int member_id
        +str name
        +str address
        +discount_rate()* float
        +can_order_unavailable() bool
        +place_order(clerk, lines) Order
    }
    class RegularMember
    class RoyalMember {
        discount_rate = 10%
        priority = True
    }
    class NonMember {
        +str name
        +str address
    }
    class MembershipApplication {
        +date sent_on
        +bool approved
        +approve(royal) Member
    }
    class Item {
        <<abstract>>
        +str code
        +str title
        +float price
        +int stock
        +is_available(qty) bool
    }
    class CD
    class Tape
    class Order {
        +int order_id
        +date order_date
        +str status
        +total() float
    }
    class OrderLine {
        +int quantity
        +bool backordered
        +subtotal() float
    }
    class Invoice {
        +float amount
        +bool paid
        +print() str
    }
    class ShippingList {
        +print() str
    }
    class Payment {
        <<abstract>>
        +float amount
        +validate()* bool
    }
    class CashPayment
    class CheckPayment {
        +str check_number
    }
    class BankDraftPayment {
        +str draft_number
        +str bank
    }
    class OrderProcessingClerk {
        +verify_membership(person) bool
        +process_order(order)
        +send_membership_application(person)
    }
    class CollectionDepartmentClerk {
        +collect_payment(order, payment) bool
    }
    class DailyRecordsFile {
        +record(order)
    }

    Member <|-- RegularMember
    Member <|-- RoyalMember
    Item <|-- CD
    Item <|-- Tape
    Payment <|-- CashPayment
    Payment <|-- CheckPayment
    Payment <|-- BankDraftPayment

    Member "1" -- "0..*" Order : passe
    Order "1" *-- "1..*" OrderLine
    OrderLine "0..*" --> "1" Item
    Order "1" *-- "0..1" Invoice
    Order "1" *-- "0..1" ShippingList
    Invoice "1" -- "0..*" Payment : réglée par
    NonMember "1" -- "0..1" MembershipApplication : reçoit
    OrderProcessingClerk "1" -- "0..*" Order : traite
    CollectionDepartmentClerk "1" -- "0..*" Payment : encaisse
    DailyRecordsFile "1" o-- "0..*" Order : enregistre
```

### Scénario : un membre Royal commande 2 CD (dont 1 indisponible) et paie par chèque

Diagramme d'objets (instances) :

```mermaid
classDiagram
    class reine["reine : RoyalMember"] {
        name = "Reine"
    }
    class o1["o1 : Order"] {
        status = "paid"
    }
    class l1["l1 : OrderLine"] {
        quantity = 1
        backordered = False
    }
    class l2["l2 : OrderLine"] {
        quantity = 1
        backordered = True
    }
    class cd1["cd1 : CD"] {
        title = "Abbey Road"
        stock = 4
    }
    class cd2["cd2 : CD"] {
        title = "Rare Pressing"
        stock = 0
    }
    class inv["inv : Invoice"] {
        amount = 45.00
        paid = True
    }
    class chk["chk : CheckPayment"] {
        check_number = "CHK-123"
    }
    reine -- o1
    o1 *-- l1
    o1 *-- l2
    l1 --> cd1
    l2 --> cd2
    o1 *-- inv
    inv -- chk
```

## Niveau 3 : diagrammes de séquence

### Flux de commande complet

```mermaid
sequenceDiagram
    actor M as Member
    participant OC as OrderProcessingClerk
    participant I as Item
    participant O as Order
    participant DR as DailyRecordsFile
    actor CC as CollectionDeptClerk

    M->>OC: place_order(lines)
    OC->>OC: verify_membership(M)
    loop pour chaque OrderLine
        OC->>I: is_available(qty)
        I-->>OC: True / False
    end
    OC->>O: total() (remise appliquée)
    OC->>O: créer Invoice + ShippingList
    OC->>DR: record(order)
    OC-->>M: facture
    M->>CC: paiement
    CC->>CC: collect_payment(order, payment)
    CC-->>M: commande payée, expédition
```

### Vérification d'adhésion (succès et échec)

```mermaid
sequenceDiagram
    actor P as Client
    participant OC as OrderProcessingClerk
    participant DR as DailyRecordsFile
    P->>OC: place_order()
    OC->>OC: verify_membership(P)
    alt membre
        OC-->>P: commande acceptée, traitement
    else non-membre
        OC->>OC: send_membership_application(P)
        OC-->>P: formulaire d'adhésion
        OC->>DR: record (rejected)
    end
```

### Traitement du paiement (tous types)

```mermaid
sequenceDiagram
    actor M as Member
    participant CC as CollectionDeptClerk
    participant Pay as Payment
    participant Inv as Invoice
    M->>CC: payer(order, payment)
    CC->>Inv: déjà payée ?
    alt CashPayment
        CC->>Pay: validate() (montant > 0)
    else CheckPayment
        CC->>Pay: validate() (numéro de chèque)
    else BankDraftPayment
        CC->>Pay: validate() (numéro + banque)
    end
    alt valide et montant >= facture
        CC->>Inv: paid = True
        CC-->>M: reçu
    else refusé
        CC-->>M: paiement refusé
    end
```

### Commande d'articles indisponibles (Royal uniquement)

```mermaid
sequenceDiagram
    actor R as RoyalMember
    participant OC as OrderProcessingClerk
    participant I as Item
    participant L as OrderLine
    R->>OC: place_order([(cd2, 1)])
    OC->>I: is_available(1)
    I-->>OC: False
    alt can_order_unavailable (Royal)
        OC->>L: backordered = True
        OC-->>R: article en réapprovisionnement
    else Regular
        OC-->>R: erreur : article indisponible
    end
```
