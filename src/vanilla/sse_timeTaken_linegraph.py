import matplotlib.pyplot as plt
from dotenv import dotenv_values


def Retreive_SSE_time_taken(f):
    star_counter = 0
    while star_counter != 6:
        if f.readline() == "***********************************************************************\n":
            star_counter += 1

    words = f.readline().split(" ")
    SSE = float(words[-1].replace("\n", ""))
    f.readline()
    words = f.readline().split(" ")
    time_taken = float(words[-2])
    return SSE, time_taken


def Collate_SSE_time_taken(plot_till_value: int, loc: str):
    SSE_of_clustering: dict[int, float] = {}
    Time_taken_by_clustering: dict[int, float] = {}
    for i in range(1, plot_till_value):
        location = loc + "/data/vanilla/" + str(i) + "-output.txt"
        f = open(location, "r")
        SSE, time_taken = Retreive_SSE_time_taken(f)
        SSE_of_clustering[i] = SSE
        Time_taken_by_clustering[i] = time_taken
        f.close()

    print("Values scraped")
    return SSE_of_clustering, Time_taken_by_clustering


def plotter(data, info):
    X = data.keys()
    Y = data.values()
    plt.plot(X, Y, marker='o')
    plt.title(info + ' vs K')
    plt.xlabel('no. of clusters(K)')
    plt.ylabel(info)
    plt.show()


def input_max_K():
    K = input("Till what value of K do you want to plot (number should be less than 645 and greater than 1)): ")
    if str(K).isnumeric() is True and int(K) < 645 and int(K) > 1:
        return int(K)
    else:
        exit(0)


def main():
    env_details = dotenv_values('.env')
    plot_till_value = 630
    plot_till_value = input_max_K()
    SSE, Time_taken = Collate_SSE_time_taken(plot_till_value, env_details['PWD'])
    plotter(SSE, "SSE")
    plotter(Time_taken, "Time Taken (in millisec)")


if __name__ == '__main__':
    main()
