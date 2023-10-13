import numpy as np
import os
import sys
import requests
import zipfile
import io
import pandas

__datasets = ['Facility', 'Bank', 'Synthetic', 'Synthetic-unequal', 'CensusII']


def dataset_names():
    return __datasets


def read_dataset(name, data_dir):

    data = []
    sex_num = []
    K = []
    if name not in __datasets:
        raise KeyError("Dataset not implemented:", name)

    elif name == 'Bank':
        # n= 6000
        # K = 4
        K = 10
        _path = 'bank-additional-full.csv'  # Big dataset with 41108 samples
        # _path = 'bank.csv' # most approaches use this small version with 4521 samples
        data_path = os.path.join(data_dir, _path)
        if (not os.path.exists(data_path)):

            print('Bank dataset does not exist in current folder --- Have to download it')
            r = requests.get('https://archive.ics.uci.edu/ml/machine-learning-databases/00222/bank-additional.zip', allow_redirects=True)
            # r = requests.get('https://archive.ics.uci.edu/ml/machine-learning-databases/00222/bank.zip', allow_redirects=True)
            if r.status_code == requests.codes.ok:
                print('Download successful')
            else:
                print('Could not download - please download')
                sys.exit()

            z = zipfile.ZipFile(io.BytesIO(r.content))
            # z.extract('bank-additional/bank-additional-full.csv','./data')
            open(data_path, 'wb').write(z.read('bank-additional/bank-additional-full.csv'))
            # open(data_path, 'wb').write(z.read('bank.csv'))

        df = pandas.read_csv(data_path, sep=';')
        print(df.columns)
#        shape = df.shape

#        df = df.loc[np.random.choice(df.index, n, replace=False)]
        sex = df['marital'].astype(str).values
        sens_attributes = list(set(sex))

        if 'unknown' in sens_attributes:
            sens_attributes.remove('unknown')

        df1 = df.loc[df['marital'] == sens_attributes[0]]
        df2 = df.loc[df['marital'] == sens_attributes[1]]
        df3 = df.loc[df['marital'] == sens_attributes[2]]

        df = [df1, df2, df3]
        df = pandas.concat(df)

        sex = df['marital'].astype(str).values

        df = df[['age', 'duration', 'euribor3m', 'nr.employed', 'cons.price.idx', 'campaign']].values
        # df = df[['age','duration','balance']].values

        sens_attributes = list(set(sex))
        sex_num = np.zeros(df.shape[0], dtype=int)
        sex_num[sex == sens_attributes[1]] = 1
        sex_num[sex == sens_attributes[2]] = 2

        data = np.array(df, dtype=float)

    elif name == 'Facility':
        K = 3
        _path = 'Facility.data'  # Big dataset with 41108 samples
        data_path = os.path.join(data_dir, _path)
        df = pandas.read_csv(data_path, sep=',')
        print(df.columns)
        sex = df['pop_density'].astype(int).values
        sens_attributes = [1000, 10000]

        df2 = df.loc[df['pop_density'] < sens_attributes[1]]
        df1 = df2.loc[df['pop_density'] < sens_attributes[0]]
        df2 = df2.loc[df['pop_density'] > sens_attributes[0]]
        df3 = df.loc[df['pop_density'] > sens_attributes[1]]
        df = [df1, df2, df3]
        df = pandas.concat(df)

        df = df[['id', 'latitude', 'longitude']].values
        # df = df[['age','duration','balance']].values

        sex_num = np.zeros(df.shape[0], dtype=int)
        sex_num[sex > sens_attributes[0]] = 1
        sex_num[sex > sens_attributes[1]] = 2

        data = np.array(df, dtype=float)

    else:
        pass

    return data, sex_num, K


if __name__ == '__main__':

    dataset = 'CensusII'
    datas = np.load('../data/CensusII.npz')['data']
    X_org = datas['X_org']
    demograph = datas['demograph']

    V_list = [np.array(demograph == j) for j in np.unique(demograph)]
    V_sum = [x.sum() for x in V_list]
    print('Balance of the dataset {}'.format(min(V_sum)/max(V_sum)))
    u_V = [x/X_org.shape[0] for x in V_sum]
