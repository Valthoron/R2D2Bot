import random
import re

from enum import IntEnum


class CriticalType(IntEnum):
    NONE = 0
    SUCCESS = 1
    FAILURE = 2


class RollResult:
    def __init__(self, rolls: int, pips: int, exploding_rolls: int, label: str|None):
        self._rolls = rolls
        self._pips = pips
        self._exploding_rolls = exploding_rolls
        self._label = label
        
        self._total = sum(rolls) + sum(exploding_rolls) + pips

    @property
    def rolls(self) -> int:
        return self._rolls

    @property
    def pips(self) -> int:
        return self._pips
    
    @property
    def exploding_rolls(self) -> int:
        return self._exploding_rolls

    @property
    def total(self) -> int:
        return self._total

    def __str__(self) -> str:
        string = self.dice_string()
        return string

    def dice_string(self) -> str:
        string = ""
        
        if self._label:
            string += f"**{self._label}:** "
        else:
            string += "**Result:** "
            
        string += f"{self._total} = ({', '.join(map(str, self._rolls))})"
        
        if self._pips > 0:
            string += f" + {self._pips}"
        
        if len(self._exploding_rolls) > 0:
            string += f" + ({', '.join(map(str, self._exploding_rolls))})"
            string += "\n:boom: *Exploding wild die*"
        elif self._rolls[0] == 1:
            if len(self._rolls) > 1:
                highest_die = max(self._rolls[1:])
                string += f"\n:exclamation: *Complication, or cancel dice for total = {self._total - highest_die - 1}*"
            else:
                string += "\n:exclamation: *Complication*"

        return string


def roll(dice: str):
    pattern = r'(\d+)\s*[dD]\s*(?:\+\s*(\d+))?(?:\s+(.+))?$'
    match = re.match(pattern, dice)
    if match:
        die_count = int(match.group(1))
        pip_count = int(match.group(2)) if match.group(2) else 0
        label = match.group(3).strip() if match.group(3) else None
    else:
        raise ValueError("Invalid dice string.")
    
    if die_count < 1 or die_count > 100:
        raise ValueError("Invalid die count. Must be at least 1 and at most 100.")
    
    if pip_count < 0 or pip_count > 2:
        raise ValueError("Invalid pip count. Must be at least 0 (or omitted) and at most 2.")
    
    rolls = [random.choice(range(1, 7)) for _ in range(die_count)]
    
    wild_die = rolls[0]
    exploding_rolls = []
    
    while (wild_die == 6):
        wild_die = random.choice(range(1, 7))
        exploding_rolls.append(wild_die)
    
    return RollResult(rolls, pip_count, exploding_rolls, label)
