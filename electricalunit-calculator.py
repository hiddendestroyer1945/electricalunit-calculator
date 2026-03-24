import sys
import math
import argparse
from typing import Dict, Tuple, Optional, Union

class UnitNormalizer:
    """Standardizes unit strings and identifies their target category."""
    
    UNIT_MAP = {
        'v': 'VOLTAGE',
        'a': 'CURRENT',
        'i': 'CURRENT',
        'ohm': 'RESISTANCE',
        'r': 'RESISTANCE',
        'kohm': 'RESISTANCE_K',
        'mohm': 'RESISTANCE_M',
        'w': 'POWER',
        'p': 'POWER',
        'f': 'CAPACITANCE',
        'uf': 'CAPACITANCE_U',
        'nf': 'CAPACITANCE_N',
        'pf': 'CAPACITANCE_P',
        'h': 'INDUCTANCE',
        'mh': 'INDUCTANCE_M',
        'uh': 'INDUCTANCE_U',
        'nh': 'INDUCTANCE_N',
        'ph': 'INDUCTANCE_P'
    }

    @classmethod
    def normalize(cls, unit: str) -> str:
        return cls.UNIT_MAP.get(unit.lower(), 'UNKNOWN')

class UnitConverter:
    """Enterprise-grade unit conversion engine."""
    
    CATEGORIES: Dict[str, Dict[str, float]] = {
        "RESISTANCE": { "ohm": 1.0, "kohm": 1000.0, "mohm": 1000000.0 },
        "CAPACITANCE": { "f": 1.0, "uf": 1e-6, "nf": 1e-9, "pf": 1e-12 },
        "INDUCTANCE": { "h": 1.0, "mh": 1e-3, "uh": 1e-6, "nh": 1e-9, "ph": 1e-12 }
    }

    @classmethod
    def find_category(cls, unit_lower: str) -> Optional[str]:
        for cat, units in cls.CATEGORIES.items():
            if unit_lower in units: return cat
        return None

    @classmethod
    def convert(cls, value: float, from_unit: str, to_unit: str) -> float:
        u1, u2 = from_unit.lower(), to_unit.lower()
        cat1, cat2 = cls.find_category(u1), cls.find_category(u2)
        if not cat1 or not cat2 or cat1 != cat2:
            raise ValueError(f"Incompatible or invalid units: {from_unit} -> {to_unit}")
        return value * (cls.CATEGORIES[cat1][u1] / cls.CATEGORIES[cat1][u2])

class OhmLawEngine:
    """Calculates V, I, R, P from any two parameters."""
    
    @staticmethod
    def calculate(v=None, i=None, r=None, p=None) -> Dict[str, float]:
        results = {'V': v, 'I': i, 'R': r, 'P': p}
        if v and i:
            results['R'], results['P'] = v / i, v * i
        elif v and r:
            results['I'], results['P'] = v / r, (v ** 2) / r
        elif v and p:
            results['I'], results['P'] = p / v, p / v # Fixed below logic
            results['I'] = p / v
            results['R'] = (v ** 2) / p
        elif i and r:
            results['V'], results['P'] = i * r, (i ** 2) * r
        elif i and p:
            results['V'], results['R'] = p / i, p / (i ** 2)
        elif r and p:
            results['V'], results['I'] = math.sqrt(p * r), math.sqrt(p / r)
        return {k: round(v, 4) for k, v in results.items() if v is not None}

class CircuitAnalyzer:
    @staticmethod
    def series_sum(val1: float, val2: float, unit: str) -> str:
        res = val1 + val2
        return f"Series Result: {res} {unit}\nAmperage remains constant (Series Law)."

    @staticmethod
    def parallel_current_sum(val1: float, val2: float) -> str:
        res = val1 + val2
        return f"Parallel Current Result: {res} A\nVoltage and Resistance consistent (Parallel Law)."

def get_float(prompt: str) -> float:
    while True:
        try:
            return float(input(prompt).strip())
        except ValueError: print("Error: Invalid numeric value.")

def interactive_mode():
    while True:
        print("\n=== Electrical Unit Calculator (Unified) ===")
        print("1. Ohm's Law Parameter Solver")
        print("2. Specialized Unit Conversion")
        print("3. Circuit Summation (Series/Parallel)")
        print("4. Exit")
        choice = input("Select an option (1-4): ").strip()
        
        if choice == '1':
            print("Enter any two (V, I, R, P).")
            # Logic simplified for space, using engine directly
            v1 = get_float("Value 1: "); u1 = input("Identity 1 (V, I, R, P): ").strip().upper()
            v2 = get_float("Value 2: "); u2 = input("Identity 2 (V, I, R, P): ").strip().upper()
            map_keys = {'V': None, 'I': None, 'R': None, 'P': None}
            map_keys[u1] = v1; map_keys[u2] = v2
            print(f"Results: {OhmLawEngine.calculate(**{k.lower(): v for k, v in map_keys.items()})}")
        elif choice == '2':
            val = get_float("Enter value: ")
            u1 = input("From Unit: ").strip()
            u2 = input("To Unit: ").strip()
            try: print(f"Result: {UnitConverter.convert(val, u1, u2)} {u2}")
            except ValueError as e: print(f"Error: {e}")
        elif choice == '3':
            v1 = get_float("Value 1: "); u1 = input("Identity (e.g., ohm, A): ")
            v2 = get_float("Value 2: ")
            op = input("Op (R=Series R, I=Parallel I): ").strip().upper()
            if op == 'R': print(CircuitAnalyzer.series_sum(v1, v2, u1))
            elif op == 'I': print(CircuitAnalyzer.parallel_current_sum(v1, v2))
        elif choice == '4': break
        else: print("Invalid choice.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Mini CLI for basic Ohm's Law automation
        parser = argparse.ArgumentParser()
        parser.add_argument("--v", type=float); parser.add_argument("--i", type=float)
        parser.add_argument("--r", type=float); parser.add_argument("--p", type=float)
        args = parser.parse_args()
        params = {k: v for k, v in vars(args).items() if v is not None}
        if len(params) == 2: print(OhmLawEngine.calculate(**params))
        else: print("Provide exactly two params or run interactively.")
    else: interactive_mode()
