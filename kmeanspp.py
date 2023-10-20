import psycopg2
from dotenv import dotenv_values
from pyclustering.cluster.kmeans import kmeans, kmeans_visualizer
from pyclustering.cluster.center_initializer import kmeans_plusplus_initializer
from pyclustering.utils.metric import distance_metric, type_metric
from constants import haversine
import time


# The function for performing kmeans using the pyclustering library
def perform_kmeans(data, no_of_facilities):
    print('***********************************************************************\nProcessing of data starts')
    try:
        initial_centers = kmeans_plusplus_initializer(data, no_of_facilities).initialize()
    except:
        print('Error in center initialization in Kmeanspp')
        return []
    print('Initialised centers are:\n', initial_centers)
    print('***********************************************************************')

    haversine_distance = distance_metric(type_metric.USER_DEFINED, func=haversine)
    kmeans_instance = kmeans(data, initial_centers, metric=haversine_distance)
    print('K-means algorithm starts')

    try:
        kmeans_instance.process()
    except:
        print('Error in kmeans processing')
        return []

    return initial_centers, kmeans_instance


def display_results(coordinates, initial_centers, kmeans_instance):
    print('***********************************************************************')
    final_centers = kmeans_instance.get_centers()
    print('Final centers are:\n', final_centers)

    print('***********************************************************************')
    final_clusters = kmeans_instance.get_clusters()
    print('Final clusters are:\n', final_clusters)

    print('***********************************************************************')
    sse = kmeans_instance.get_total_wce()
    print('SSE of the clustering is', sse)

    plt = kmeans_visualizer.show_clusters(coordinates, final_clusters, final_centers, initial_centers=initial_centers, display=False)
    plt.savefig('map.png')

    # pip install numpy==1.23.4
    # CHECK if this function produces an animation?!
    # plt = kmeans_visualizer.animate_cluster_allocation(data, clusters, observer...)


def main():
    # Establish connection with the database
    print('***********************************************************************\nConnecting to the database...')
    db_details = dotenv_values('.env')
    conn = psycopg2.connect(dbname=db_details['DB_NAME'], user=db_details['DB_USER'], password=db_details['DB_PASS'], host=db_details['DB_HOST'])
    cur = conn.cursor()
    try:
        cur.execute("SELECT pop_density, latitude, longitude FROM districts;")
        data = cur.fetchall()
    except:
        print('Error in retrieving the data')
        exit(0)
    print('Data retrieved')

    # Iterate through the whole data and create an array of pairs (latitude and longitude for each district)
    coordinates = []
    for row in data:
        for num in range(0, row[0]):
            coordinates.append([float(row[1]), float(row[2])])

    try:
        initial_centers, kmeans_instance = perform_kmeans(coordinates, int(db_details['NO_OF_FACILITIES']))
        try:
            display_results(coordinates, initial_centers, kmeans_instance)
        except:
            print('Error while displaying the data')
        # CODE FOR RETRIEVING NAMES OF DISTRICTS BASED ON THEIR LATITUDE AND LONGITUDE
        # try:
        #     chosen_districts = []
        #     print('Retriving names of final_centers from the database')
        #     for point in final_centers:
        #         cur.execute("SELECT name, state FROM districts WHERE latitude = (%s) AND longitude = (%s);", (point[0], point[1]))
        #         res = cur.fetchone()
        #         chosen_districts.append(res)
        #     print(chosen_districts)
        #     print('***********************************************************************')
        # except:
    except:
        print("Error while performing Kmeans")
        exit(0)
    finally:
        print('Code terminates correctly')
        cur.close()
        conn.close()
        return


if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print("The time of execution of above program is :", (end-start) * 10**3, "ms")
