def add_complex(r1, i1, r2, i2):
    real = r1 + r2
    imag = i1 + i2
    return real, imag

def subtract_complex(r1, i1, r2, i2):
    return r1 - r2, i1 - i2


result = add_complex(10, 5, 4, 3)


'''

What Did We Gain?

This is where the industry narrative becomes important.

Basic Script	                    Functions
Repeated logic	                    Reusable logic
Harder to maintain	                Easier to maintain
Difficult to test	                Easier to test
Large main program	                Smaller main program
Logic mixed together	            Logic separated
Difficult to reuse	                Easy to reuse


Software Engineering Principle
DRY — Don't Repeat Yourself

If the same logic exists in five places, changing the logic requires changing five places.

With a function:

                ┌───────────────┐
Input ─────────►│ add_complex() │
                └───────┬───────┘
                        │
                     Result

The caller doesn't need to know how addition is implemented.

This introduces another important concept:

Abstraction

The caller simply says:

add_complex(...)

rather than knowing the internal calculations.

--------------------------------------------------------------------------------

But Functions Have a Limitation

Now deliberately make the problem slightly larger.

Suppose we have:

c1_real = 10
c1_imag = 5

c2_real = 4
c2_imag = 3

And functions:

add_complex(...)
subtract_complex(...)
multiply_complex(...)
divide_complex(...)
magnitude(...)
conjugate(...)

We have reusable functions.

But:

Where is the complex number itself?

The data is still scattered across variables.

c1_real
c1_imag
c2_real
c2_imag
c3_real
c3_imag
...

And our functions need multiple parameters:

add_complex(r1, i1, r2, i2)

As the system grows, this becomes increasingly difficult to manage.

This gives us the next transition:

We have organized the behavior, but we haven't organized the data.

That leads to Object-Oriented Programming.



'''