# Plotter

### Purpose
The purpose of this branch is to create all the necessary plots for analysing the outputs of Vanilla Clustering and Variational Fair Clustering (Ziko Et al. 2021).

It contains code for creating following plots (K is the no. of clusters):
1.  ```src/vanilla/```
    1.  Plot (SSE vs K) and (Time taken vs K) plots from the data that was collected from CMLBDA: ```sse_timeTaken_linegraph.py```
    2.  Plot balance graph of vanilla clustering output and calculate overall balance of clustering: ```balance_bar.py```
2. ```src/ziko_etal```
   1. Plot balance graph of fair clustering output and calculate overall balance of clustering: ```balance_fair_bar.py```
3. ```src/heatmap_demographicbar.py```: Plot Heatmap of 640 districts of India (optionally with cluster centers of Variational Fair Clustering)

---

### How to use (Steps)
        1. Install dependencies from 'requirements.txt': pip install -r requirements.txt
        2. Create database and import from the .sql present in data folder
        3. Create .env file and add the required details (refer .env.sample)
        4. Vanilla Clustering:
           1. Add all the required output.txt files to the data/vanilla folder
           2. NOTE: There is a very specific format of the output.txt files which has to be followed strictly (refer output files collected at CMLBDA)
        5. Variational Fair Clustering:
           1. Add protected.txt, labels.txt and centers.txt as obtained from running the code from ziko_etal to data/ziko_etal
           2. NOTE: There is a very specific format of the output.txt files which has to be followed strictly (refer ziko_etal code)
           3. NOTE: data/ziko_etal contains the output files for K=3
        6. NOTE: The algorithms are tightly coupled with specific use case of age-demographic, do not use for other use cases.

---

### Log

    Created: 14 November 2023
    Last Edit: 30 December 2023
    
---
