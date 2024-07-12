"""
Created on: 12-7-2021 13:22

@author: IvS
"""

import pandas as pd
import numpy as np
import random
import math
from collections import defaultdict

from degrade_data.missing_data import delete_values_completely_random
from degrade_data.noise_data import assign_noise
from degrade_data.bias_data import assign_bias, sample_bias


class Node(object):
    def __init__(self, full_data_set, data_set, name, level):
        self.name = name
        self.level = level

        self.quantity = 0
        self.quality = 0

        self.scv = self.calculate_visibility_per_node(full_data_set[name], data_set[name])

        self.average_inventory = np.mean(full_data_set[name])

    def calculate_visibility_per_node(self, full_data_node, data_set_node):
        """ Calculate the visibility of one node based on the quantity and the quality of the data set. The visibility
        is the square root of the product of the quantity and the quality. """
        quantity_per_node = self.calculate_quantity_per_node(full_data_node, data_set_node)
        quality_per_node = max(0, self.calculate_quality_per_node(full_data_node, data_set_node)) #cannot be zero

        visibility = math.sqrt(quantity_per_node * quality_per_node)
        #print("Visibility of node", self.name, "is", visibility, "%")

        return visibility

    def calculate_quantity_per_node(self, full_data_node, data_set_node):
        """" Quantity is the percentage of data points compared to the full data set. """
        percentage_quantity = (data_set_node.count() / full_data_node.count()) * 100
        self.quantity = percentage_quantity
        return self.quantity

    def calculate_quality_per_node(self, full_data_node, data_set_node):
        """ Quality is the 100 - mean absolute percentage error of the data set compared to the full data set.
        Data rows that include a missing value, given the data set, are deleted. """
        combine_datasets = pd.concat([full_data_node, data_set_node], axis=1).dropna(axis=0)
        if combine_datasets.eq(0).all()[0] == True and combine_datasets.eq(0).all()[1] == True:
            percentage_quality = 0 #all values are zero
        else:
            percentage_quality = self.MAPE(combine_datasets.iloc[:, 0], combine_datasets.iloc[:, 1])
        self.quality = 100 - percentage_quality

        return self.quality

    def MAPE(self, Y_actual, Y_Predicted):
        """Mean Absolute Percentage Error"""
        data = ((Y_actual - Y_Predicted)/ (Y_actual))
        mape = np.mean(np.abs((Y_actual - Y_Predicted) / np.mean(Y_actual))) * 100
        return mape


def create_missing_value_df(data_frame, percentage,**kwargs):
    """Create missing values in a data frame based on the user-defined percentage."""
    random.seed(2)
    if "seed" in kwargs:
        random.seed(kwargs["seed"])
        #print("Seed is", kwargs["seed"])

    #print("Percentage of missing values is " + str(percentage))
    data_frame_data = data_frame.iloc[:, :-2]
    data_frame_scenrep = data_frame.iloc[:, -2:]

    missing_values = delete_values_completely_random(percentage, data_frame_data)
    total_missing_values = pd.concat([missing_values, data_frame_scenrep], axis=1)

    return total_missing_values

def create_noise_df(data_frame, percentage,**kwargs):
    """Create noise in a data frame based on the user-defined percentage."""
    random.seed(2)
    np.random.seed(2)
    if "seed" in kwargs:
        random.seed(kwargs["seed"])
        np.random.seed(kwargs["seed"])
        #print("Seed is", kwargs["seed"])

    #print("Percentage of noise is " + str(percentage))
    data_frame_data = data_frame.iloc[:, :-2]
    data_frame_scenrep = data_frame.iloc[:, -2:]

    noise_df = assign_noise(percentage, data_frame_data)
    total_noise_df = pd.concat([noise_df, data_frame_scenrep], axis=1)

    return total_noise_df

def create_bias_df(data_frame, percentage, **kwargs):
    """Create bias in a data frame based on the user-defined percentage."""
    np.random.seed(2)
    if "seed" in kwargs:
        np.random.seed(kwargs["seed"])
        #print("Seed is", kwargs["seed"])

    #print("Percentage of bias is " + str(percentage))
    data_frame_data = data_frame.iloc[:, :-2]
    data_frame_scenrep = data_frame.iloc[:, -2:]

    bias_df = sample_bias(data_frame_data, percentage)
    total_bias_df = pd.concat([bias_df, data_frame_scenrep], axis=1)

    return total_bias_df


def calculate_supply_chain_visibility(data_set, percentage_missing, names_nodes, levels_nodes, dim_sparseness="missing",
                                      seed=2):
    """ Data set and percentage of missing values to calculate supply chain visibility for.
    The global measure for the level of visibility is the weighted average of the metrics assessed for each node."""

    #TODO change this to missing value, noise and bias (and relevance)
    if str.lower(dim_sparseness) == "noise":
        df_degrade_data = create_noise_df(data_set, percentage=percentage_missing, seed=seed)
        df_degrade_data.iloc[:, 1:] = df_degrade_data.iloc[:, 1:].apply(pd.to_numeric)
    if str.lower(dim_sparseness) == "missing":
        df_degrade_data = create_missing_value_df(data_set, percentage=percentage_missing, seed=seed)
        df_degrade_data.iloc[:, 1:] = df_degrade_data.iloc[:, 1:].apply(pd.to_numeric)
    if str.lower(dim_sparseness) == "relevance":
        df_degrade_data = create_relevance_df(data_set, percentage=percentage_missing, seed=seed)
        df_degrade_data.iloc[:, 1:] = df_degrade_data.iloc[:, 1:].apply(pd.to_numeric)
    if str.lower(dim_sparseness) == "bias":
        df_degrade_data = create_bias_df(data_set, percentage=percentage_missing, seed=seed)
        df_degrade_data.iloc[:, 1:] = df_degrade_data.iloc[:, 1:].apply(pd.to_numeric)

    nodes = []
    for name, level in zip(names_nodes, levels_nodes):
        node = Node(data_set, df_degrade_data, name, level)
        nodes.append(node)
        #print(node.name, "quality", node.quality, "quantity", node.quantity)

    #Determine weights
    inventory_nodes = [node.average_inventory for node in nodes]
    norm_weights = normalize(inventory_nodes)

    scv_weight_inventory = sum([node.scv*weight for node, weight in zip(nodes, norm_weights)])

    #print("Global supply chain visibility is ", scv_weight_inventory, "%")

    return scv_weight_inventory, nodes

def determine_weight_levels(levels):
    """ Levels is a list with the level of which the actors in the supply chain is.
    The closer the location, the more weight is assigned."""
    dist = np.empty([len(levels), len(levels)])

    for i in range(len(levels)):
        for j in range(len(levels)):
            dist[i][j] = abs(levels[i]-levels[j])

    average_distance = [np.mean(dist[i]) for i in range(len(dist))]

    normalized_distance = normalize(average_distance)
    #Invert range
    normalized_distance = [(1-norm) for norm in normalized_distance]

    return normalized_distance

def normalize(lst):
    norm = [float(i) / sum(lst) for i in lst]
    return norm

