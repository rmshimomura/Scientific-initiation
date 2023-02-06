import math

def logarithmic_growth_distance(day: int) -> float:
    return math.log(day, 7)

def logarithmic_growth_days(distance: float) -> float:
    return 7**distance