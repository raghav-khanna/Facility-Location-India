#!/bin/bash

c_v_l=False # Set true for clusters vs lambda figures in Synthetic or Synthetic-unequal dataset
f_v_E=False # Set true to check the fairness error vs Discrete clustering energy plots in a lambda range. Note that,
          # In this case also set --lmd_tune to True to have the default range.
conv=False # Set true to see if the algorithm converges.
lmd_tune=False

dataset=Synthetic-unequal
cluster_option=kmeans
lmd=10
py test_fair_clustering.py -d $dataset \
                             --cluster_option $cluster_option \
                             --lmbda-tune $lmd_tune \
                             --lmbda $lmd \
                             --L 1.0
                            #  --plot_option_clusters_vs_lambda $c_v_l \
                            #  --plot_option_fairness_vs_clusterE $f_v_E \
                            #  --plot_option_convergence $conv

#dataset=Bank
#cluster_option=ncut
#lmd=40
#python test_fair_clustering.py -d $dataset \
#                             --cluster_option $cluster_option \
#                             --lmbda-tune $lmd_tune \
#                             --lmbda $lmd \
#                             --L 1.0 \
#                             --plot_option_clusters_vs_lambda $c_v_l \
#                             --plot_option_fairness_vs_clusterE $f_v_E \
#                             --plot_option_convergence $conv
