# dioptric_demand_landscapes

Documentation of code for study: Quantification of near-work and peripheral defocus 

Purpose: Gaze data is matched with 2D image of a point cloud. Code extract and visualize

A)	Accumulative figure of depth data at gaze coordinates

B)	Accumulative dioptric landscape matched at gaze coordinates


A) Aim: to compare objective and subjective data - distance to point of regard

matlab: extract_gaze_depth_from_PoR.m
-	extract distance to point of regard from all point clouds
- apply clustering filter to validate depth data

matlab: royale_LEVEL1_extract_depth_data_at_PoR.m
- access point cloud

Jupyter notebook, python: studyII_raw_data_dioptric_demand.jpynb 

-	extract annotated labels and timestamps from eye-tracking data
-	extract diary data 
-	visualize all data 

dependencies:
from studyII_helpers_lib import DataAccess as get_px_meta
-	Easy access of px individuals meta data 
from studyII_helpers_lib import VisualizeData
-	Visualisation of data 

B)  Aim: Creates accumulative dioptric maps per participant / also if multiple recordings that are aligned at gaze coordinates from point cloud data and gaze estimates.  

matlab: extract_clustered_depth_reference_PoR.mlx 

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

Jupyter notebook, python: dioptric_landscapes_studyII.jpynb 

summarises dioptric demand for participants
and visualisation 

dependencies:
from studyII_helpers_lib import DataAccess as get_px_meta
-	Easy access of px individuals meta data 
from studyII_helpers_lib import VisualizeData
-	Visualisation of data 

