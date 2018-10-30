# For data loading
from scipy.io import loadmat
# For splitting the data into test, train, validation splits
from sklearn.model_selection import train_test_split
# For manipulation of the arrays
import numpy as np
# For file manipulation and locating
import os
# For plotting
import json
# For showing progress
from tqdm import tqdm

import copy

# We define some constants that we are going to reuse
DATA_DIR = "data/"
RAW_DIR = "data/raw/"
PROCESSED_DIR = "data/processed/"
N = 14096
TOTAL_SIZE = 2048
H = 64
W = 32

def load_mat(file_path, label):
    """
    Loading of the data indexes of the images

    Parameters
    ----------
    file_path: str
        Name of the `.mat` input file
    label: str
        Name of the sheet for the indexes in the '.mat' input file

    Returns
    -------
    idxs: list
        * idxs corresponding to the given category
    """
    idxs = loadmat(file_path)[label].flatten()

    return (idxs)

def normalize(data):
    """
    Removes the mean of the image
    normalizses it between 0 and 1
    among all data poings

    Parameters
    ----------
    data: numpy matrix
        Data matrix with features

    Returns
    -------
    _data: numpy matrix
    """
    _data = []
    shape = data.shape
    for i in tqdm(range(len(data))):
         _data.append(copy.deepcopy((data[i] - data[i].mean(axis=0)) / data[i].std(axis=0)))
    _data = np.array(_data)
    _data = _data.reshape(shape)
    return _data

def save_data(data, file_path, name):
    """
    Saves the data
    given the name and
    the file path

    Parameters
    ----------
    data: numpy matrix
        Data matrix with features
    file_path: str
        File path where the file should be saved
    name: str
        Specific name of the given file

    """
    np.save(file_path + "{}.npy".format(name),data)

def preprocess():
    """
    1. Preprocesses the dataset into three splits: training, validation, test
    2. Performs z normalization on the three different chunks
    3. Saves the data

    Parameters
    ----------
    None

    Returns
    -------
    all_data: list
        * All the data split into lists of [features, labels]

    """
    types = ["training","query", "gallery"]
    print("Loading of index data...")

    labels = load_mat(RAW_DIR + "cuhk03_new_protocol_config_labeled.mat", "labels")
    _training_indexes = loadmat(RAW_DIR + 'cuhk03_new_protocol_config_labeled.mat')['train_idx'].flatten()
    _query_indexes = loadmat(RAW_DIR + 'cuhk03_new_protocol_config_labeled.mat')['query_idx'].flatten()
    _gallery_indexes = loadmat(RAW_DIR + 'cuhk03_new_protocol_config_labeled.mat')['gallery_idx'].flatten()
    camIds = loadmat(RAW_DIR + 'cuhk03_new_protocol_config_labeled.mat')['camId'].flatten()

    training_indexes = np.array([i-1 for i in _training_indexes])
    query_indexes = np.array([i-1 for i in _query_indexes])
    gallery_indexes = np.array([i-1 for i in _gallery_indexes])

    training_labels = labels[training_indexes]
    query_labels = labels[query_indexes]
    gallery_labels = labels[gallery_indexes]

    training_camId = camIds[training_indexes]
    query_camId = camIds[query_indexes]
    gallery_camId = camIds[gallery_indexes]

    print("Loading of features...")
    with open(RAW_DIR + "feature_data.json", 'r') as data:
        features = np.array(json.load(data))
        features = features.reshape((N,TOTAL_SIZE))

        _training_data = features[training_indexes,:]
        _query_data = features[query_indexes,:]
        _gallery_data = features[gallery_indexes,:]

        print("Normalizing data...")
        training_data = normalize(_training_data)
        query_data = normalize(_query_data)
        gallery_data = normalize(_gallery_data)

        print("Saving data...")
        all_data = [[training_data,training_labels, training_camId], \
                    [query_data, query_labels, query_camId], \
                    [gallery_data,gallery_labels, gallery_camId]]
        for i,t in enumerate(types):
            save_data(all_data[i][0],PROCESSED_DIR,"{}_features".format(t))
            save_data(all_data[i][1],PROCESSED_DIR,"{}_labels".format(t))
            save_data(all_data[i][2],PROCESSED_DIR,"{}_camId".format(t))

        return all_data

def load_data():
    """
    Load the cached data or call preprocess()
    to generate new data

    Parameters
    ----------
    None

    Returns
    -------
    all_data: list
        * All the data split into lists of [features, labels]

    """
    if not os.path.exists(os.path.join(DATA_DIR, "processed/", "training_features.npy")):
        print("Generating new data...")
        return preprocess()
    print("Loading data...")

    types = ["training","query", "gallery"]
    all_data = []
    for t in types:
        data = []
        data.append(np.load(PROCESSED_DIR + "{}_features.npy".format(t)))
        data.append(np.load(PROCESSED_DIR + "{}_labels.npy".format(t)))
        data.append(np.load(PROCESSED_DIR + "{}_camId.npy".format(t)))
        all_data.append(data)
    print("Finished loading data...")
    return all_data

if __name__ == '__main__':
    preprocess()