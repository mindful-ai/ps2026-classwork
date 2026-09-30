'''
Representation of a complex number and its operations

x = r1 + i1*i
y = r2 + i2*i

'''

r1 = 10
i1 = 5

r2 = 4
i2 = 3

add_real = r1 + r2
add_imag = i1 + i2

sub_real = r1 - r2
sub_imag = i1 - i2


'''

What happens when the program grows?

Suppose we now need:

10 complex numbers
multiplication
division
magnitude
conjugate
comparison
repeated calculations

The code starts becoming repetitive.
----------------------------------

The First Design Problem

Duplication.

And duplication creates:

more code
more places for bugs
difficult maintenance
poor readability
difficult testing

This creates the natural question:

Can we package the operation so that we can reuse it?

That leads naturally to functions.

'''