from typing import List, Dict

from models import Person

database: List[Dict[str, Person]] = [
    {"1": Person(name="Bruce Wayne", age=42, alive=True)},
    {"2": Person(name="Clark Kent", age=40, alive=True)},
    {"3": Person(name="Diana Prince", age=2500, alive=True)},
    {"4": Person(name="Barry Allen", age=32, alive=True)},
    {"5": Person(name="Arthur Curry", age=38, alive=True)},
    {"6": Person(name="Victor Stone", age=25, alive=True)},
    {"7": Person(name="Thomas Wayne", age=44, alive=False)},
    {"8": Person(name="Martha Wayne", age=42, alive=False)},
    {"9": Person(name="Jor-El", age=50, alive=False)},
    {"10": Person(name="Harvey Dent", age=41, alive=True)},
    {"11": Person(name="Dick Grayson", age=28, alive=True)},
    {"12": Person(name="Rachel Roth", age=19, alive=True)},
    {"13": Person(name="The Joker", age=45, alive=True)}
]
