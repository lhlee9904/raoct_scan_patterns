import numpy as np
from math import pi, cos, sin

#incompatible function argument =
#NOT IN THE WRITE FORMAT
# arr = np.arange(10)
# print("arr :")
# print(arr)

# np.save('ask_python', arr)
# print("Your array has been saved to ask_python.npy")


#Semi - works: Analog voltage output channel creation failed
# arr = np.array([[1,0], [1, 0.1], [1, 0.2], [1,0.3]])
# print(arr)
# print("type:", arr.dtype)

# np.save('simple.npy', arr)

# Create a sine function with 10 points
numCols = 2
numRows = 10

arr = [[np.sin(i) for i in range(numCols)] for j in range(numRows)]

arr2 = [[i*0.1, sin(i*0.1)] for i in range(5)]

print(arr2)
np.save('simple.npy', arr2)