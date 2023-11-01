# Facility Location using Fairness in clustering

Welcome to Facility location repository.

---

## Purpose
The motivation behind this repository and the analysis behind it, is to compare performance of (Vanilla) K-means Clustering algorithm and algorithms based on fairness notions for the same dataset.

---

## Problem Description 

#### The Facility-Location problem: 
This problem is concerned with the optimal placement of facilities based on certain parameters like distance and ease of transportation.

#### Dataset:
Locate facilities all across India based on district-wise population density. As per 2011 Census, there are 640 Districts of India.

---

## Repository Structure
```
1. Dataset
    1. Contains 640 districts with following attributes:
        1. District Name
        2. Population Density
        3. Coordinates (Latitude and Longitude)
    2. The file 'districtsCompleteData.csv' contains the data used for all the clustering methods
2. Kmeans Branch
    1. Contains code for Kmeans clustering with Kmeans++ initialization.
    2. The implementation uses Pyclustering library, outputs final centers, final clusters, SSE, plot and animation of the clustering
3. Ziko_etal Branch
    1. Based on [Variational Fair Clustering](https://arxiv.org/abs/1906.08207)
    2. This clustering method helps you to find clusters with specified proportions of different demographic groups pertaining to a sensitive attribute of the dataset (population density in our case)
4. CMLBDA Branch
    1. The purpose of this branch was to simulate Vanilla Kmeans batch jobs for a set of values of K (no. of clusters) on the lab workstations.
    2. Vanilla Kmeans output for all values of K from 1 to 640 was collected and stored using this branch.

```

---

### Log

    Created: 4 September 2023
    Last Edit: 1 November 2023
    

---
