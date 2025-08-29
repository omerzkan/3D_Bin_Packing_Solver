# Class to define different types of rotations for a 3D object
class RotationType:
    RT_WHD = 0  # Width-Height-Depth
    RT_HWD = 1  # Height-Width-Depth
    RT_HDW = 2  # Height-Depth-Width
    RT_DHW = 3  # Depth-Height-Width
    RT_DWH = 4  # Depth-Width-Height
    RT_WDH = 5  # Width-Depth-Height

    # List containing all possible rotation types
    ALL = [RT_WHD, RT_HWD, RT_HDW, RT_DHW, RT_DWH, RT_WDH]

    # List of rotation types that do not involve a full 180-degree flip
    Notupdown = [RT_WHD, RT_HWD]

# Class to define the axes for 3D dimensions
class Axis:
    WIDTH = 0   # Index for the width dimension
    HEIGHT = 1  # Index for the height dimension
    DEPTH = 2   # Index for the depth dimension

    # List containing all the axis indices
    ALL = [WIDTH, HEIGHT, DEPTH]
