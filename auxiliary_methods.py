from decimal import Decimal
from .constants import Axis  # Import Axis constants (WIDTH, HEIGHT, DEPTH)

# Check if two rectangles (in 2D plane) intersect on a given pair of axes (x, y).
def rectIntersect(item1, item2, x, y):
    d1 = item1.getDimension()  # Get dimensions of the first item
    d2 = item2.getDimension()  # Get dimensions of the second item

    # Calculate the centers of the two items along the x and y axes
    cx1 = item1.position[x] + d1[x] / 2
    cy1 = item1.position[y] + d1[y] / 2
    cx2 = item2.position[x] + d2[x] / 2
    cy2 = item2.position[y] + d2[y] / 2

    # Calculate the overlap distances along x and y axes
    ix = max(cx1, cx2) - min(cx1, cx2)
    iy = max(cy1, cy2) - min(cy1, cy2)

    # Check if the items intersect by comparing the overlap distances with half the sum of their dimensions
    return ix < (d1[x] + d2[x]) / 2 and iy < (d1[y] + d2[y]) / 2

# Determine if two 3D items intersect in space.
def intersect(item1, item2):
    return (
        rectIntersect(item1, item2, Axis.WIDTH, Axis.HEIGHT) and  # Check intersection in width-height plane
        rectIntersect(item1, item2, Axis.HEIGHT, Axis.DEPTH) and  # Check intersection in height-depth plane
        rectIntersect(item1, item2, Axis.WIDTH, Axis.DEPTH)       # Check intersection in width-depth plane
    )

# Return a Decimal object representing the smallest unit for a given number of decimals.
def getLimitNumberOfDecimals(number_of_decimals):
    return Decimal('1.{}'.format('0' * number_of_decimals))

# Round a value to a specified number of decimal places.
def set2Decimal(value, number_of_decimals=0):
    number_of_decimals = getLimitNumberOfDecimals(number_of_decimals)
    return Decimal(value).quantize(number_of_decimals)
