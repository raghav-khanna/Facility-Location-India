import argparse
import os
import sys
import os.path as osp
import numpy as np
from sklearn.preprocessing import scale
from src.fair_clustering import fair_clustering, km_init
import src.utils as utils
from src.dataset_load import read_dataset
from src.utils import get_fair_accuracy, get_fair_accuracy_proportional, normalizefea, Logger, str2bool
from data_visualization import plot_clusters_vs_lambda, plot_fairness_vs_clusterE, plot_convergence, plot_balance_vs_clusterE, plotMap
import random
import warnings
import matplotlib.pyplot as plt
warnings.filterwarnings('ignore')


def main(args):
    if args.seed is not None:
        np.random.seed(args.seed)
        random.seed(args.seed)

# Set Algorithm Options
    dataset = 'Facility'
    cluster_option = 'kmeans'
    data_dir = osp.join(args.data_dir, dataset)
    output_path = data_dir
    if not osp.exists(data_dir):
        os.makedirs(data_dir)

# Set Plotting Options
    plot_option_clusters_vs_lambda = args.plot_option_clusters_vs_lambda
    plot_option_fairness_vs_clusterE = args.plot_option_fairness_vs_clusterE
    plot_option_balance_vs_clusterE = args.plot_option_balance_vs_clusterE
    plot_option_convergence = args.plot_option_convergence

# Load Dataset
    savepath_compare = osp.join(data_dir, dataset+'.npz')
    if not os.path.exists(savepath_compare):
        X_unnormalised, protected_groups, K = read_dataset(data_dir)
        if X_unnormalised.shape[0] > 200000:
            np.savez_compressed(savepath_compare, X_unnormalised=X_unnormalised, protected_groups=protected_groups, K=K)
        else:
            np.savez(savepath_compare, X_unnormalised=X_unnormalised, protected_groups=protected_groups, K=K)
    else:
        datas = np.load(savepath_compare)
        X_unnormalised = datas['X_unnormalised']
        protected_groups = datas['protected_groups']
        K = datas['K'].item()

# Write to a log file
    log_path = osp.join(data_dir, cluster_option+'_log.txt')
    sys.stdout = Logger(log_path)

# Scale and Normalize Features
    # X_unnormalised = scale(X_unnormalised, axis=0)
    # X = normalizefea(X_unnormalised)
    X = X_unnormalised

# Store and print necessary variables for future use
    N, Tot_dim = X.shape
    print('Number of clusters for dataset {} are {}'.format(dataset, K))
    V = [np.array(protected_groups == j) for j in np.unique(protected_groups)]
    V_sum = [x.sum() for x in V]
    print('Balance of the dataset {}'.format(min(V_sum)/max(V_sum)))
    print('Number of points in the dataset {}'.format(N))
    U = [x/N for x in V_sum]  # proportional
    print('Demographic-probabilites: {}'.format(U))
    print('Demographic-numbers per group: {}'.format(V_sum))

# Initialise Fair Clustering variable
    fairness = True  # Setting False only runs unfair clustering
    elapsetimes = []
    avg_balance_set = []
    min_balance_set = []
    fairness_error_set = []
    E_cluster_set = []
    E_cluster_discrete_set = []
    bestacc = 1e10
    best_avg_balance = -1
    best_min_balance = -1
    labels = None

# Set value for the trade-off controller lambda
    if args.lmbda_tune:
        print('Lambda tune is true')
        lmbdas = np.arange(0, 10000, 100).tolist()
    else:
        lmbdas = [args.lmbda]
    length_lmbdas = len(lmbdas)

# Obtain initial clusters
    init_C_path = osp.join(data_dir, '{}_init_{}_{}.npz'.format(dataset, cluster_option, K))
    if not osp.exists(init_C_path):
        print('Generating initial seeds')
        C_init, labels_init = km_init(X, K, 'kmeans')
        np.savez(init_C_path, C_init=C_init, labels_init=labels_init)
    else:
        temp = np.load(init_C_path)
        C_init = temp['C_init']
        labels_init = temp['labels_init']

