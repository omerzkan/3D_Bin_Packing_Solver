# Required for plotting a representation of Bin and contained items
from matplotlib.patches import Rectangle, Circle
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.art3d as art3d
import numpy as np

import copy

DEFAULT_NUMBER_OF_DECIMALS = 0
START_POSITION = [0, 0, 0]


class My_Painter:
    def __init__(self, bins):
        # Initialize with the bins containing items and dimensions
        self.items = bins.items
        self.width = bins.width
        self.height = bins.height
        self.depth = bins.depth

    def _plotCube(self, ax, x, y, z, dx, dy, dz, color='red', mode=2, linewidth=1, text="", fontsize=15, alpha=0.5):
        """ Auxiliary function to plot a cube. """
        # Define the coordinates for the cube's base
        xx = [x, x, x + dx, x + dx, x]
        yy = [y, y + dy, y + dy, y, y]

        kwargs = {'alpha': 1, 'color': color, 'linewidth': linewidth}
        if mode == 1:
            # Plot the wireframe of the cube
            ax.plot3D(xx, yy, [z] * 5, **kwargs)
            ax.plot3D(xx, yy, [z + dz] * 5, **kwargs)
            ax.plot3D([x, x], [y, y], [z, z + dz], **kwargs)
            ax.plot3D([x, x], [y + dy, y + dy], [z, z + dz], **kwargs)
            ax.plot3D([x + dx, x + dx], [y + dy, y + dy], [z, z + dz], **kwargs)
            ax.plot3D([x + dx, x + dx], [y, y], [z, z + dz], **kwargs)
        else:
            # Plot the surfaces of the cube
            p = Rectangle((x, y), dx, dy, fc=color, ec='black', alpha=alpha)
            p2 = Rectangle((x, y), dx, dy, fc=color, ec='black', alpha=alpha)
            p3 = Rectangle((y, z), dy, dz, fc=color, ec='black', alpha=alpha)
            p4 = Rectangle((y, z), dy, dz, fc=color, ec='black', alpha=alpha)
            p5 = Rectangle((x, z), dx, dz, fc=color, ec='black', alpha=alpha)
            p6 = Rectangle((x, z), dx, dz, fc=color, ec='black', alpha=alpha)
            ax.add_patch(p)
            ax.add_patch(p2)
            ax.add_patch(p3)
            ax.add_patch(p4)
            ax.add_patch(p5)
            ax.add_patch(p6)

            if text:
                # Add text label inside the cube
                ax.text((x + dx / 2), (y + dy / 2), (z + dz / 2), str(text), color='black', fontsize=fontsize,
                        ha='center', va='center')

            # Convert 2D patches to 3D
            art3d.pathpatch_2d_to_3d(p, z=z, zdir="z")
            art3d.pathpatch_2d_to_3d(p2, z=z + dz, zdir="z")
            art3d.pathpatch_2d_to_3d(p3, z=x, zdir="x")
            art3d.pathpatch_2d_to_3d(p4, z=x + dx, zdir="x")
            art3d.pathpatch_2d_to_3d(p5, z=y, zdir="y")
            art3d.pathpatch_2d_to_3d(p6, z=y + dy, zdir="y")

    def _plotCylinder(self, ax, x, y, z, dx, dy, dz, color='red', mode=2, text="", fontsize=10, alpha=0.2):
        """ Auxiliary function to plot a cylinder. """
        # Plot the top and bottom circles of the cylinder
        p = Circle((x + dx / 2, y + dy / 2), radius=dx / 2, color=color, alpha=0.5)
        p2 = Circle((x + dx / 2, y + dy / 2), radius=dx / 2, color=color, alpha=0.5)
        ax.add_patch(p)
        ax.add_patch(p2)
        art3d.pathpatch_2d_to_3d(p, z=z, zdir="z")
        art3d.pathpatch_2d_to_3d(p2, z=z + dz, zdir="z")

        # Create the cylindrical surface
        center_z = np.linspace(0, dz, 10)
        theta = np.linspace(0, 2 * np.pi, 10)
        theta_grid, z_grid = np.meshgrid(theta, center_z)
        x_grid = dx / 2 * np.cos(theta_grid) + x + dx / 2
        y_grid = dy / 2 * np.sin(theta_grid) + y + dy / 2
        z_grid = z_grid + z
        ax.plot_surface(x_grid, y_grid, z_grid, shade=False, fc=color, alpha=alpha, color=color)

        if text:
            # Add text label inside the cylinder
            ax.text((x + dx / 2), (y + dy / 2), (z + dz / 2), str(text), color='black', fontsize=fontsize, ha='center',
                    va='center')

    def plotBoxAndItems(self, title="", alpha=0.2, write_num=False, fontsize=10):
        """ Plot the bin and the items it contains. """
        fig = plt.figure()
        axGlob = plt.axes(projection='3d')

        # Plot the bin itself
        self._plotCube(axGlob, 0, 0, 0, float(self.width), float(self.height), float(self.depth), color='black', mode=1,
                       linewidth=2, text="")

        # Plot each item in the bin
        for item in self.items:
            rt = item.rotation_type
            x, y, z = item.position
            [w, h, d] = item.getDimension()
            color = item.color
            text = item.partno if write_num else ""

            if item.typeof == 'cube':
                # Plot a cuboid item
                self._plotCube(axGlob, float(x), float(y), float(z), float(w), float(h), float(d), color=color, mode=2,
                               text=text, fontsize=fontsize, alpha=alpha)
            elif item.typeof == 'cylinder':
                # Plot a cylindrical item
                self._plotCylinder(axGlob, float(x), float(y), float(z), float(w), float(h), float(d), color=color,
                                   mode=2, text=text, fontsize=fontsize, alpha=alpha)

        plt.title(title)
        self.setAxesEqual(axGlob)  # Ensure equal scaling for all axes
        return plt

    def setAxesEqual(self, ax):
        """ Make axes of 3D plot have equal scale so that spheres appear as spheres, cubes as cubes, etc. """
        x_limits = ax.get_xlim3d()
        y_limits = ax.get_ylim3d()
        z_limits = ax.get_zlim3d()

        x_range = abs(x_limits[1] - x_limits[0])
        x_middle = np.mean(x_limits)
        y_range = abs(y_limits[1] - y_limits[0])
        y_middle = np.mean(y_limits)
        z_range = abs(z_limits[1] - z_limits[0])
        z_middle = np.mean(z_limits)

        # The plot bounding box is a sphere in the sense of the infinity norm,
        # hence the plot radius is half the max range.
        plot_radius = 0.5 * max([x_range, y_range, z_range])

        ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
        ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
        ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])