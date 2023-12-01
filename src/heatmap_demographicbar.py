import psycopg2
import matplotlib.pyplot as plt
from dotenv import dotenv_values
import matplotlib
import numpy as np
cur = []


def readVals(K: int, loc: str):
    f = open(loc + "/data/ziko_etal/centers.txt", "r")
    nums3 = f.read()
    while nums3[-1] == ' ' or nums3[-1] == '\n':
        nums3 = nums3[:len(nums3) - 1]
    f.close()
    C: list[list[float]] = []
    i = 0
    for L in nums3.split('], ['):
        if i == 0:
            L = L.strip(' [[')
        elif i == K - 1:
            L = L.strip(']]\n')
        i += 1
        C.append([float(x) for x in L.split(', ')])
    return C


def plotHeatMap(showClusters: bool, K: int, loc: str):
    try:
        cur.execute("SELECT latitude, longitude, pop_density FROM districts;")
        data = cur.fetchall()
    except Exception:
        print('Error in retrieving the data')
        exit(0)
    print('Data retrieved')
    X: list[float] = []
    Y: list[float] = []
    pop_density: int = []

    for point in data:
        X.append(point[0])
        Y.append(point[1])
        pop_density.append(point[2])
    plt.scatter(X, Y, marker='x', c=pop_density, cmap='hot_r', norm=matplotlib.colors.LogNorm())
    plt.colorbar()

    if showClusters is True:
        C = readVals(K, loc)
        X_c: list[float] = []
        Y_c: list[float] = []
        for point in C:
            X_c.append(point[0])
            Y_c.append(point[1])
        plt.scatter(X_c, Y_c, marker='o', c='b')
    plt.show()


def plotDemographicsOfCities(city_list):
    city_res_pair: dict[str, list[int]] = {}
    X = ['5-9', '10-14', '15-19', '20-24', '25-29', '30-34', '35-39', '40-49', '50-59', '60-69', '70-79', '80+']
    for city in city_list:
        try:
            cur.execute('SELECT area, demographics."5-9", demographics."10-14", demographics."15-19", demographics."20-24", demographics."25-29", demographics."30-34", demographics."35-39", demographics."40-49", demographics."50-59", demographics."60-69", demographics."70-79", demographics."80+" FROM demographics WHERE id = (SELECT id FROM districts WHERE name = %s);', (city,))
            data = cur.fetchone()
        except Exception:
            print('Error in retrieving the data')
            exit(0)

        Y: int = []
        for i in range(1, len(data)):
            Y.append(int(data[i] / data[0]))

        city_res_pair[city] = Y

    x = np.arange(len(X))
    width = 0.75 / len(city_list)
    multiplier = 0

    fig, ax = plt.subplots(layout='constrained')

    for attribute, measurement in city_res_pair.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute)
        ax.bar_label(rects, padding=3)
        multiplier += 1

    ax.set_ylabel('Population Density (per km²)')
    ax.set_title('Cities')
    ax.set_xticks(x + width, X)
    ax.legend(loc='upper left', ncols=3)
    ax.set_xlabel('Demographics based on Age')
    # ax.set_ylim(0, 250)
    plt.show()


def main():
    print('***********************************************************************\nConnecting to the database...')
    env_details = dotenv_values('.env')
    conn = psycopg2.connect(dbname=env_details['DB_NAME'], user=env_details['DB_USER'], password=env_details['DB_PASS'], host=env_details['DB_HOST'])
    global cur
    cur = conn.cursor()
    choice = int(input('Press 0 for heatmap and 1 for Demographics of Cities: '))
    if choice == 0:
        showClusters = bool(input('Do you want to display cluster centers: '))
        K = input("Enter Value of K for which you need the K-means Balance graph (default 3): ")
        if K == '':
            K = 3
        plotHeatMap(showClusters, int(K), env_details['PWD'])
    elif choice == 1:
        cities = input("Enter space-seperated cities: ")
        if len(cities) == 0:
            cities = ["Mumbai", "Lucknow", "Sambalpur"]
            plotDemographicsOfCities(cities)
    else:
        exit(0)


if __name__ == '__main__':
    main()
