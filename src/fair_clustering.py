import numpy as np
import math
from sklearn.metrics.pairwise import haversine_distances as hs_dist
from sklearn.cluster import KMeans
# from sklearn.cluster.k_means_ import _init_centroids
from src.bound_update import bound_update, normalize_2, get_S_discrete
from src.utils import get_fair_accuracy, get_fair_accuracy_proportional
import timeit
import src.utils as utils
import multiprocessing.dummy as multiprocessing
from numba import jit
import numexpr as ne
import time


def kmeans_update(tmp):
    # print("ID of process running worker: {}".format(os.getpid()))
    X = utils.SHARED_VARS['X_i']
    X_tmp = X[tmp, :]
    c1 = X_tmp.mean(axis=0)
    return c1


@jit
def reduce_func(D_chunk, start):
    J = np.mean(D_chunk, axis=1)
    return J


def KernelBound_k(A, d, S_k, N):
    # S_k = S[:,k]
    volume_s_k = np.dot(np.transpose(d), S_k)
    volume_s_k = volume_s_k[0, 0]
    temp = np.dot(np.transpose(S_k), A.dot(S_k)) / (volume_s_k * volume_s_k)
    temp = temp * d
    temp2 = temp + np.reshape(- 2 * A.dot(S_k) / volume_s_k, (N, 1))

    return temp2.flatten()


@jit
def km_le(X, M):
    """
    Discretize the assignments based on center

    """
    h_dist = hs_dist(X, M)
    labels = h_dist.argmin(axis=1)
    return labels


# Fairness term calculation
def fairness_term_V_j(u_j, S, V_j):
    V_j = V_j.astype('float')
    S_term = np.maximum(np.dot(V_j, S), 1e-20)
    S_sum = np.maximum(S.sum(0), 1e-20)
    S_term = ne.evaluate('u_j*(log(S_sum) - log(S_term))')
    return S_term


def km_discrete_energy(h_dist, labels, k):
    tmp = np.asarray(np.where(labels == k)).squeeze()
    return np.sum(h_dist[tmp, k])


# Compute Fair Energy (i.e. Objective for LPP)
def compute_energy_fair_clustering(X, C, labels, S, U, V, bound_lambda, A=None, method_cl='kmeans'):
    J = len(U)
    N, K = S.shape
    clustering_E_discrete = []

    # Clustering term
    h_dist = hs_dist(X, C)
    h_dist2 = h_dist**2
    clustering_E = ne.evaluate('S*e_dist').sum()
    clustering_E_discrete = [km_discrete_energy(h_dist2, labels, k) for k in range(K)]
    clustering_E_discrete = sum(clustering_E_discrete)

    # Fairness term
    fairness_E = [fairness_term_V_j(U[j], S, V[j]) for j in range(J)]
    fairness_E = (bound_lambda*sum(fairness_E)).sum()

    # Total energy/objective
    E = clustering_E + fairness_E
    return E, clustering_E, fairness_E, clustering_E_discrete


# Initialise cluster centers
def km_init(X, K, cluster_init, labels_init=None):

    # If cluster_init is string, then
    if isinstance(cluster_init, str):
        if cluster_init == 'kmeans_plus':
            C = _init_centroids(X, K, init='k-means++')
            labels = km_le(X, C)
        elif cluster_init == 'kmeans':
            kmeans = KMeans(n_clusters=K).fit(X)
            labels = kmeans.labels_
            C = kmeans.cluster_centers_

    # If cluster_init is not a string, then
    else:
        C = cluster_init.copy()
        labels = labels_init.copy()
    del cluster_init, labels_init

    return C, labels


def restore_nonempty_cluster(X, K, oldlabels, oldC, oldS, ts):
    ts_limit = 2
    cluster_init_method = 'kmeans'
    if ts > ts_limit:
        # print('not having some labels')
        trivial_status = True
        labels = oldlabels.copy()
        C = oldC.copy()
        S = oldS.copy()

    else:
        # print('try with new seeds')

        C, labels = km_init(X, K, cluster_init_method)
        h_dist = hs_dist(X, C)
        sqdist = h_dist**2
        S = normalize_2(np.exp((-sqdist)))
        trivial_status = False

    return labels, C, S, trivial_status


# Proposed Fairness clustering method
def fair_clustering(X, K, U, V, lmbda, L, fairness=False, method='kmeans', cluster_init="kmeans_plus", labels_init=None, A=None):

    # Initialise variables
    N, Tot_dim = X.shape
    start_time = timeit.default_timer()
    C, labels = km_init(X, K, cluster_init, labels_init=labels_init)
    assert len(np.unique(labels)) == K
    ts = 0
    S = []
    E_org = []
    E_cluster = []
    E_fair = []
    E_cluster_discrete = []
    fairness_error = 0.0
    oldE = 1e100

    # Parallelise computation by creating threads
    maxiter = 15
    pool = multiprocessing.Pool(processes=20)
    utils.init(X_i=X)

    # Actual Algorithm
    for i in range(maxiter):
        oldC = C.copy()
        oldlabels = labels.copy()
        oldS = S.copy()

        if i == 0:
            h_dist = hs_dist(X, C)
            sqdist = h_dist**2
            a_p = sqdist.copy()
        else:
            tmp_list = [np.where(labels == k)[0] for k in range(K)]
            C_list = pool.map(kmeans_update, tmp_list)
            C = np.asarray(np.vstack(C_list))
            h_dist = hs_dist(X, C)
            sqdist = h_dist**2
            a_p = sqdist.copy()

        if fairness is True and lmbda != 0.0:
            l_check = a_p.argmin(axis=1)
            # Check for empty cluster
            if (len(np.unique(l_check)) != K):
                l, C, S, trivial_status = restore_nonempty_cluster(X, K, oldlabels, oldC, oldS, ts)
                ts = ts+1
                if trivial_status:
                    break
            bound_iterations = 10000
            labels, S, bound_E = bound_update(a_p, U, V, lmbda, L, bound_iterations)
            fairness_error = get_fair_accuracy_proportional(U, V, labels, N, K)
            print('fairness_error = {:0.4f}'.format(fairness_error))

        else:
            S = get_S_discrete(labels, N, K)
            labels = km_le(X, C)

        currentE, clusterE, fairE, clusterE_discrete = compute_energy_fair_clustering(X, C, labels, S, bound_update, V, lmbda, A=A, method_cl=method)
        E_org.append(currentE)
        E_cluster.append(clusterE)
        E_fair.append(fairE)
        E_cluster_discrete.append(clusterE_discrete)

        if (len(np.unique(l)) != K) or math.isnan(fairness_error):
            labels, C, S, trivial_status = restore_nonempty_cluster(X, K, oldlabels, oldC, oldS, ts)
            ts = ts+1
            if trivial_status:
                break

        if (i > 1 and (abs(currentE-oldE) <= 1e-4*abs(oldE))):
            print('......Job  done......')
            break

        else:
            oldE = currentE.copy()

    # Stop Parallelisation and return values
    pool.close()
    pool.join()
    pool.terminate()
    elapsed = timeit.default_timer() - start_time
    print(elapsed)
    E = {'fair_cluster_E': E_org, 'fair_E': E_fair, 'cluster_E': E_cluster, 'cluster_E_discrete': E_cluster_discrete}
    return C, labels, elapsed, S, E