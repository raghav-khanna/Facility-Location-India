import numpy as np
import os
import pandas

def read_dataset(data_dir):

    # Initialise variables
    data = []
    protected_groups = []
    K = 7
    _path = 'Facility.data'  # Big dataset with 41108 samples
    data_path = os.path.join(data_dir, _path)

# Read CSV
    df = pandas.read_csv(data_path, sep=',')
    pop_density = df['pop_density'].astype(int).values

# Sort data on the basis of protected groups
    sens_attributes = [5000, 100000]
    df2 = df.loc[df['pop_density'] < sens_attributes[1]]
    df1 = df2.loc[df['pop_density'] < sens_attributes[0]]
    df2 = df2.loc[df['pop_density'] > sens_attributes[0]]
    df3 = df.loc[df['pop_density'] > sens_attributes[1]]
    df = [df1, df2, df3]
    df = pandas.concat(df)

# Assign each protected group a unique id
    df = df[['latitude', 'longitude']].values
    protected_groups = np.zeros(df.shape[0], dtype=int)
    protected_groups[pop_density > sens_attributes[0]] = 1
    protected_groups[pop_density > sens_attributes[1]] = 2
    data = np.array(df, dtype=float)

    return data, protected_groups, K
