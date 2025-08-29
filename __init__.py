from py3dbp.main import Packer, Item, Bin
from py3dbp.Painter import My_Painter

# Function to convert a string to a boolean value
def str_to_bool(our_string):
    our_string_lower = our_string.lower()
    if our_string_lower == 'true':
        return True
    elif our_string_lower == 'false':
        return False

# Function to process packing of items into a bin
def threePackerProcess(binWidth, binHeight, binDepth, inFileName):

    packer = Packer()  # Create a new Packer object
    raw_file_array = []
    # Define the bin with given dimensions and maximum weight capacity
    box = Bin(
        partno='example0',
        WHD=(binWidth, binHeight, binDepth),
        max_weight=28000,
        corner=0,
        put_type=0
    )

    # Add the bin to the packer
    packer.addBin(box)

    # Open the input file containing item data
    file = open(inFileName, "r")
    file.readline()  # Skip the header line

    # Read and process each line in the file
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
        raw_file_array.append((partno, name, types, width, height, depth, weight, level, loadbear, updown, color, rotation_allowed))
        # Add the item to the packer
        packer.addItem(Item(partno=partno, name=name, typeof=types, WHD=(width, height, depth), weight=weight, level=level, loadbear=loadbear, updown=updown, color=color, rotation_allowed=rotation_allowed))

    # Perform the packing operation
    packer.pack(
        bigger_first=True,            # Try to place bigger items first
        distribute_items=False,       # Do not distribute items across multiple bins
        fix_point=True,               # Fix the starting point for placing items
        check_stable=True,            # Check for the stability of placed items
        support_surface_ratio=0.75,   # Minimum support surface ratio for stability
        number_of_decimals=0          # Round off to zero decimals
    )

    # Write the fitted items to a CSV file
    filewf = open("fit.csv", "w")
    header = "boxName;xcoordinate;ycoordinate;zcoordinate;width;height;depth\n"
    filewf.write(header)
    fit_arr = []  # List to store the details of fitted items

    for item in box.items:
        boxtype = item.partno

        if boxtype[0:6] != "corner":  # Filter out items labeled as "corner"
            boxName = item.name
            x = str(item.position[0])
            y = str(item.position[1])
            z = str(item.position[2])
            width = str(item.getDimension()[0])
            height = str(item.getDimension()[1])
            depth = str(item.getDimension()[2])
            fit_arr.append((boxName, x, y, z, width, height, depth))
            data = boxName + ";" + x + ";" + y + ";" + z + ";" + width + ";" + height + ";" + depth + "\n"
            filewf.write(data)

    filewf.close()

    # Write the unfitted items to a separate CSV file
    filewu = open("unfit.csv", "w")
    header = "partno,name,types,width,height,depth,weight,level,loadbear,updown,color,rotation_allowed\n"
    filewu.write(header)
    ufit_arr = []  # List to store the details of unfitted items

    for item in box.unfitted_items:
        boxtype = item.partno

        if boxtype[0:6] != "corner":  # Filter out items labeled as "corner"
            partno = item.partno
            name = item.name
            types = item.typeof
            width = item.getDimension()[0]
            height = item.getDimension()[1]
            depth = item.getDimension()[2]
            weight = item.weight
            level = item.level
            loadbear = item.loadbear
            updown = item.updown
            color = item.color
            rotation_allowed = item.rotation_allowed

            ufit_arr.append((partno, name, types, width, height, depth, weight, level, loadbear, updown, color, rotation_allowed))

            data = partno + "," + name + "," + types + "," + str(width) + "," + str(height) + "," + str(depth) + "," + str(weight) + "," + str(level) + "," + str(loadbear) + "," + str(updown) + "," + color + "," + str(rotation_allowed) + "\n"
            filewu.write(data)

    filewu.close()

    # Visualize the packed items using My_Painter
    for box in packer.bins:
        painter = My_Painter(box)
        fig = painter.plotBoxAndItems(
            title=box.partno,  # Title of the plot
            alpha=0.2,         # Transparency of the items
            write_num=True,    # Write numbers on items
            fontsize=10        # Font size for the numbers
        )
    fig.show()  # Show the plot

    return "success", fit_arr, raw_file_array
