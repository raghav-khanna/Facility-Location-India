import psycopg2
import matplotlib.pyplot as plt
from dotenv import dotenv_values
import matplotlib
import numpy as np
cur = []


def plotHeatMap():
    try:
        cur.execute("SELECT latitude, longitude, pop_density FROM districts;")
        data = cur.fetchall()
    except Exception:
        print('Error in retrieving the data')
        exit(0)
    print('Data retrieved')
    X: float = []
    Y: float = []
    pop_density: int = []

    for point in data:
        X.append(point[0])
        Y.append(point[1])
        pop_density.append(point[2])
    plt.scatter(X, Y, marker='x', c=pop_density, cmap='hot_r', norm=matplotlib.colors.LogNorm())
    plt.colorbar()
    plt.show()


def plotDemographicsOfCity(city_list):
    city_res_pair = {}
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
            Y.append(int(data[i]/data[0]))

        city_res_pair[city] = Y

    x = np.arange(len(X))
    width = 0.25  # the width of the bars
    multiplier = 0

    fig, ax = plt.subplots(layout='constrained')

    for attribute, measurement in city_res_pair.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute)
        ax.bar_label(rects, padding=3)
        multiplier += 1

    ax.set_ylabel('Population Density')
    ax.set_title('Cities')
    ax.set_xticks(x + width, X)
    ax.legend(loc='upper left', ncols=3)
    ax.set_xlabel('Demographics')
    # ax.set_ylim(0, 250)
    plt.show()


def main():
    print('***********************************************************************\nConnecting to the database...')
    db_details = dotenv_values('.env')
    conn = psycopg2.connect(dbname=db_details['DB_NAME'], user=db_details['DB_USER'], password=db_details['DB_PASS'], host=db_details['DB_HOST'])
    global cur
    cur = conn.cursor()
    # plotHeatMap()
    plotDemographicsOfCity(["Mumbai", "Lucknow", "Sambalpur"])


if __name__ == '__main__':
    main()
