import matplotlib.pyplot as plt

data = [
    ["Name", "Age", "Occupation"],
    ["Alice", 28, "Engineer"],
    ["Bob", 35, "Designer"],
    ["Charlie", 22, "Student"]
]

fig, ax = plt.subplots()

# Create a table
table = ax.table(cellText=data, loc='center', cellLoc='center', colLabels=None)

# Modify table appearance
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1.2, 1.2)  # Adjust table size
ax.axis('off')  # Turn off axes

plt.show()
