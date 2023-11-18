import psycopg2
import matplotlib.pyplot as plt
from dotenv import dotenv_values
import numpy as np
cur = []


def plotDemographicsOfCity(cluster_list: list[list[int]]):
    cluster_res_pair = {}
    X = ['5-9', '10-14', '15-19', '20-24', '25-29', '30-34', '35-39', '40-49', '50-59', '60-69', '70-79', '80+']
    cur_cluster = 0
    for cluster in cluster_list:
        cur_cluster += 1
        Y = np.zeros(12)
        for districtId in cluster:
            try:
                cur.execute('SELECT area, demographics."5-9", demographics."10-14", demographics."15-19", demographics."20-24", demographics."25-29", demographics."30-34", demographics."35-39", demographics."40-49", demographics."50-59", demographics."60-69", demographics."70-79", demographics."80+" FROM demographics WHERE id = (SELECT id FROM districts WHERE id = %s);', (districtId,))
                data = cur.fetchone()
            except Exception:
                print('Error in retrieving the data')
                exit(0)
            for i in range(1, len(data)):
                Y[i-1] += (int(data[i]/data[0]))

        cluster_res_pair['cluster ' + str(cur_cluster)] = Y

    x = np.arange(len(X))
    width = 0.75/len(cluster_list)
    multiplier = 0

    fig, ax = plt.subplots(layout='constrained')

    for attribute, measurement in cluster_res_pair.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute)
        # ax.bar_label(rects, padding=3)
        multiplier += 1

    ax.set_ylabel('Population Density')
    ax.set_title('Balance of demographics for each cluster')
    ax.set_xticks(x + width, X)
    ax.legend(loc='upper left', ncols=len(cluster_list))
    ax.set_xlabel('Demographics')
    # ax.set_ylim(0, 250)
    plt.show()


def retrieveClusterAssignment(K: int):
    location = "./data/" + str(K) + "-output.txt"
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
        elif i == K-1:
            L = L.strip(']]\n')
        i += 1
        clusterAssignment.append([int(x) for x in L.split(', ')])

    f.close()
    return clusterAssignment


def main():
    print('***********************************************************************\nConnecting to the database...')
    db_details = dotenv_values('.env')
    conn = psycopg2.connect(dbname=db_details['DB_NAME'], user=db_details['DB_USER'], password=db_details['DB_PASS'], host=db_details['DB_HOST'])
    global cur
    cur = conn.cursor()
    K = int(input("Enter Value of K for which you need the K-means Balance graph: "))
    clusterAssignment = retrieveClusterAssignment(K)
    plotDemographicsOfCity(clusterAssignment)


if __name__ == '__main__':
    main()
