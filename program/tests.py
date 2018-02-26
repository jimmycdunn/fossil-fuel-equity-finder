import unittest

def fun(x):
    return x + 1

# make a test for each class
# TestCase
class myTest(unittest.TestCase):
    def test(self):
        self.assertEqual(fun(3), 4)

# doctest searches for pieces of text that look like interactive Python session in docstrings

def square(x):
    """Return the square of x.

    >>> square(2)
    4
    >>> square(-2)
    4
    """
    return x * x

if __name__ == '__main__':
    import doctest
    doctest.testmod()

# test fixture

# test TestCase

# test suite

# test runner


# unittest.mock
