# dioptric_demand_landscapes

Documentation of code for study: Quantification of near-work and peripheral defocus 

Purpose: Gaze data is matched with 2D pixel image of a point cloud. Code extract and visualize

A)	Accumulative figure of depth data at gaze coordinates

B)	Accumulative dioptric landscape matched at gaze coordinates


A) Aim: data access to objective and subjective data distance to point of regard 
Jupyter notebook, python: studyII_raw_data_dioptric_demand 
-	extract distance to point of regard from all point clouds
-	extract annotated labels and timestamps 
-	extract diary data 
-	visualize data 

dependencies:
from studyII_helpers_lib import DataAccess as get_px_meta
-	Easy access of px individuals meta data 
from studyII_helpers_lib import VisualizeData
-	Visualisation of data 

B)  Aim: Creates accumulative dioptric maps per participant / also if multiple recordings that are aligned at gaze coordinates from point cloud data and gaze estimates.  

matlab: extract_clustered_depth_reference_PoR.mpl 

extract dioptric maps with reference point of regard (gaze coordinates)

dependencies:
- extract_clustered_depth_data.m
Extract each point cloud, applies clustering filter
- recoridng_fp == filepath of recording folder 
Data from each participant 
- disp_pointcloud - visualize point cloud (very slow but looks good) 
Optional to visualize data on the go 
- studyII_helpers_lib.m
Provides participant meta data e.g., recording locations

Output csv: 
clustered_depth_data_with_reference_PoR.csv
clustered_depth_data_PoR_counter.csv

Jupyter notebook, python: dioptric_landscapes_studyII 

summarises dioptric demand for participants

dependencies:
from studyII_helpers_lib import DataAccess as get_px_meta
-	Easy access of px individuals meta data 
from studyII_helpers_lib import VisualizeData
-	Visualisation of data 

