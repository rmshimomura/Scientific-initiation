import math
import matplotlib.pyplot as plt

days = []
radius = []
area = []

for i in range(1,138):
    print(f"Dia = {i} Raio do círculo = {math.log(i, 990000)*111.45}")
    days.append(i)
    radius.append(math.log(i, 990000)*111.45)

plt.plot(days, radius)

for i in range(1,138):
    if i % 10 == 0:
        plt.plot(i, math.log(i, 990000)*111.45, 'ro')

plt.plot(137, math.log(137, 990000)*111.45, 'ro')

# Make x axis ticks at 10 day intervals, and the last at 137 days
plt.xticks([i*10 for i in range(1,14)] + [137])


plt.xlabel('Dias')
plt.ylabel('Raio do círculo (km)')
plt.title('Raio do círculo em função dos dias')
plt.grid(True)
plt.savefig("test.png")
plt.show()