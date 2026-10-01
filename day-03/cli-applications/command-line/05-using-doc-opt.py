# pip install docopt

"""
Usage:
  myscript.py <name> <age> [--city=<city>]

Options:
  --city=<city>  City name [default: Unknown]
"""
from docopt import docopt

args = docopt(__doc__)
print(args)
