import pandas as pd
import numpy as np
import random

from degrade_data.restructure_data import read_and_shape_data

def index_number(max_number, list_index_chosen):
    """This function randomly defines an index number and ensures that no index number is assigned twice.
    
    Parameters:
        max_number (int)            :Higher bound of the index number.
        list_index_chosen (lst)     :List of indeces that have already been chosen.
        
    Returns:
        index (int)                 :Index number."""
    index = random.randint(0, max_number)

    if index in list_index_chosen:
        return index_number(max_number, list_index_chosen)

    list_index_chosen.append(index)
    return index

def delete_values_completely_random(percentage, dataframe):
    """This function deletes an user-defined percentages values from the observed dataframe, based on the Missing 
    Value Completely Random type. It replaces the values with a None value.
    
    Parameters:
        percentage (float): Percentage of missing values.
        dataframe       : Dataframe of data to delete values. 
        
    Returns:
        missing_df      : Dataframe with missing values given the percentage. """

    #Convert values of dataframe to one list
    list_data = [value for in_list in dataframe.values.tolist() for value in in_list]

    #Determine how many values need to be deleted
    num_choice = int(round(percentage*len(list_data)))

    
    #Replace value of list with NaN value
    list_index_chosen = []
    num = 0 
    for num in range(num_choice):
        index = index_number(len(list_data)-1, list_index_chosen)
        list_data[index] = None
        num += 1

    #Split the list in number of rows of dataframe
    splitted_list = np.array_split(list_data, len(dataframe))
    

    #Reformat list to dataframe
    missing_df = pd.DataFrame(data = splitted_list, columns=dataframe.columns.tolist())

    return missing_df