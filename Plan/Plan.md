
---
# <p align="center">MODULAR ABAQUS BUILDER - A GENERAL PYTHON CODE FOR ORGANISING, BUILDING AND RUNNING MODULAR ABAQUS MODELS.</p>
<p align="center">By Hazel Full.</p>

<p align="center">Monash University, Department of Mechanical and Aerospace Engineering</p>

---
# <p align="center">Contents</p>
- Summary
- Introduction
- Statement of Problem
- Method of Solution
- Data Structure and the Code
  - Object Class
  - Model Class
  - Modular_Abaqus_Builder Class

---
# Summary
A general command line python interface that enables the user to modularise their Abaqus models. Input files can be read into the system that are then represented as different modular pieces that can be combined into new model combinations. This was developed to streamline the workflow when a number of very similar simulations must be run, with different geometries, materials or analyses.

---
# Introduction
The bane of many Engineers working with Abaqus is the sheer number of repetitive tasks the user must complete to ensure high quality models are built. To alleviate this issue many users will modularise their input files in such a manner that previously completed work — such as a meshed geometry or step/analysis setup — does not need to be redone.

The problem with this arises when they start working with more and more different models. Due to the way the importing of modularised input files is completed the input files typically all have identical names for the same modularised objects. If the modularised input files do not use identical names, then the input files require minor edits which makes tracking the exact details necessary. Either way, each method ends up being complicated, time-consuming and irritating to deal with, especially when working with a large number of models.

To combat this issue an easy to use command line or python based interface was developed to easily read, store, create, modify and run models built in a modular manner. An example of the use case would be if a user wants to run a previously modularised analysis on a recently meshed geometry. The new geometry can be added to the system and then a new model can be generated with the old analysis and the new geometry. This process can be repeated with the new geometry and multiple analyses that were previously added to the system.

---
# Method of Solution
The problem to be solved is as follows: Multiple modular abaqus .inp, fluent .msh and mpcci .csp files are disorganised and difficult to manage when running multiple similar but slightly different simulations. To alleviate the difficulty of managing a large number of modular simulation files this tool will facilitate storing the modular components in organised bins. These can then be combined into a new model comprised of multiple modular pieces. The modular pieces are referred to as "objects", they are split into the following three distinct categories:

- Analysis, this is analagous to a step definition in abaqus, in that it contains the necessary files to perform a specific type of analysis. Examples include: Frequency extraction in specific frequency bands, a dynamic implicit vibration of the entire chip or a submodel of a specific channel section coupled to a fluid model for predicting atomisation. The majority of these files are abaqus .inp files

- Geometry, this contains the mesh data for a specific chip geometry. Notably, there are five distinct meshes, the entire chip mesh, the acoustic representation of the fluid for the entire chip, a submodel solid mesh, a submodel acoustic mesh and the fluid mesh. All of these are abaqus .inp files except for the fluid mesh which is .msh.

- Material, this contains material definitions used by abaqus, there are two types of materials, solid and acoustic/fluid . All of these are abaqus .inp files.

Multiple objects of each of these three categories/types will be able to be added to the system. When an object is added to the system, a folder of pre-prepared files (typically abaqus input files) will be selected by the user. These will then be moved to a folder in that objects type subdirectory where the name of the folder is the object added. The ability to modify, duplicate and delete objects will also be included. 

Once objects have been added to the system the user will be able to build a model by initially selecting an analysis object. The analysis object will have a list of requirements (provided when initially building the object) built into the data structure that the user will have to select from the geometry and materials and other potential files. 

---
# Data Structure and Code
Three Classes will be built:

- Object
- Model
- Modular_Abaqus_Builder

These represent the components mentioned earlier, where the Modular_Abaqus_Builder class is the controller/command line interface. A Comprehensive overview of each of the classes, their attributes and methods as well as usage is included below.

---
## Analysis_Object Class
### Attributes
- object_name : str
  - The name of the object.
- description : str
  - A description of what the analysis object is.
- fpath : str
  - File path to the object files.
- files : list 
  - A list of the names of all files
- parameters : dict
  - A dictionary containing all the modifiable parameters for the object, including their names, their data types and their ranges.
- requirements : list of dicts
  - A list of all the requirements for the Analysis to function
- softwares : dict
  - A dictionary that contains the software requirements required for this analysis (abaqus, fluent, mpcci)
- Builder : Modular_Abaqus_Builder
  - The Modular_Abaqus_Builder class that contains this Analysis Object.
- Allowed_Characters : dict
  - A dictionary containing the allowed characters for attributes

---
### Methods
- init : [Builder : Modular_Abaqus_Builder]
  - Initialise the class and then request information from the user.

Save the Builder object in self.Builder.

Get the list of current Analysis_Object names.

Prompt the user to enter a name for the new object.

Check that the name is not currently used and that it only contains allowed characters.

Prompt for a description, and check that it only contains allowed characters.

Prompt the user to pick a fpath/folder that contains the files to be used in this Analysis_Object.

Create a new folder in the object storage folder.

Move all files from the previously specified directory to the new one.

Specify parameters.

Pick Requirements.

Pick Softwares.

- new_name

---
### Usage
-

---
## Object_Properties Class
### Attributes



---
### Methods
-
---
### Usage
-

---
## Model Class
### Attributes
- 
---
### Methods
-
---
### Usage
-

---
## Modular_Abaqus_Builder Class
### Attributes
- 
---
### Methods
-
---
### Usage
-
---
