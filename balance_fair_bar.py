import numpy as np
import psycopg2
import matplotlib.pyplot as plt
from dotenv import dotenv_values
cur = []


def readVals():
    f = open("labels.txt", "r")
    nums = f.read()
    f.close()

    f = open("protected.txt", "r")
    nums2 = f.read()
    f.close()

    labels = [int(x) for x in nums[1:len(nums) - 2].split(' ')]
    protected_groups = [int(x) for x in nums2[1:len(nums2) - 2].split(',')]
    C6 = [[0.50495261, 1.34617382], [0.31906353, 1.38396952], [0.41431652, 1.54980307], [0.34886035, 1.27571029], [0.20874683, 1.36621215], [0.44776925, 1.4599872]]
    C3 = [[0.4979076, 1.34766025], [0.27470139, 1.33591127], [0.42529846, 1.5141709]]
    return labels, protected_groups, C6


def showSensibleOutput(C, labels, protected_groups):
    # For each cluster, find the number of points in each protected group
    mapping = {}
    print("----------------------------")
    print("MAKING SENSE OF THE OUTPUT")
    print("----------------------------")
    for i in range(len(labels)):
        if labels[i] not in mapping:
            mapping[labels[i]] = {}
            mapping[labels[i]][protected_groups[i]] = 1
        elif protected_groups[i] not in mapping[labels[i]]:
            mapping[labels[i]][protected_groups[i]] = 1
        else:
            mapping[labels[i]][protected_groups[i]] += 1

    # for key in mapping:
    #     print("<-------------------------->")
    #     print("Cluster Center : ", C[key])
    #     print("Cluster Details -> ")
    #     for k in mapping[key]:
    #         print("Protected Group : ", k, " Count : ", mapping[key][k])
    #     print("<-------------------------->")

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


def plotDemographics(cluster_list: dict[int, dict[int, int]]):
    cluster_res_pair = {}
    X = ['5-9', '10-14', '15-19', '20-24', '25-29', '30-34', '35-39', '40-49', '50-59', '60-69', '70-79', '80+']
    Y_ideal = []
    for demographic in X:
        Y_ideal.append(round(returnOne(demographic) / returnTot() * 100))

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
        diff: int = round(np.sum(np.abs(np.subtract(Y, Y_ideal))))
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
        # ax.bar_label(rects, padding=3)
        multiplier += 1

    ax.set_ylabel('% Population Density in that cluster')
    ax.set_title('Balance of demographics for each cluster for Fair Clustering')
    ax.set_xticks(x + width, X)
    ax.legend(loc='upper left', ncols=len(cluster_list) + 1)
    ax.set_xlabel('Demographics based on Age')
    # ax.set_ylim(0, 250)
    plt.show()


def main():
    print('***********************************************************************\nConnecting to the database...')
    db_details = dotenv_values('.env')
    conn = psycopg2.connect(dbname=db_details['DB_NAME'], user=db_details['DB_USER'], password=db_details['DB_PASS'], host=db_details['DB_HOST'])
    global cur
    cur = conn.cursor()
    # temp()
    # K = int(input("Enter Value of K for which you need the K-means Balance graph: "))
    labels, protected_groups, C = readVals()
    clusterAssignment = showSensibleOutput(C, labels, protected_groups)
    plotDemographics(clusterAssignment)


if __name__ == "__main__":
    main()
