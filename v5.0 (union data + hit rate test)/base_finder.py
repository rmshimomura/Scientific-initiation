from math import log

def base_finder(target):
    number = 105
    exponent = 111.11
    base = 2
    
    steps = [100000, 10000, 1000, 100, 10, 1, 0.1, 0.01, 0.001]

    for step in steps:
        while log(number, base) * exponent > target:
            base += step
        base -= step  # Adjust back one step

    return base

print(f"Base ideal para chegar a um raio de 20km: {base_finder(20)} - {log(105, base_finder(20)) * 111.11}km")
print(f"Base ideal para chegar a um raio de 25km: {base_finder(25)} - {log(105, base_finder(25)) * 111.11}km")
print(f"Base ideal para chegar a um raio de 30km: {base_finder(30)} - {log(105, base_finder(30)) * 111.11}km")
print(f"Base ideal para chegar a um raio de 35km: {base_finder(35)} - {log(105, base_finder(35)) * 111.11}km")
print(f"Base ideal para chegar a um raio de 40km: {base_finder(40)} - {log(105, base_finder(40)) * 111.11}km")
print(f"Base ideal para chegar a um raio de 45km: {base_finder(45)} - {log(105, base_finder(45)) * 111.11}km")
print(f"Base ideal para chegar a um raio de 50km: {base_finder(50)} - {log(105, base_finder(50)) * 111.11}km")
print(f"Base ideal para chegar a um raio de 55km: {base_finder(55)} - {log(105, base_finder(55)) * 111.11}km")
print(f"Base ideal para chegar a um raio de 60km: {base_finder(60)} - {log(105, base_finder(60)) * 111.11}km")
