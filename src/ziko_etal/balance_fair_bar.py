import numpy as np
import psycopg2
import matplotlib.pyplot as plt
from dotenv import dotenv_values
cur = []


def readVals(K: int, loc: str):
    f = open(loc + "/data/ziko_etal/labels.txt", "r")
    nums = f.read()
    while nums[-1] == ' ':
        nums = nums[:len(nums) - 1]
    if nums[-1] != '\n':
        nums = nums + '\n'
    f.close()

    f = open(loc + "/data/ziko_etal/protected.txt", "r")
    nums2 = f.read()
    f.close()

    f = open(loc + "/data/ziko_etal/centers.txt", "r")
    nums3 = f.read()
    while nums3[-1] == ' ' or nums3[-1] == '\n':
        nums3 = nums3[:len(nums3) - 1]
    f.close()

    labels = [int(x) for x in nums[1:len(nums) - 2].split(' ')]
    protected_groups = [int(x) for x in nums2[1:len(nums2) - 2].split(',')]
    C: list[list[float]] = []
    i = 0
    for L in nums3.split('], ['):
        if i == 0:
            L = L.strip(' [[')
        elif i == K - 1:
            L = L.strip(']]\n')
        i += 1
        C.append([float(x) for x in L.split(', ')])

    return labels, protected_groups, C


def ComputeDeviation(C, labels, protected_groups):
    print("----------------------------")
    # For each cluster, find the number of points in each protected group

    # for key in mapping:
    #     print("<-------------------------->")
    #     print("Cluster Center : ", C[key])
    #     print("Cluster Details -> ")
    #     for k in mapping[key]:
    #         print("Protected Group : ", k, " Count : ", mapping[key][k])
    #     print("<-------------------------->")

    mapping = {}
    print("Deviaion of each cluster from the perfectly balanced cluster:")
    print("----------------------------")
    for i in range(len(labels)):
        if labels[i] not in mapping:
            mapping[labels[i]] = {}
            mapping[labels[i]][protected_groups[i]] = 1
        elif protected_groups[i] not in mapping[labels[i]]:
            mapping[labels[i]][protected_groups[i]] = 1
        else:
            mapping[labels[i]][protected_groups[i]] += 1
    return mapping


def returnOne(demographic: str):
    cur.execute('SELECT SUM(demographics."' + demographic + '") FROM demographics')
    tot = cur.fetchone()[0]
    return tot


def returnTot():
    tot = 0
    cur.execute('SELECT SUM(demographics."5-9") FROM demographics')
    tot += cur.fetchone()[0]
    cur.execute('SELECT SUM(demographics."10-14") FROM demographics')
    tot += cur.fetchone()[0]
    cur.execute('SELECT SUM(demographics."15-19") FROM demographics')
    tot += cur.fetchone()[0]
    cur.execute('SELECT SUM(demographics."20-24") FROM demographics')
    tot += cur.fetchone()[0]
    cur.execute('SELECT SUM(demographics."25-29") FROM demographics')
    tot += cur.fetchone()[0]
    cur.execute('SELECT SUM(demographics."30-34") FROM demographics')
    tot += cur.fetchone()[0]
    cur.execute('SELECT SUM(demographics."35-39") FROM demographics')
    tot += cur.fetchone()[0]
    cur.execute('SELECT SUM(demographics."40-49") FROM demographics')
    tot += cur.fetchone()[0]
    cur.execute('SELECT SUM(demographics."50-59") FROM demographics')
    tot += cur.fetchone()[0]
    cur.execute('SELECT SUM(demographics."60-69") FROM demographics')
    tot += cur.fetchone()[0]
    cur.execute('SELECT SUM(demographics."70-79") FROM demographics')
    tot += cur.fetchone()[0]
    cur.execute('SELECT SUM(demographics."80+") FROM demographics')
    tot += cur.fetchone()[0]
    return tot


def plotDemographics(cluster_list: dict[int, dict[int, int]], roundVals: bool, showLabels: bool):
    cluster_res_pair = {}
    X = ['5-9', '10-14', '15-19', '20-24', '25-29', '30-34', '35-39', '40-49', '50-59', '60-69', '70-79', '80+']
    Y_ideal = []
    for demographic in X:
        if roundVals:
            Y_ideal.append(round(returnOne(demographic) / returnTot() * 100))
        else:
            Y_ideal.append(returnOne(demographic) / returnTot() * 100)

    cluster_res_pair['ideal'] = Y_ideal
    cur_cluster = 0
    tot_deviation = 0
    for cluster in cluster_list.items():
        cur_cluster += 1
        Y = np.zeros(12)
        tot_pop_density = 0
        for i in range(0, 12):
            Y[i] += cluster[1][i]
            tot_pop_density += cluster[1][i]
        Y = Y / tot_pop_density * 100
        cluster_res_pair['cluster ' + str(cur_cluster)] = Y
        diff: int
        if roundVals:
            diff = round(np.sum(np.abs(np.subtract(Y, Y_ideal))))
        else:
            diff = np.sum(np.abs(np.subtract(Y, Y_ideal)))
        tot_deviation += diff
        print("cluster ", cur_cluster, ": ", diff)

    print("Total Deviation from absolute balanced clustering: ", tot_deviation)
    x = np.arange(len(X))
    width = 0.75 / (len(cluster_list) + 1)
    multiplier = 0

    fig, ax = plt.subplots(layout='constrained')

    for attribute, measurement in cluster_res_pair.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute)
        if showLabels:
            ax.bar_label(rects, padding=3)
        multiplier += 1

    ax.set_ylabel('% Population Density in that cluster')
    ax.set_title('Balance of demographics for each cluster for Fair Clustering')
    ax.set_xticks(x + width, X)
    ax.legend(loc='upper left', ncols=len(cluster_list) + 1)
    ax.set_xlabel('Demographics based on Age')
    plt.show()


def main():
    print('***********************************************************************\nConnecting to the database...')
    env_details = dotenv_values('.env')
    conn = psycopg2.connect(dbname=env_details['DB_NAME'], user=env_details['DB_USER'], password=env_details['DB_PASS'], host=env_details['DB_HOST'])
    global cur
    cur = conn.cursor()
    K = input("Enter Value of K for which you need the K-means Balance graph (default 3): ")
    if K == '':
        K = 3
    roundVals = input("Press 1 to round values to ones digit while plotting the graph: ")
    if roundVals == '':
        roundVals = 0
    showLabels = input("Press 1 to display the ordinate values while plotting the graph: ")
    if showLabels == '':
        showLabels = 0
    labels, protected_groups, C = readVals(int(K), env_details['PWD'])
    clusterAssignment = ComputeDeviation(C, labels, protected_groups)
    plotDemographics(clusterAssignment, bool(roundVals), bool(showLabels))
    print("Function terminated!\n\n")


if __name__ == "__main__":
    main()
