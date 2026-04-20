
# Libraries to learn

- sqlite3
- textual

# Classes to Build

- object
    - analysis
    - geometry
    - material
- model
- requirements
- interface
- database
- theme
- tests
    - objects
    - models
    - interface
    - database
    - theme
- validation

# Database plan

- objects

| object_name | description | analysis/geometry | files | fpath
|-|-|-|-|-|

- object_files

| object_name | fpath | extension | 
|-|-|-|

- object_parameters

| object_name | parameter_name | dtype | solvers | value_range | default_value |
|-|-|-|-|-|-|


- models

| name | description | analysis_object | geometry_object | fpath |
|-|-|-|-|-|

- model_files

| model_name | fpath | extension | 
|-|-|-|

- model_parameters

| model_name | original_object_name | parameter_name | dtype | solvers | value_range | default_value | value |
|-|-|-|-|-|-|-|-|


- requirements

| object_name | solvers | analysis | geometry |
|-|-|-|-|