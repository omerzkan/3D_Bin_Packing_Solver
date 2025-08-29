

"""
USED VERSION OF BI SOLVER:

This version allowed the solver solve according to items dimension.

In this version, dimensions have to have a dimension in common.
This code find the common dimension and put it into the depth and do the 2D packing

"""
from rectpack import newPacker

# Convert a string to a boolean value.
def str_to_bool(our_string):
	our_string_lower = our_string.lower()
	if our_string_lower == 'true':
		return True
	elif our_string_lower == 'false':
		return False


# Find common dimensions among all given dimensions.
def common_lengths_in_all(dimensions):
	result_list = []
	if len(dimensions) == 0:
		return result_list

	# Start with the dimensions of the first item
	common_lengths = set(dimensions[0])

	# Find the intersection of dimensions across all items
	for dim in dimensions[1:]:
		common_lengths &= set(dim)
		if len(common_lengths) == 0:
			return result_list

	return list(common_lengths)


# Adjust all rectangles to have a common depth if possible.
def make_common_one_depth(rectangle_list, common_length):
	if common_length is None:
		return "error", "Error: No common length, you can't use bi packer", None

	suit_result = []  # List of rectangles that can be adjusted
	not_suit_result = []  # List of rectangles that cannot be adjusted

	for rectangle in rectangle_list:
		# Unpack rectangle attributes
		partno, name, types, width, height, depth, weight, level, loadbear, updown, color, rotation_allowed = rectangle

		# Adjust the rectangle dimensions to have the common depth if possible
		if depth != common_length:
			if rotation_allowed:
				if width == common_length:
					width, depth = depth, width
				elif height == common_length:
					height, depth = depth, height
				elif depth == common_length:
					pass
				else:
					if rotation_allowed:
						if width == common_length:
							width, depth = depth, width
						elif height == common_length:
							height, depth = depth, height
					else:
						print(f"Part {partno} cannot be rotated to achieve common depth.")

		# Add to the appropriate list based on the adjustment
		if depth == common_length:
			updated_rectangle = (
			partno, name, types, width, height, depth, weight, level, loadbear, updown, color, rotation_allowed)
			suit_result.append(updated_rectangle)
		else:
			updated_rectangle = (
			partno, name, types, width, height, depth, weight, level, loadbear, updown, color, rotation_allowed)
			not_suit_result.append(updated_rectangle)

	return suit_result, not_suit_result


# Find the name of a rectangle by its ID.
def find_rect_name_by_id(rect_id, rectangle_list):
	for rect in rectangle_list:
		if rect[0] == rect_id:
			return rect[1]


# Main function to process the packing.
def biPackerProcess(bin_width, bin_height, bin_depth, inFileName):
	dimension_list = []  # List to store dimensions of all rectangles
	rectangle_list = []  # List to store all rectangle attributes

	# Read the input file and populate the rectangle list
	file = open(inFileName, "r")
	file.readline()  # Skip header
	for line in file.readlines():
		line = line.split(",")
		partno = line[0]
		name = line[1]
		types = line[2]
		width = int(line[3])
		height = int(line[4])
		depth = int(line[5])
		weight = int(line[6])
		level = int(line[7])
		loadbear = float(line[8])
		updown = str_to_bool(line[9].strip())
		color = line[10].strip()
		rotation_allowed = updown if True else str_to_bool(line[11].strip())

		dimension_list.append((width, height, depth))
		rectangle_list.append(
			(partno, name, types, width, height, depth, weight, level, loadbear, updown, color, rotation_allowed))

	file.close()

	# Determine the common length that can be used
	common_length = None
	common_lengths = common_lengths_in_all(dimension_list)

	if len(common_lengths) == 0:
		return "error", "Error: No common length, you can't use bi packer", None
	elif len(common_lengths) == 1:
		if common_lengths[0] <= bin_depth:
			common_length = int(common_lengths[0])
		else:
			return "error", "Error: Container depth is too low", None
	elif len(common_lengths) > 0:
		result_list = []
		for common_len in common_lengths:
			flag = True
			for dimensions in dimension_list:
				if common_len not in dimensions or common_len > bin_depth:
					flag = False
			if flag:
				result_list.append(common_len)
		if len(result_list) > 0:
			common_length = max(result_list)
		else:
			return "error", "Error: No suitable common length, you can't use bi packer", None

	# Separate rectangles into those that can and cannot be adjusted to the common depth
	suit_rects, not_suit_rects = make_common_one_depth(rectangle_list=rectangle_list, common_length=common_length)

	packer = newPacker()

	# Add the suitable rectangles to the packing queue
	for rect in suit_rects:
		width = rect[3]
		height = rect[4]
		packer.add_rect(width, height, rid=rect[0])

	packer.add_bin(bin_width, bin_height)  # Add the bin with the given dimensions

	packer.pack()  # Execute the packing process

	# Write the fit results to a CSV file
	filewf = open("fit.csv", "w")
	header = "boxtype;xcoordinate;ycoordinate;zcoordinate;width;height;depth\n"
	filewf.write(header)
	fit_arr = []  # Array to store fit rectangle details
	fit_rect_id = []  # Array to store the IDs of fit rectangles

	for abin in packer:
		for rect in abin:
			x = rect.x
			y = rect.y
			z = 0
			width = rect.width
			height = rect.height
			depth = common_length

			rid = rect.rid
			name = find_rect_name_by_id(rid, rectangle_list)

			fit_arr.append((name, str(x), str(y), str(z), str(width), str(height), str(depth)))
			fit_rect_id.append(rid)

			data = f"{name};{x};{y};{z};{width};{height};{depth}\n"
			filewf.write(data)
	filewf.close()

	# Write the unfit results to a CSV file
	filewu = open("unfit.csv", "w")
	header = "partno,name,types,width,height,depth,weight,level,loadbear,updown,color,rotation_allowed\n"
	filewu.write(header)
	ufit_arr = []  # Array to store unfit rectangle details

	for unfit_rect in rectangle_list:
		if unfit_rect[0] not in fit_rect_id:
			partno, name, types, width, height, depth, weight, level, loadbear, updown, color, rotation_allowed = unfit_rect
			ufit_arr.append(
				(partno, name, types, width, height, depth, weight, level, loadbear, updown, color, rotation_allowed))

			data = f"{partno},{name},{types},{width},{height},{depth},{weight},{level},{loadbear},{updown},{color},{rotation_allowed}\n"
			filewu.write(data)

	filewu.close()

	return "success", fit_arr, rectangle_list
