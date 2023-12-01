import psycopg2
import matplotlib.pyplot as plt
from dotenv import dotenv_values
import numpy as np
cur = []


def retrieveClusterAssignment(K: int, loc: str):
    location = loc + "/data/vanilla/" + str(K) + "-output.txt"
    f = open(location, 'r')
    star_counter = 0
    while star_counter != 5:
        if f.readline() == "***********************************************************************\n":
            star_counter += 1

    f.readline()
    clusterAssignment: list[list[int]] = []
    i = 0
    for L in f.readline().split('], ['):
        if i == 0:
            L = L.strip(' [[')
        elif i == K - 1:
            L = L.strip(']]\n')
        i += 1
        clusterAssignment.append([int(x) for x in L.split(', ')])

    f.close()
    return clusterAssignment


def returnOne(demographic: str):
    cur.execute('SELECT SUM(demographics."' + demographic + '") FROM demographics')
    tot = cur.fetchone()[0]
    return tot


def returnTot():
    # X = ['5-9', '10-14', '15-19', '20-24', '25-29', '30-34', '35-39', '40-49', '50-59', '60-69', '70-79', '80+']
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
    for cluster in cluster_list:
        cur_cluster += 1
        Y = np.zeros(12)
        tot_pop_density = 0
        for districtId in cluster:
            try:
                cur.execute('SELECT area, demographics."5-9", demographics."10-14", demographics."15-19", demographics."20-24", demographics."25-29", demographics."30-34", demographics."35-39", demographics."40-49", demographics."50-59", demographics."60-69", demographics."70-79", demographics."80+" FROM demographics WHERE id = (SELECT id FROM districts WHERE id = %s);', (districtId,))
                data = cur.fetchone()
            except Exception:
                print('Error in retrieving the data')
                exit(0)
            for i in range(1, len(data)):
                Y[i - 1] += (int(data[i] / data[0]))
                tot_pop_density += (int(data[i] / data[0]))

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
    ax.set_title('Balance of demographics for each cluster for Vanilla')
    ax.set_xticks(x + width, X)
    ax.legend(loc='upper left', ncols=len(cluster_list) + 1)
    ax.set_xlabel('Demographics')
    # ax.set_ylim(0, 250)
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
    clusterAssignment = retrieveClusterAssignment(int(K), env_details['PWD'])
    plotDemographics(clusterAssignment, bool(roundVals), bool(showLabels))
    print("Function terminated!\n\n")


if __name__ == '__main__':
    main()
