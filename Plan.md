
---
# <p align="center">MODULAR ABAQUS BUILDER - A GENERAL PYTHON CODE FOR ORGANISING, BUILDING AND RUNNING MODULAR ABAQUS MODELS.</p>
<p align="center">By Hazel Full.</p>

<p align="center">Monash University, Department of Mechanical and Aerospace Engineering</p>

---
# <p align="center">Contents</p>
- Summary
- Introduction
- Statement of Problem
  - a
- Method of Solution
  - a
- The Code and its Usage
  - a
- Coding
  - General
- Appendices
  - a

---
# Summary
A general command line python interface that enables the user to modularise their Abaqus models. Input files can be read into the system that are then represented as different modular pieces that can be combined into new model combinations. This was developed to streamline the workflow when a number of very similar simulations must be run, with different geometries, materials or analyses.

---
# Introduction
The bane of many Engineers working with Abaqus is the sheer number of repetitive tasks the user must complete to ensure high quality models are built. To alleviate this issue many users will modularise their input files in such a manner that previously completed work — such as a meshed geometry or step/analysis setup — does not need to be redone.

The problem with this arises when they start working with more and more different models. Due to the way the importing of modularised input files is completed the input files typically all have identical names for the same modularised objects. If the modularised input files do not use identical names, then the input files require minor edits which makes tracking the exact details necessary. Either way, each method ends up being complicated, time-consuming and irritating to deal with, especially when working with a large number of models.

To combat this issue an easy to use command line or python based interface was developed to easily read, store, create, modify and run models built in a modular manner. An example of the use case would be if a user wants to run a previously modularised analysis on a recently meshed geometry. The new geometry can be added to the system and then a new model can be generated with the old analysis and the new geometry. This process can be repeated with the new geometry and multiple analyses that were previously added to the system.

---
# Statement of Problem


---
# Method of Solution
a

---
# The Code and its Usage
a

---
# Coding
a

---
# Appendices
a

---