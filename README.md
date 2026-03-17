# Surface saline lakes detection

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Status](https://img.shields.io/badge/Status-Completed-green)
![Type](https://img.shields.io/badge/Type-Research%20Internship-orange)

“Surface saline lakes” detection in the Mediterranean Sea using Argo float data

## Context

**Research internship** at Ruđer Bošković Institute in Split, Croatia (April - August 2024)

Division for Marine and Environmental Research

**Supervisors:** Elena Terzić, Ivica Vilibić

## Table of Contents

- [Objective](#objective)
- [Methods](#methods)
- [Data](#data)
- [Tools](#tools)
- [Associated Publication](#associated-publication)
- [Acknowledgements](#acknowledgements)
- [Contact](#contact)

## Objective
To document trends, variability, and spatial extent of "Surface Saline Lakes" (SSLs) using Argo profiling float data in the Mediterranean Sea.

SSLs are highly seasonal phenomena characterized by a near-surface salinity maximum overlying the pycnocline. They form in regions of low precipitation, high evaporation, and limited freshwater input, where weak winter wind mixing allows salt to accumulate near the surface.

Originally documented exclusively in the Levantine Basin, SSLs were subsequently observed in the Adriatic Sea following an isolated occurrence in 2017.

## Methods 

### Task 1. Argo data preparation
- Collection and preprocessing of Argo profiling float data in the Mediterranean Sea
- Development of detection methodology for surface saline lakes
- Calculation of descriptive variables (halocline/thermocline intensity, lake thickness, lake stability using Schmidt stability Index)

### Task 2. Surface saline lakes detection and characterization
Detection and documentation of surface saline lakes with the following variables:
- Location (longitude, latitude)
- Halocline intensity
- Thermocline intensity
- Lake depth
- Lake stability (Schmidt stability)

## Data
**Source:** [Argo profiling floats](https://argo.ucsd.edu/)

**Region:** Mediterranean Sea  

**Period:** 2000 - 2024

## Tools
Python libraries: `argopy`, `pandas`, `xarray`, `numpy`, `matplotlib`, `cartopy`, `gsw`, `os`

Python scripts were written in 2024 and may require older versions of the dependencies to run.

## How to use
Run the scripts in the following order:

1. `save_argo_data.py` — Downloads and preprocesses Argo float data for the Mediterranean Sea (including Black sea data). Outputs `Argo_data.csv` and `Argo_data.nc`.

2. `SSLs_detection.py` — Detects surface saline lakes from the Argo data. Outputs `Save_variables.csv` and profile figures.

3. `save_SSL_variables_Mediterranean_sea.py` — Filters out Black Sea data. Outputs `SSLs_variables_Mediterranean_sea.csv`.

## Associated Publication
This work contributed to the following publication:
[Surface saline lakes in the Mediterranean Sea](https://os.copernicus.org/articles/21/1441/2025/os-21-1441-2025.html) — *Ocean Science*, 2025

## Acknowledgements

This work was carried out at the Ruđer Bošković Institute (Split, Croatia) within the Division for Marine and Environmental Research. Many thanks to Elena Terzić and Ivica Vilibić for their guidance and support throughout this internship.

## Contact
Clara Gardiol - clara.gardiol@hotmail.fr

