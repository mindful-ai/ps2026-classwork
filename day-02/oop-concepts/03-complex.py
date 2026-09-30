class ComplexNumber:

    def __init__(self, real, imag):
        self.real = real
        self.imag = imag

    def add(self, other):
        return ComplexNumber(
            self.real + other.real,
            self.imag + other.imag
        )

    def subtract(self, other):
        return ComplexNumber(
            self.real - other.real,
            self.imag - other.imag
        )

if __name__ == "__main__":
    c1 = ComplexNumber(10, 5)
    c2 = ComplexNumber(4, 3)

    c3 = c1.add(c2)
    print(f"Addition: {c3.real} + {c3.imag}i")

    c4 = c1.subtract(c2)
    print(f"Subtraction: {c4.real} + {c4.imag}i")


'''

What Did Classes Solve?

We have now moved from:

Separate Data
      +
Separate Functions

to:

             ComplexNumber
          ┌──────────────────┐
          │      DATA        │
          │ real             │
          │ imaginary        │
          │                  │
          │    BEHAVIOR      │
          │ add()            │
          │ subtract()       │
          │ magnitude()      │
          │ conjugate()      │
          └──────────────────┘

This introduces one of the most important OOP ideas:

Encapsulation — bundling data and the operations that work on that data.


'''