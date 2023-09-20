import psycopg2
from dotenv import dotenv_values
from pyclustering.cluster.kmeans import kmeans
from pyclustering.cluster.center_initializer import kmeans_plusplus_initializer
from pyclustering.utils.metric import distance_metric, type_metric
from math import cos, sin, asin, sqrt


# CHECK https://pyclustering.github.io/docs/0.8.2/html/db/d6d/classpyclustering_1_1cluster_1_1kmeans_1_1kmeans__visualizer.html


def haversine(point1, point2):
    lat1, lon1 = point1[0], point1[1]
    lat2, lon2 = point2[0], point2[1]
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r


def perform_kmeans(data):
    no_of_facilities = 20
    initial_centers = kmeans_plusplus_initializer(data, no_of_facilities).initialize()
    haversine_distance = distance_metric(type_metric.USER_DEFINED, func=haversine)

    print(initial_centers)
    kmeans_instance = kmeans(data, initial_centers, metric=haversine_distance)
    final_centers = kmeans_instance.get_centers()
    print()
    print(final_centers)


def main():
    db_details = dotenv_values('.env')
    conn = psycopg2.connect(dbname=db_details['DB_NAME'], user=db_details['DB_USER'], password=db_details['DB_PASS'], host=db_details['DB_HOST'])
    cur = conn.cursor()
    try:
        cur.execute("SELECT pop_density, latitude, longitude FROM districts;")
        data = cur.fetchall()
        coordinates = []
        for row in data:
            for num in range(0,row[0]):
                coordinates.append([float(row[1]), float(row[2])])
        
        try:
            perform_kmeans(coordinates)
        except:
            print("failed to perform kmeans")
        # print(data[0][0])
        print("Data Retrieved")
    except:
        print("failed to retrieve data")
    finally:
        cur.close()
        conn.close()
        return


if __name__ == "__main__":
    main()