# Repeated iterations of fair_clustering
    C = []

    for count, lmbda in enumerate(lmbdas):
        print('Inside Lambda ', lmbda)

    # Calculate clustering measures
        C, labels, elapsed, S, E = fair_clustering(X, K, U, V, lmbda, args.L, fairness, cluster_option, cluster_init=C_init, labels_init=labels_init)
        print("C - ")
        print(C)
        print("S - ")
        print(S)
        print("l - ")
        print(labels)

    # Calculate fairness measures
        min_balance, avg_balance = get_fair_accuracy(U, V, labels, N, K)
        fairness_error = get_fair_accuracy_proportional(U, V, labels, N, K)
        print('lambda = {}, \n fairness_error {: .2f} and \n avg_balance = {: .2f} \n min_balance = {: .2f}'.format(lmbda, fairness_error, avg_balance, min_balance))

    # Assign (and print) new values to global values (if conditions match)
        if avg_balance > best_avg_balance:
            best_avg_balance = avg_balance
            best_lambda_avg_balance = lmbda
        if min_balance > best_min_balance:
            best_min_balance = min_balance
            best_lambda_min_balance = lmbda
        if fairness_error < bestacc:
            bestacc = fairness_error
            best_lambda_acc = lmbda
        print('Best fairness_error %0.4f' % bestacc, '|Error lambda = ', best_lambda_acc)
        print('Best  Avg balance %0.4f' % best_avg_balance, '| Avg Balance lambda = ', best_lambda_avg_balance)
        print('Best  Min balance %0.4f' % best_min_balance, '| Min Balance lambda = ', best_lambda_min_balance)
        print(float(E['fair_cluster_E'][0]))

    # Plot results of the iteration
        if plot_option_convergence is True and count == 0:
            filename = osp.join(output_path, 'Fair_{}_convergence_{}.png'.format(cluster_option, dataset))
            E_fair = E['fair_cluster_E']
            plot_convergence(cluster_option, filename, E_fair)

    # Add results to global arrays (for later reference?)
        elapsetimes.append(elapsed)
        avg_balance_set.append(avg_balance)
        min_balance_set.append(min_balance)
        fairness_error_set.append(fairness_error)
        E_cluster_set.append(E['cluster_E'][-1])
        E_cluster_discrete_set.append(E['cluster_E_discrete'][-1])

    # denormalized_final_cluster = utils.denormalizefea(normalized_final_cluster, X_unnormalised)
    # print("DENORMALIZED - ")
    # print(denormalized_final_cluster)
    print("-------------------")
    print(X.shape)
    print("Final Cluster - ")
    print(C)
    plotMap(X, C)

# Calculate elapsed time used by loop
    avgelapsed = sum(elapsetimes)/len(elapsetimes)
    # print('avg elapsed ', avgelapsed)

# Add few more plots if cluster options have them
    if plot_option_fairness_vs_clusterE is True and length_lmbdas > 1:
        savefile = osp.join(data_dir, 'Fair_{}_fairness_vs_clusterEdiscrete_{}.npz'.format(cluster_option, dataset))
        filename = osp.join(output_path, 'Fair_{}_fairness_vs_clusterEdiscrete_{}.png'.format(cluster_option, dataset))
        plot_fairness_vs_clusterE(cluster_option, savefile, filename, lmbdas, fairness_error_set, min_balance_set, avg_balance_set, E_cluster_discrete_set)
    if plot_option_balance_vs_clusterE is True and length_lmbdas > 1:
        savefile = osp.join(data_dir, 'Fair_{}_balance_vs_clusterEdiscrete_{}.npz'.format(cluster_option, dataset))
        filename = osp.join(output_path, 'Fair_{}_balance_vs_clusterEdiscrete_{}.png'.format(cluster_option, dataset))
        plot_balance_vs_clusterE(cluster_option, savefile, filename, lmbdas, fairness_error_set, min_balance_set, avg_balance_set, E_cluster_discrete_set)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Clustering with Fairness Constraints")

# Add clustering options
    parser.add_argument('--seed', type=int, default=None)
    parser.add_argument('-d', '--dataset', type=str, default='Facility')
    parser.add_argument('--cluster_option', type=str, default='kmeans')

# Add Plot options
    parser.add_argument('--plot_option_clusters_vs_lambda', default=False, type=str2bool, help="plot clusters in 2D w.r.t lambda")
    parser.add_argument('--plot_option_fairness_vs_clusterE', default=False, type=str2bool, help="plot clustering original energy w.r.t fairness")
    parser.add_argument('--plot_option_balance_vs_clusterE', default=False, type=str2bool, help="plot clustering original energy w.r.t balance")
    parser.add_argument('--plot_option_convergence', default=False, type=str2bool, help="plot convergence of the fair clustering energy")

# Add Lambda options
    parser.add_argument('--lmbda', type=float, default=50)  # specified lambda
    parser.add_argument('--lmbda-tune', type=str2bool, default=True)  # run in a range of different lambdas
    parser.add_argument('--L', type=float, default=2.0)  # Lipchitz value in bound update

# Save results to directory
    working_dir = osp.dirname(osp.abspath(__file__))
    parser.add_argument('--data_dir', type=str, metavar='PATH', default=osp.join(working_dir, 'data'))
    parser.add_argument('--output_path', type=str, metavar='PATH', default=osp.join(working_dir, 'outputs'))

# Start code
    main(parser.parse_args())