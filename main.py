from .constants import Axis, RotationType
from .auxiliary_methods import intersect, set2Decimal
import numpy as np
import copy

DEFAULT_NUMBER_OF_DECIMALS = 0
START_POSITION = [0, 0, 0]


class Item:
    def __init__(self, partno, name, typeof, WHD, weight, level, loadbear, updown, color, rotation_allowed):
        # Initialize an item with its properties
        self.partno = partno
        self.name = name
        self.typeof = typeof
        self.width = WHD[0]
        self.height = WHD[1]
        self.depth = WHD[2]
        self.weight = weight
        self.level = level  # Packing priority level (1-3)
        self.loadbear = loadbear  # Load-bearing capacity
        self.updown = updown if typeof == 'cube' else False  # Allow upside down if item is a cube
        self.color = color  # Visual representation color
        self.rotation_allowed = rotation_allowed  # Can the item be rotated
        self.rotation_type = 0  # Initial rotation type
        self.position = START_POSITION  # Starting position
        self.number_of_decimals = DEFAULT_NUMBER_OF_DECIMALS

    def formatNumbers(self, number_of_decimals):
        # Format item dimensions and weight to a fixed number of decimals
        self.width = set2Decimal(self.width, number_of_decimals)
        self.height = set2Decimal(self.height, number_of_decimals)
        self.depth = set2Decimal(self.depth, number_of_decimals)
        self.weight = set2Decimal(self.weight, number_of_decimals)
        self.number_of_decimals = number_of_decimals

    def string(self):
        # Return a string representation of the item
        return "%s(%sx%sx%s, weight: %s) pos(%s) rt(%s) vol(%s)" % (
            self.partno, self.width, self.height, self.depth, self.weight,
            self.position, self.rotation_type, self.getVolume()
        )

    def getVolume(self):
        # Calculate and return the volume of the item
        return set2Decimal(self.width * self.height * self.depth, self.number_of_decimals)

    def getMaxArea(self):
        # Get the maximum area of the item, sorted by dimension
        a = sorted([self.width, self.height, self.depth], reverse=True) if self.updown else [self.width, self.height,
                                                                                             self.depth]
        return set2Decimal(a[0] * a[1], self.number_of_decimals)

    def getDimension(self):
        # Get the dimensions of the item based on its rotation type
        if self.typeof == "cube" and not self.rotation_allowed:
            return [self.width, self.height, self.depth]
        if self.rotation_type == RotationType.RT_WHD:
            dimension = [self.width, self.height, self.depth]
        elif self.rotation_type == RotationType.RT_HWD:
            dimension = [self.height, self.width, self.depth]
        elif self.rotation_type == RotationType.RT_HDW:
            dimension = [self.height, self.depth, self.width]
        elif self.rotation_type == RotationType.RT_DHW:
            dimension = [self.depth, self.height, self.width]
        elif self.rotation_type == RotationType.RT_DWH:
            dimension = [self.depth, self.width, self.height]
        elif self.rotation_type == RotationType.RT_WDH:
            dimension = [self.width, self.depth, self.height]
        else:
            dimension = []
        return dimension


