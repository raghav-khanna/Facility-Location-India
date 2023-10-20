import psycopg2
from dotenv import dotenv_values
from pyclustering.cluster.kmeans import kmeans, kmeans_visualizer
from pyclustering.cluster.center_initializer import kmeans_plusplus_initializer
from pyclustering.utils.metric import distance_metric, type_metric
from math import cos, sin, asin, sqrt
import time
import argparse

# Function for defining the custom distance metric (Haversine distance, in this case)
def haversine(point1, point2):
    lat1, lon1 = point1[0], point1[1]
    lat2, lon2 = point2[0], point2[1]
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r

# The function for performing kmeans using the pyclustering library
def perform_kmeans(data, no_of_facilities):

    try:
        # Get initial centers using kmeans++ initializer
        initial_centers = kmeans_plusplus_initializer(data, no_of_facilities).initialize()
        print(initial_centers)
    except Exception as error:
        # If the error is printed as - module 'numpy' has no attribute 'warnings'
        # Then do - pip uninstall numpy 
        # Then do - pip install numpy==1.23.4
        print(error)

    # Create instance of K-Means algorithm with custom distance metric
    haversine_distance = distance_metric(type_metric.USER_DEFINED, func=haversine)
    kmeans_instance = kmeans(data, initial_centers, metric=haversine_distance)


    # CHECK if this is NECESSARY? -> Most probably, yes
    kmeans_instance.process()

    # Get the FINAL CENTERS
    final_centers = kmeans_instance.get_centers()
    print(); print(final_centers)

    # Get the FINAL CLUSTERS
    clusters = kmeans_instance.get_clusters()

    # Get SSE
    sse = kmeans_instance.get_total_wce()
    print("SSE: ", sse)

    # visualise using the pyclustering visualiser function
    plt = kmeans_visualizer.show_clusters(data, clusters, final_centers, initial_centers=initial_centers, display=False)
    mapFileName = "data/results/" + str(no_of_facilities) + "-map.png"
    plt.savefig(mapFileName)

    # CHECK if this function produces an animation?!
    # plt = kmeans_visualizer.animate_cluster_allocation(data, clusters, observer...)

    return final_centers


def main():
    # Establish connection with the database
    db_details = dotenv_values('.env')
    conn = psycopg2.connect(dbname=db_details['DB_NAME'], user=db_details['DB_USER'], password=db_details['DB_PASS'], host=db_details['DB_HOST'])
    cur = conn.cursor()
    try:
        # Retrieve the data from the database
        cur.execute("SELECT pop_density, latitude, longitude FROM districts;")
        data = cur.fetchall()
        coordinates = []
        # Iterate through the whole data and create an array of pairs (latitude and longitude for each district)
        for row in data:
            for num in range(0, row[0]):
                coordinates.append([float(row[1]), float(row[2])])

        try:
            # Perform kmeans++ on the data
            final_cluster = perform_kmeans(coordinates, int(args.no_of_facilities))
            # print(final_cluster)

            # Get the final district names and states
            chosen_districts = []
            for point in final_cluster:
                cur.execute("SELECT name, state FROM districts WHERE latitude = (%s) AND longitude = (%s);", (point[0], point[1]))
                res = cur.fetchone()
                chosen_districts.append(res)

            print(chosen_districts)

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
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--no_of_facilities", help="Number of facilities to be chosen", type=int)
    args = parser.parse_args()
    start = time.time()
    main()
    end = time.time()
    print("Time taken: ", (end - start)*1000, "ms")