"""Exercices OOP - Surcharge d'opérateurs (operator overloading)."""

from __future__ import annotations

import math
from functools import total_ordering


# --- Problem 1 : nombres complexes -----------------------------------------
class Complex:
    def __init__(self, real: float, imag: float) -> None:
        self.real = real
        self.imag = imag

    def __add__(self, other: Complex) -> Complex:
        return Complex(self.real + other.real, self.imag + other.imag)

    def __sub__(self, other: Complex) -> Complex:
        return Complex(self.real - other.real, self.imag - other.imag)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Complex):
            return NotImplemented
        return self.real == other.real and self.imag == other.imag

    def __repr__(self) -> str:
        sign = "+" if self.imag >= 0 else "-"
        return f"{self.real} {sign} {abs(self.imag)}i"


# --- Problem 2 : Person comparée par l'âge ---------------------------------
class Person:
    def __init__(self, name: str, age: int, gender: str) -> None:
        self.name = name
        self.age = age
        self.gender = gender

    def __gt__(self, other: Person) -> bool:
        return self.age > other.age

    def __repr__(self) -> str:
        return f"Person({self.name!r}, {self.age}, {self.gender!r})"


# --- Problem 4 : produit scalaire de vecteurs ------------------------------
class Vector:
    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z

    def __mul__(self, other: Vector) -> float:
        """v1 * v2 -> produit scalaire (dot product)."""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def __repr__(self) -> str:
        return f"Vector({self.x}, {self.y}, {self.z})"


# --- Problem 5 : Circle, les 6 opérateurs de comparaison --------------------
class Circle:
    def __init__(self, radius: float) -> None:
        self.radius = radius

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Circle):
            return NotImplemented
        return self.radius == other.radius

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, Circle):
            return NotImplemented
        return self.radius != other.radius

    def __lt__(self, other: Circle) -> bool:
        return self.radius < other.radius

    def __le__(self, other: Circle) -> bool:
        return self.radius <= other.radius

    def __gt__(self, other: Circle) -> bool:
        return self.radius > other.radius

    def __ge__(self, other: Circle) -> bool:
        return self.radius >= other.radius

    def __repr__(self) -> str:
        return f"Circle(r={self.radius})"


# --- Problem 6 : points 2D comparés par distance à l'origine ---------------
@total_ordering
class Point2D:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def distance_from_origin(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point2D):
            return NotImplemented
        return math.isclose(self.distance_from_origin(), other.distance_from_origin())

    def __lt__(self, other: Point2D) -> bool:
        return self.distance_from_origin() < other.distance_from_origin()

    def __repr__(self) -> str:
        return f"Point2D({self.x}, {self.y})"


# --- Problem 7 : multiplication de matrices --------------------------------
class Matrix:
    def __init__(self, rows: list[list[float]]) -> None:
        if not rows or any(len(r) != len(rows[0]) for r in rows):
            raise ValueError("Toutes les lignes doivent avoir la même longueur")
        self.rows = [list(r) for r in rows]

    @property
    def shape(self) -> tuple[int, int]:
        return len(self.rows), len(self.rows[0])

    def __matmul__(self, other: Matrix) -> Matrix:
        n, m = self.shape
        m2, p = other.shape
        if m != m2:
            raise ValueError(f"Dimensions incompatibles : {self.shape} @ {other.shape}")
        return Matrix([
            [sum(self.rows[i][k] * other.rows[k][j] for k in range(m)) for j in range(p)]
            for i in range(n)
        ])

    # On autorise aussi "*" pour la multiplication matricielle
    __mul__ = __matmul__

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Matrix):
            return NotImplemented
        return self.rows == other.rows

    def __repr__(self) -> str:
        return f"Matrix({self.rows})"


if __name__ == "__main__":
    c1, c2 = Complex(3, 2), Complex(1, 7)
    print("P1:", c1 + c2, "|", c1 - c2)
    assert c1 + c2 == Complex(4, 9) and c1 - c2 == Complex(2, -5)

    alice, bob = Person("Alice", 30, "F"), Person("Bob", 25, "M")
    print("P2: Alice > Bob ?", alice > bob)
    assert alice > bob and not bob > alice

    v1, v2 = Vector(1, 2, 3), Vector(4, 5, 6)
    print("P4:", v1, "*", v2, "=", v1 * v2)
    assert v1 * v2 == 32

    a, b = Circle(2), Circle(5)
    print("P5:", a < b, a <= b, a > b, a >= b, a == b, a != b)
    assert (a < b, a <= b, a > b, a >= b, a == b, a != b) == (True, True, False, False, False, True)

    p, q = Point2D(3, 4), Point2D(1, 1)
    print("P6:", p, "plus loin que", q, "?", p > q)
    assert p > q and Point2D(0, 5) == p

    m1 = Matrix([[1, 2], [3, 4]])
    m2 = Matrix([[5, 6], [7, 8]])
    print("P7:", m1 @ m2)
    assert m1 @ m2 == Matrix([[19, 22], [43, 50]]) == m1 * m2

    print("Tous les tests passent.")
