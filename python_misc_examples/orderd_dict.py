from collections import OrderedDict

# Create an OrderedDict
od = OrderedDict()

# Add items in a specific order
od['apple'] = 1
od['banana'] = 2
od['cherry'] = 3

print("Original OrderedDict:", od)

# Iterate to observe insertion order
print("Iterating through OrderedDict:")
for key, value in od.items():
    print(f"{key}: {value}")

# Move 'banana' to the end
od.move_to_end('banana')
print("After moving 'banana' to end:", od)

# Pop an item from the beginning (FIFO)
first_item = od.popitem(last=False)
print("Popped item (FIFO):", first_item)
print("OrderedDict after pop:", od)
