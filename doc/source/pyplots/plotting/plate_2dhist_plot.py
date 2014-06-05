from FlowCytometryTools import FCPlate
import os, FlowCytometryTools
from pylab import *
import matplotlib.pyplot as plt

# Locate sample data included with this package
datadir = os.path.join(FlowCytometryTools.__path__[0], 'tests', 'data', 'Plate02')

# datadir = '[insert path to your own folder with fcs files.]'
# Make sure that the files follow the correct naming convention for the 'name' parser.
# Alternatively, change the parser (see tutorial online for further information).

# Load plate
plate = FCPlate.from_dir(ID='Demo Plate', path=datadir, parser='name')
plate = plate.transform('hlog', channels=['Y2-A', 'B1-A'], b=500.0)

# Drop empty cols / rows
plate = plate.dropna()

# Plot
ax_main, ax_subplots = plate.plot(['B1-A', 'Y2-A'], bins=200, wspace=0.4, hspace=0.1,
        hide_tick_labels=False, hide_tick_lines=False,
        col_label_yoffset=0.3, row_label_xoffset=0.5);

# Customizing the axes a bit
for rows in ax_subplots:
    for ax in rows:
        sca(ax)
        grid(True)
        ax.set_xticks(linspace(-2000.0, 10000.0, 5))
        ax.set_yticks(linspace(-2000.0, 10000.0, 5))
        tick_params(axis='both', which='major', labelsize=6)
        tick_params(axis='both', which='minor', labelsize=6)

#show() # <-- Uncomment when running as a script.
