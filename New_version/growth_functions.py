import math

def logaritmic_growth_distance(day: int, base: int) -> float:
    return math.log(day, base)

def logaritmic_growth_days(distance: float, base: int) -> float:
    return base**distance

def dummy_distance(days):
    return days*0.01

def dummy_days(distance):
    return distance*100