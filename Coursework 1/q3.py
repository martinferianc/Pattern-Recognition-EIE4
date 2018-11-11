import numpy as np
import matplotlib.pyplot as plt
import time
import tqdm
import copy
from random import randint, sample
from statistics import mode

from pre_process_raw import load_data
from lda import LDA

def sample_rnd(train_y,sample_size):
    max_size = train_y.shape[0]
    return [randint(0,max_size-1) for i in range(sample_size)]

def sample_stratified(train_y,sample_size):
    # Set of labels
    labels = np.unique(train_y)

    rnd_indices = []

    # Get indices for each
    for label in labels:
        # Get indices for those labels
        indices = []
        for i in range(train_y.shape[0]):
            indices.append(i) if (train_y[i] == label) else 0
        # sample subset of indices
        rnd_indices.extend(sample(indices,sample_size))
    return rnd_indices

def committe_machine_majority_vote(labels):
    # number of machines
    num_machines = len(labels)

    # number of labels
    num_labels = len(labels[0])

    labels_out = []

    for i in range(num_labels):
        votes = []
        for j in range(num_machines):
            votes.append(labels[j][i])
        labels_out.append(max(set(votes), key = votes.count))

    return labels_out

def random_parameters(M0,M1,max_size=405):
    pass

def identity_error(labels, labels_correct):
    err = 0
    for i in range(len(labels)):
        if labels[i] != labels_correct[i]:
            err += 1
    #normalise by size of labels
    return err/len(labels)

def main():

    # Load dataset
    dataset = load_data()

    '''

    ##############
    # BASIC TEST #
    ##############

    # Setup
    lda = LDA()
    lda.dataset = copy.deepcopy(dataset)
    lda.run_setup()

    # Set hyper parameters
    lda.M_pca = 100
    lda.M_lda = 50

    # Run
    lda.run_pca_lda()
    lda.run_nn_classifier()

    '''

    '''
    ######################
    # PCA-LDA EVALUATION #
    ######################

    # Evaluate for different M_pca
    M_pca = [5,20,50,100]
    M_lda = [5,20,50,100]

    for m_pca in M_pca:
        for m_lda in M_lda:
            # Setup
            lda = LDA()
            lda.dataset = copy.deepcopy(dataset)
            lda.run_setup()

            # Set hyper parameters
            lda.M_pca = m_pca
            lda.M_lda = m_lda
results
            # Run
            lda.run_pca_lda()
            lda.run_nn_classifier()


    '''

    ###################
    # PCA-LDA BAGGING #
    ###################

    # Number of machines
    NUM_MACHINES = 5

    # Machine Parameters
    M_pca = 100
    M_lda = 50
    sample_size = 5

    machine = [LDA() for i in range(NUM_MACHINES)]

    for i in range(NUM_MACHINES):
        # Randomly sample training data TODO try stratified and un-stratified
        #sample_index = sample_rnd(dataset['train_y'],sample_size)
        sample_index = sample_stratified(dataset['train_y'],sample_size)

        # assign dataset for machine
        machine[i].dataset['train_x'] = copy.deepcopy(dataset['train_x'][:,sample_index])
        machine[i].dataset['train_y'] = copy.deepcopy(dataset['train_y'][sample_index])

        machine[i].dataset['test_x'] = copy.deepcopy(dataset['test_x'])
        machine[i].dataset['test_y'] = copy.deepcopy(dataset['test_y'])

        # Setup each machine
        machine[i].run_setup()
        machine[i].M_pca = M_pca
        machine[i].M_lda = M_lda

    # variable to store label results
    labels =  [[] for i in range(NUM_MACHINES)]

    for i in range(NUM_MACHINES):
        machine[i].run_pca_lda()
        _, labels[i] = machine[i].run_nn_classifier()

    # get committee machine output
    labels_out = committe_machine_majority_vote(labels)
    err = identity_error(labels_out,dataset['test_y'])

    print('error: ',err)

    ###################
    # PCA-LDA BAGGING #
    ###################

    # Number of machines
    NUM_MACHINES = 5

    # Machine Parameters
    M0 = 50
    M1 = 25

    M_pca = 100
    M_lda = 50
    sample_size = 5

    machine = [LDA() for i in range(NUM_MACHINES)]

    for i in range(NUM_MACHINES):
        # Randomly sample training data TODO try stratified and un-stratified
        #sample_index = sample_rnd(dataset['train_y'],sample_size)
        sample_index = sample_stratified(dataset['train_y'],sample_size)

        # assign dataset for machine
        machine[i].dataset['train_x'] = copy.deepcopy(dataset['train_x'][:,sample_index])
        machine[i].dataset['train_y'] = copy.deepcopy(dataset['train_y'][sample_index])

        machine[i].dataset['test_x'] = copy.deepcopy(dataset['test_x'])
        machine[i].dataset['test_y'] = copy.deepcopy(dataset['test_y'])

        # Setup each machine
        machine[i].run_setup()
        machine[i].M_pca = M_pca
        machine[i].M_lda = M_lda

    # variable to store label results
    labels =  [[] for i in range(NUM_MACHINES)]

    for i in range(NUM_MACHINES):
        machine[i].run_pca_lda()
        _, labels[i] = machine[i].run_nn_classifier()

    # get committee machine output
    labels_out = committe_machine_majority_vote(labels)
    err = identity_error(labels_out,dataset['test_y'])

    print('error: ',err)

if __name__ == '__main__':
    main()
