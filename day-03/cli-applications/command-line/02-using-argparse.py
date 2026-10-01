import argparse

parser = argparse.ArgumentParser(description="Example: argparse demo")

parser.add_argument("name", help="Your name")
parser.add_argument("age", type=int, help="Your age")
parser.add_argument("--city", default="Unknown", help="City you live in")

args = parser.parse_args()

print(f"Hello {args.name}, age {args.age}, from {args.city}")


'''
C:\mindful-ai\ust-global-python-fs\day-12\command-line>python 02-using-argparse.py Anil 25 --city Paris
Hello Anil, age 25, from Paris

C:\mindful-ai\ust-global-python-fs\day-12\command-line>python 02-using-argparse.py --help
usage: 02-using-argparse.py [-h] [--city CITY] name age

Example: argparse demo

positional arguments:
  name         Your name
  age          Your age

options:
  -h, --help   show this help message and exit
  --city CITY  City you live in

C:\mindful-ai\ust-global-python-fs\day-12\command-line>python 02-using-argparse.py Anil 25             
Hello Anil, age 25, from Unknown



'''