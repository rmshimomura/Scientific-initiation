import math

def base_7_logarithmic_growth_distance(day: int) -> float:
    return math.log(day, 7)

def base_7_logarithmic_growth_days(distance: float) -> float:
    return 7**distance

def base_10_logarithmic_growth_distance(day: int) -> float:
    return math.log(day, 10)

def base_10_logarithmic_growth_days(distance: float) -> float:
    return 10**distance

def base_100_logarithmic_growth_distance(day: int) -> float:
    return math.log(day, 100)

def base_100_logarithmic_growth_days(distance: float) -> float:
    return 100**distance

def base_50_div_2_logarithmic_growth_distance(day: int) -> float:
    return math.log(day, 50)/2

def base_50_div_2_logarithmic_growth_days(distance: float) -> float:
    return 50**(distance*2)