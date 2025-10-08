'''
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
This script creates a grid of partitions acting on the predefined set "Partition_Cells"
--------------------------------------------------------------------------------
    INPUTS
--------------------------------------------------------------------------------
Initial_X_Coord : float : 0.0
    The X coordinate of the first partition. (mm)

Initial_Y_Coord : float : 0.0
    The Y coordinate of the first partition. (mm)

N_Partitions : int : 15
    The number of cells to be partitioned in each direction.

Channel_Width : float : 0.02
    The width of the channels of the PALM chip to be partitioned. (mm)

Grid_Spacing : float : 0.5
    The width of each grid cell. (mm)

Model_Name : str : Vibrating_Chip_Model
    The name of the model that contains the part to be partitioned.

Part_Name : str : SOLID_GEOMETRY
    The name of the part to be partitioned.

Set_Name : str : PARTITION_CELLS
    The name of the set that contains the cells to be partitioned.
--------------------------------------------------------------------------------
    EXAMPLES
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
'''
from abaqus import *
from abaqusConstants import *

# Defining fields for dialog box
Fields_Parameters = (('Initial_X_Coord (float):', '0'),
                     ('Initial_Y_Coord (float):', '0'),
                     ('N_Partitions (int):', '15'), 
                     ('Channel_Width (float):', '0.02'),
                     ('Grid_Spacing (float):', '0.5'))

# Get input parameter values from dialog box
Initial_X_Coord, Initial_Y_Coord, N_Partitions, Channel_Width, Grid_Spacing = getInputs(fields=Fields_Parameters,
                                                                                                                  label='Specify partition parameters (See script for details): ',
                                                                                                                  dialogTitle='Partition Chip')

# Check user did not cancel dialog box
if Initial_X_Coord == None:
    print('--------------------')
    print('Script Cancelled')
    print('--------------------')
    exit

# Convert parameters to correct datatypes
Initial_X_Coord = float(Initial_X_Coord)
Initial_Y_Coord = float(Initial_Y_Coord)
N_Partitions = int(N_Partitions)
Channel_Width = float(Channel_Width)
Grid_Spacing = float(Grid_Spacing)

# Defining fields for dialog box
Fields_Names = (('Model_Name (str):', 'Vibrating_Chip_Model'),
                ('Part_Name (str):', 'SOLID_GEOMETRY'),
                ('Set_Name (str):', 'PARTITION_CELLS'))

# Get Names of objects
Model_Name, Part_Name, Set_Name = getInputs(fields=Fields_Names,
                                                         label='Specify model, part and set name to be partitioned (See script for details): ',
                                                         dialogTitle='Names')

# Check user did not cancel dialog box
if Model_Name == None:
    print('--------------------')
    print('Script Cancelled')
    print('--------------------')
    exit

# Get Part object
Part_To_Partition = mdb.models[Model_Name].parts[Part_Name]

# Get Set object
Set_To_Partition = Part_To_Partition.allSets[Set_Name]

# Create axes
Part_To_Partition.DatumAxisByPrincipalAxis(XAXIS)
x_axis = Part_To_Partition.datums[max(Part_To_Partition.datums.keys())]
Part_To_Partition.DatumAxisByPrincipalAxis(YAXIS)
y_axis = Part_To_Partition.datums[max(Part_To_Partition.datums.keys())]

# Partition geometry
for i in range(N_Partitions):

    # Partitions in the x direction (along the y axis)
    Part_To_Partition.DatumPointByCoordinate((Initial_X_Coord, Initial_Y_Coord + (i+1)*Grid_Spacing, 0))
    Datum_Point = max(Part_To_Partition.datums.keys())
    Part_To_Partition.PartitionCellByPlanePointNormal(normal = y_axis, cells=Set_To_Partition.cells, point=Part_To_Partition.datums[Datum_Point])

    Part_To_Partition.DatumPointByCoordinate((Initial_X_Coord, Initial_Y_Coord + i*Grid_Spacing + Channel_Width, 0))
    Datum_Point = max(Part_To_Partition.datums.keys())
    Part_To_Partition.PartitionCellByPlanePointNormal(normal = y_axis, cells=Set_To_Partition.cells, point=Part_To_Partition.datums[Datum_Point])

    # Partitions in the y direction (along the x axis)
    Part_To_Partition.DatumPointByCoordinate((Initial_X_Coord + (i+1)*Grid_Spacing, Initial_Y_Coord, 0))
    Datum_Point = max(Part_To_Partition.datums.keys())
    Part_To_Partition.PartitionCellByPlanePointNormal(normal = x_axis, cells=Set_To_Partition.cells, point=Part_To_Partition.datums[Datum_Point])

    Part_To_Partition.DatumPointByCoordinate((Initial_X_Coord + i*Grid_Spacing + Channel_Width, Initial_Y_Coord, 0))
    Datum_Point = max(Part_To_Partition.datums.keys())
    Part_To_Partition.PartitionCellByPlanePointNormal(normal = x_axis, cells=Set_To_Partition.cells, point=Part_To_Partition.datums[Datum_Point])