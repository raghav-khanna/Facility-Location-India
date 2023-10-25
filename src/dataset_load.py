import numpy as np
import os
import sys
import requests
import zipfile
import io
import pandas

__datasets = ['Facility']


def dataset_names():
    return __datasets


def read_dataset(name, data_dir):

    data = []
    sex_num = []
    K = []
    if name not in __datasets:
        raise KeyError("Dataset not implemented:", name)

    elif name == 'Facility':
        K = 7
        print("IN FACILITY ->>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        _path = 'Facility.data'  # Big dataset with 41108 samples
        data_path = os.path.join(data_dir, _path)
        df = pandas.read_csv(data_path, sep=',')
        print(df.columns)
        sex = df['pop_density'].astype(int).values
        sens_attributes = [0, 100000]

        df2 = df.loc[df['pop_density'] < sens_attributes[1]]
        df1 = df2.loc[df['pop_density'] < sens_attributes[0]]
        df2 = df2.loc[df['pop_density'] > sens_attributes[0]]
        df3 = df.loc[df['pop_density'] > sens_attributes[1]]
        df = [df1, df2, df3]
        df = pandas.concat(df)

        df = df[['latitude', 'longitude']].values
        # df = df[['age','duration','balance']].values

        sex_num = np.zeros(df.shape[0], dtype=int)
        sex_num[sex > sens_attributes[0]] = 1
        sex_num[sex > sens_attributes[1]] = 2

        data = np.array(df, dtype=float)

    else:
        print("Getting Passed")
        pass

    return data, sex_num, K