class Bin:
    def __init__(self, partno, WHD, max_weight, corner=0, put_type=1):
        # Initialize a bin with its properties
        self.partno = partno
        self.width = WHD[0]
        self.height = WHD[1]
        self.depth = WHD[2]
        self.max_weight = max_weight
        self.corner = corner  # Optional corners for support
        self.items = []  # Items placed in the bin
        self.fit_items = np.array([[0, WHD[0], 0, WHD[1], 0, 0]])  # Array of items' positions
        self.unfitted_items = []  # Items that could not be fitted
        self.number_of_decimals = DEFAULT_NUMBER_OF_DECIMALS
        self.fix_point = False
        self.check_stable = False
        self.support_surface_ratio = 0
        self.put_type = put_type
        self.gravity = []  # Gravity distribution data

    def formatNumbers(self, number_of_decimals):
        # Format bin dimensions and weight to a fixed number of decimals
        self.width = set2Decimal(self.width, number_of_decimals)
        self.height = set2Decimal(self.height, number_of_decimals)
        self.depth = set2Decimal(self.depth, number_of_decimals)
        self.max_weight = set2Decimal(self.max_weight, number_of_decimals)
        self.number_of_decimals = number_of_decimals

    def string(self):
        # Return a string representation of the bin
        return "%s(%sx%sx%s, max_weight:%s) vol(%s)" % (
            self.partno, self.width, self.height, self.depth, self.max_weight,
            self.getVolume()
        )

    def getVolume(self):
        # Calculate and return the volume of the bin
        return set2Decimal(
            self.width * self.height * self.depth, self.number_of_decimals
        )

    def getTotalWeight(self):
        # Calculate and return the total weight of all items in the bin
        total_weight = 0
        for item in self.items:
            total_weight += item.weight
        return set2Decimal(total_weight, self.number_of_decimals)

    def putItem(self, item, pivot, axis=None):
        # Attempt to place an item in the bin at the specified pivot point
        fit = False
        valid_item_position = item.position
        item.position = pivot
        rotate = RotationType.ALL if item.updown else RotationType.Notupdown

        for i in range(len(rotate)):
            item.rotation_type = i
            dimension = item.getDimension()
            # Check if the item fits within the bin dimensions
            if (
                    self.width < pivot[0] + dimension[0] or
                    self.height < pivot[1] + dimension[1] or
                    self.depth < pivot[2] + dimension[2]
            ):
                continue

            fit = True

            # Check for intersections with other items in the bin
            for current_item_in_bin in self.items:
                if intersect(current_item_in_bin, item):
                    fit = False
                    break

            if fit:
                # Check if adding the item exceeds the bin's weight limit
                if self.getTotalWeight() + item.weight > self.max_weight:
                    fit = False
                    return fit

                # Adjust item position to fit within the bin, if necessary
                if self.fix_point:
                    [w, h, d] = dimension
                    [x, y, z] = [float(pivot[0]), float(pivot[1]), float(pivot[2])]

                    for _ in range(3):
                        y = self.checkHeight([x, x + float(w), y, y + float(h), z, z + float(d)])
                        x = self.checkWidth([x, x + float(w), y, y + float(h), z, z + float(d)])
                        z = self.checkDepth([x, x + float(w), y, y + float(h), z, z + float(d)])

                    # Check the stability of the item placement
                    if self.check_stable:
                        item_area_lower = int(dimension[0] * dimension[1])
                        support_area_upper = 0
                        for i in self.fit_items:
                            if z == i[5]:
                                area = len(set(range(int(x), int(x + int(w)))) & set(range(int(i[0]), int(i[1])))) * \
                                       len(set(range(int(y), int(y + int(h)))) & set(range(int(i[2]), int(i[3]))))
                                support_area_upper += area

                        # Check if the support area is sufficient
                        if support_area_upper / item_area_lower < self.support_surface_ratio:
                            four_vertices = [[x, y], [x + float(w), y], [x, y + float(h)], [x + float(w), y + float(h)]]
                            c = [False, False, False, False]
                            for i in self.fit_items:
                                if z == i[5]:
                                    for jdx, j in enumerate(four_vertices):
                                        if (i[0] <= j[0] <= i[1]) and (i[2] <= j[1] <= i[3]):
                                            c[jdx] = True
                            if False in c:
                                item.position = valid_item_position
                                fit = False
                                return fit

                    self.fit_items = np.append(self.fit_items,
                                               np.array([[x, x + float(w), y, y + float(h), z, z + float(d)]]), axis=0)
                    item.position = [set2Decimal(x), set2Decimal(y), set2Decimal(z)]

                if fit:
                    self.items.append(copy.deepcopy(item))
                else:
                    item.position = valid_item_position
            return fit

        item.position = valid_item_position
        return fit

    def checkDepth(self, unfix_point):
        # Adjust item position along the depth (z-axis) to fit within the bin
        z_ = [[0, 0], [float(self.depth), float(self.depth)]]
        for j in self.fit_items:
            x_bottom = set(range(int(j[0]), int(j[1])))
            x_top = set(range(int(unfix_point[0]), int(unfix_point[1])))
            y_bottom = set(range(int(j[2]), int(j[3])))
            y_top = set(range(int(unfix_point[2]), int(unfix_point[3])))
            if len(x_bottom & x_top) != 0 and len(y_bottom & y_top) != 0:
                z_.append([float(j[4]), float(j[5])])
        top_depth = unfix_point[5] - unfix_point[4]
        z_ = sorted(z_, key=lambda z_: z_[1])
        for j in range(len(z_) - 1):
            if z_[j + 1][0] - z_[j][1] >= top_depth:
                return z_[j][1]
        return unfix_point[4]

    def checkWidth(self, unfix_point):
        # Adjust item position along the width (x-axis) to fit within the bin
        x_ = [[0, 0], [float(self.width), float(self.width)]]
        for j in self.fit_items:
            z_bottom = set(range(int(j[4]), int(j[5])))
            z_top = set(range(int(unfix_point[4]), int(unfix_point[5])))
            y_bottom = set(range(int(j[2]), int(j[3])))
            y_top = set(range(int(unfix_point[2]), int(unfix_point[3])))
            if len(z_bottom & z_top) != 0 and len(y_bottom & y_top) != 0:
                x_.append([float(j[0]), float(j[1])])
        top_width = unfix_point[1] - unfix_point[0]
        x_ = sorted(x_, key=lambda x_: x_[1])
        for j in range(len(x_) - 1):
            if x_[j + 1][0] - x_[j][1] >= top_width:
                return x_[j][1]
        return unfix_point[0]

    def checkHeight(self, unfix_point):
        # Adjust item position along the height (y-axis) to fit within the bin
        y_ = [[0, 0], [float(self.height), float(self.height)]]
        for j in self.fit_items:
            x_bottom = set(range(int(j[0]), int(j[1])))
            x_top = set(range(int(unfix_point[0]), int(unfix_point[1])))
            z_bottom = set(range(int(j[4]), int(j[5])))
            z_top = set(range(int(unfix_point[4]), int(unfix_point[5])))
            if len(x_bottom & x_top) != 0 and len(z_bottom & z_top) != 0:
                y_.append([float(j[2]), float(j[3])])
        top_height = unfix_point[3] - unfix_point[2]
        y_ = sorted(y_, key=lambda y_: y_[1])
        for j in range(len(y_) - 1):
            if y_[j + 1][0] - y_[j][1] >= top_height:
                return y_[j][1]
        return unfix_point[2]

    def addCorner(self):
        # Add corners to the bin for additional support
        if self.corner != 0:
            corner = set2Decimal(self.corner)
            corner_list = []
            for i in range(8):
                a = Item(
                    partno='corner{}'.format(i),
                    name='corner',
                    typeof='cube',
                    WHD=(corner, corner, corner),
                    weight=0,
                    level=0,
                    loadbear=0,
                    updown=True,
                    color='#000000'
                )
                corner_list.append(a)
            return corner_list

    def putCorner(self, info, item):
        # Place a corner item in the bin
        x = set2Decimal(self.width - self.corner)
        y = set2Decimal(self.height - self.corner)
        z = set2Decimal(self.depth - self.corner)
        pos = [[0, 0, 0], [0, 0, z], [0, y, z], [0, y, 0], [x, y, 0], [x, 0, 0], [x, 0, z], [x, y, z]]
        item.position = pos[info]
        self.items.append(item)
        corner = [float(item.position[0]), float(item.position[0]) + float(self.corner),
                  float(item.position[1]), float(item.position[1]) + float(self.corner),
                  float(item.position[2]), float(item.position[2]) + float(self.corner)]
        self.fit_items = np.append(self.fit_items, np.array([corner]), axis=0)

    def clearBin(self):
        # Clear all items from the bin
        self.items = []
        self.fit_items = np.array([[0, self.width, 0, self.height, 0, 0]])


