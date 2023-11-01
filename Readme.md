# Facility Location using Fairness in clustering

## Description of codebase

	1. data folder
		1. 
    2. constants.py
       1. Contains code to calculate haversine distance between 2 geolocations (as a distance measure for kmeans clustering)
	3. dataCollection.py
      	1. 
	4. kmeanspp.py
      	1. NOTE: Ensure that the data is already exists in the postgres database before running this file
      	2. File takes flag input 
      	3. Primarily uses PyClustering library
      	4. Contains code for
         	1. Retrieve features of the dataset
         	2. Find K initial clusters using Kmeans++ initialisation method (K is file arg provided before running)
         	3. Perform Kmeans on the dataset
         	4. Outputs final centers, final clusters and SSE of the clustering
         	5. Plots all points and also shows their membership
         	6. Creates a gif file displaying each iteration of Kmeans
	5. bashInput.sh
      	1. Used to pass multiple different values for number of clusters
      	2. Add all values, separated by space in facilities variable

---

## Example: Output for No. of Facilities, K = 28
 
#### Console output
The console output file is present [here](/Data/results/28-output.txt)

#### Plot
<div align="center"><img src="Data/results/28-map.png" alt=""/></div>

#### Animation
<div align="center"><img src="Data/results/28-map.gif" alt=""/></div>

---