class Packer:
    def __init__(self):
        # Initialize the packer with empty lists for bins, items, and unfit items
        self.bins = []
        self.items = []
        self.unfit_items = []
        self.total_items = 0
        self.binding = []

    def addBin(self, bin):
        # Add a bin to the packer
        return self.bins.append(bin)

    def addItem(self, item):
        # Add an item to the packer
        self.total_items = len(self.items) + 1
        return self.items.append(item)

    def pack2Bin(self, bin, item, fix_point, check_stable, support_surface_ratio):
        # Try to pack an item into a bin
        fitted = False
        bin.fix_point = fix_point
        bin.check_stable = check_stable
        bin.support_surface_ratio = support_surface_ratio

        # Add corners if necessary
        if bin.corner != 0 and not bin.items:
            corner_lst = bin.addCorner()
            for i in range(len(corner_lst)):
                bin.putCorner(i, corner_lst[i])

        elif not bin.items:
            response = bin.putItem(item, item.position)
            if not response:
                bin.unfitted_items.append(item)
            return

        # Attempt to place the item in the bin along each axis
        for axis in range(0, 3):
            items_in_bin = bin.items
            for ib in items_in_bin:
                pivot = [0, 0, 0]
                w, h, d = ib.getDimension()
                if axis == Axis.WIDTH:
                    pivot = [ib.position[0] + w, ib.position[1], ib.position[2]]
                elif axis == Axis.HEIGHT:
                    pivot = [ib.position[0], ib.position[1] + h, ib.position[2]]
                elif axis == Axis.DEPTH:
                    pivot = [ib.position[0], ib.position[1], ib.position[2] + d]

                if bin.putItem(item, pivot, axis):
                    fitted = True
                    break
            if fitted:
                break
        if not fitted:
            bin.unfitted_items.append(item)

    def sortBinding(self, bin):
        # Sort items based on binding constraints
        b, front, back = [], [], []
        for i in range(len(self.binding)):
            b.append([])
            for item in self.items:
                if item.name in self.binding[i]:
                    b[i].append(item)
                elif item.name not in self.binding:
                    if len(b[0]) == 0 and item not in front:
                        front.append(item)
                    elif item not in back and item not in front:
                        back.append(item)

        min_c = min([len(i) for i in b])

        sort_bind = []
        for i in range(min_c):
            for j in range(len(b)):
                sort_bind.append(b[j][i])

        for i in b:
            for j in i:
                if j not in sort_bind:
                    self.unfit_items.append(j)

        self.items = front + sort_bind + back

    def putOrder(self):
        # Arrange the order of items in the bin
        for i in self.bins:
            if i.put_type == 2:  # Open top container
                i.items.sort(key=lambda item: item.position[0], reverse=False)
                i.items.sort(key=lambda item: item.position[1], reverse=False)
                i.items.sort(key=lambda item: item.position[2], reverse=False)
            elif i.put_type == 1:  # General container
                i.items.sort(key=lambda item: item.position[1], reverse=False)
                i.items.sort(key=lambda item: item.position[2], reverse=False)
                i.items.sort(key=lambda item: item.position[0], reverse=False)

    def gravityCenter(self, bin):
        # Calculate the gravity distribution within the bin
        w = int(bin.width)
        h = int(bin.height)
        d = int(bin.depth)

        area1 = [set(range(0, w // 2 + 1)), set(range(0, h // 2 + 1)), 0]
        area2 = [set(range(w // 2 + 1, w + 1)), set(range(0, h // 2 + 1)), 0]
        area3 = [set(range(0, w // 2 + 1)), set(range(h // 2 + 1, h + 1)), 0]
        area4 = [set(range(w // 2 + 1, w + 1)), set(range(h // 2 + 1, h + 1)), 0]
        area = [area1, area2, area3, area4]

        for i in bin.items:
            x_st = int(i.position[0])
            y_st = int(i.position[1])
            if i.rotation_type == 0:
                x_ed = int(i.position[0] + i.width)
                y_ed = int(i.position[1] + i.height)
            elif i.rotation_type == 1:
                x_ed = int(i.position[0] + i.height)
                y_ed = int(i.position[1] + i.width)
            elif i.rotation_type == 2:
                x_ed = int(i.position[0] + i.height)
                y_ed = int(i.position[1] + i.depth)
            elif i.rotation_type == 3:
                x_ed = int(i.position[0] + i.depth)
                y_ed = int(i.position[1] + i.height)
            elif i.rotation_type == 4:
                x_ed = int(i.position[0] + i.depth)
                y_ed = int(i.position[1] + i.width)
            elif i.rotation_type == 5:
                x_ed = int(i.position[0] + i.width)
                y_ed = int(i.position[1] + i.depth)

            x_set = set(range(x_st, int(x_ed) + 1))
            y_set = set(range(y_st, y_ed + 1))

            # Calculate gravity distribution based on item position
            for j in range(len(area)):
                if x_set.issubset(area[j][0]) and y_set.issubset(area[j][1]):
                    area[j][2] += int(i.weight)
                    break
                elif x_set.issubset(area[j][0]) and not y_set.issubset(area[j][1]) and len(y_set & area[j][1]) != 0:
                    y = len(y_set & area[j][1]) / (y_ed - y_st) * int(i.weight)
                    area[j][2] += y
                    if j >= 2:
                        area[j - 2][2] += (int(i.weight) - y)
                    else:
                        area[j + 2][2] += (int(i.weight) - y)
                    break
                elif not x_set.issubset(area[j][0]) and y_set.issubset(area[j][1]) and len(x_set & area[j][0]) != 0:
                    x = len(x_set & area[j][0]) / (x_ed - x_st) * int(i.weight)
                    area[j][2] += x
                    if j >= 2:
                        area[j - 2][2] += (int(i.weight) - x)
                    else:
                        area[j + 2][2] += (int(i.weight) - x)
                    break
                elif not x_set.issubset(area[j][0]) and not y_set.issubset(area[j][1]) and len(
                        y_set & area[j][1]) != 0 and len(x_set & area[j][0]) != 0:
                    all = (y_ed - y_st) * (x_ed - x_st)
                    y = len(y_set & area[0][1])
                    y_2 = y_ed - y_st - y
                    x = len(x_set & area[0][0])
                    x_2 = x_ed - x_st - x
                    area[0][2] += x * y / all * int(i.weight)
                    area[1][2] += x_2 * y / all * int(i.weight)
                    area[2][2] += x * y_2 / all * int(i.weight)
                    area[3][2] += x_2 * y_2 / all * int(i.weight)
                    break

        r = [area[0][2], area[1][2], area[2][2], area[3][2]]
        total_weight = sum(r)
        if total_weight == 0:
            return [0, 0, 0, 0]

        result = []
        print(r)
        for i in r:
            result.append(round(i / sum(r) * 100, 2))
        return result

    def pack(self, bigger_first=False, distribute_items=True, fix_point=True, check_stable=True,
             support_surface_ratio=0.75, binding=[], number_of_decimals=DEFAULT_NUMBER_OF_DECIMALS):
        # Main packing function
        for bin in self.bins:
            bin.formatNumbers(number_of_decimals)

        for item in self.items:
            item.formatNumbers(number_of_decimals)

        self.binding = binding

        # Sort bins and items based on various criteria
        self.bins.sort(key=lambda bin: bin.getVolume(), reverse=bigger_first)
        self.items.sort(key=lambda item: item.getVolume(), reverse=bigger_first)
        self.items.sort(key=lambda item: item.loadbear, reverse=True)
        self.items.sort(key=lambda item: item.level, reverse=False)

        if binding:
            self.sortBinding(bin)

        for idx, bin in enumerate(self.bins):
            # Pack items into each bin
            for item in self.items:
                self.pack2Bin(bin, item, fix_point, check_stable, support_surface_ratio)

            if binding:
                self.items.sort(key=lambda item: item.getVolume(), reverse=bigger_first)
                self.items.sort(key=lambda item: item.loadbear, reverse=True)
                self.items.sort(key=lambda item: item.level, reverse=False)
                bin.items = []
                bin.unfitted_items = self.unfit_items
                bin.fit_items = np.array([[0, bin.width, 0, bin.height, 0, 0]])
                for item in self.items:
                    self.pack2Bin(bin, item, fix_point, check_stable, support_surface_ratio)

            # Calculate the gravity center deviation for the bin
            self.bins[idx].gravity = self.gravityCenter(bin)

            if distribute_items:
                for bitem in bin.items:
                    no = bitem.partno
                    for item in self.items:
                        if item.partno == no:
                            self.items.remove(item)
                            break

        # Arrange the order of items in the bin
        self.putOrder()

        if self.items:
            self.unfit_items = copy.deepcopy(self.items)
            self.items = []
