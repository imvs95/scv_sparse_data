import pandas as pd
import numpy as np
import random
import datetime
from itertools import chain

from degrade_data.restructure_data import read_and_shape_data, create_dict_alternatives

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

def assign_noise(percentage, dataframe, percentage_noise_width=1, date_delta=182, dict_alternatives=None):
    """This function assigns noise to an user-defined percentages values from the observed dataframe. Categorial units are replaced 
    by an alternative of a selected list. Numerical units are replace by alternative following a Normal distribution.
    
    Parameters:
        percentage (int): Percentage of missing values.
        dataframe       : Dataframe of data to delete values. 
        
    Returns:
        noise_df      : Dataframe with noise given the percentage. """

    #Convert values of dataframe to one list
    list_data = [value for in_list in dataframe.values.tolist() for value in in_list]

    #Determine how many values need to be deleted
    num_choice = int(round(percentage*len(list_data)))
    
    #Replace value with an alternative
    list_index_chosen = []
    num = 0 
    for num in range(num_choice):
        index = index_number(len(list_data)-1, list_index_chosen)
        list_data[index] = determine_noise(list_data[index], percentage_noise_width, date_delta, dict_alternatives)
        num += 1

    #Split the list in number of rows of dataframe
    splitted_list = np.array_split(list_data, len(dataframe))

    #Reformat list to dataframe
    noise_df = pd.DataFrame(data = splitted_list, columns=dataframe.columns.tolist())

    return noise_df

# %%
def determine_noise(value, percentage_noise_width, date_delta, dict_alternatives):
    """This function determines noise for a specific value. Categorial units are replaced by an alternative 
     of a selected list following an Uniform distribution. Numerical units are replaced by alternative 
     following a Normal distribution with as mean the value itself and the standard deviation determined by the
     user-defined percentage of noise width. Default is 100% for uniformity.
    
    Parameters:
        value                      : Value to add noise to.
        percentage_noise_width     : Percentage of the value that is marked as the standard deviation.
        date_delta                 : Number of days that is used for the standard deviation of the date.  
        dict_alternatives          : Dictonairy with column name as key and a list of alternatives as value.

    Returns:
        noise_value                : Value with noise. """

    if type(value) == float or type(value) == int:
        if value >= 0:
            #For the continous numerical values
            noise_value = np.random.normal(value, percentage_noise_width*value)
            return noise_value
        else:
            #For the Latitude and Longitude
            noise_value = -abs(np.random.normal(abs(value), percentage_noise_width*abs(value)))
            return noise_value

    if type(value) == datetime.time:
        noise_value_time = noise_in_time(value, percentage_noise_width)

       
        return noise_value_time

    try:
        if type(datetime.datetime.strptime(str(value), '%Y-%m-%d')) == datetime.datetime:
            #For Date with the use of proleptic Gregorian ordinal
            date_time = datetime.datetime.strptime(str(value), '%Y-%m-%d')
            date_ordinal = date_time.date().toordinal()
            noise_value = datetime.date.fromordinal(round(np.random.normal(date_ordinal, date_delta))).strftime("%Y-%m-%d")
            
            return noise_value
    except ValueError:
        pass

    try:
        if type(datetime.datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S')) == datetime.datetime:
            # For Date and time with the use of proleptic Gregorian ordinal
            date_time = datetime.datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S')
            date_ordinal = date_time.date().toordinal()
            noise_date = datetime.date.fromordinal(round(np.random.normal(date_ordinal, date_delta)))
            noise_time = noise_in_time(date_time.time(), percentage_noise_width)

            combine_date_time = datetime.datetime.combine(noise_date, noise_time).strftime("%Y-%m-%d %H:%M:%S")

            return combine_date_time
    except ValueError:
        pass

    try:
        if value in chain(*dict_alternatives.values()):
            #For categorial units with alternatives
            key_name_noise =  [key for key, list_alt in dict_alternatives.items() \
                                if value in list_alt][0]

            #Remove the current value from list of alternatives
            dict_alt_without_value = dict_alt[key_name_noise].copy()
            dict_alt_without_value.remove(value)

            noise_value = random.sample(dict_alt_without_value, k = 1)[0]

            return noise_value
    except AttributeError:
        pass
  
    return None

def noise_in_time(value, percentage_noise_width):
    time_in_seconds = int(datetime.timedelta(hours=value.hour, minutes=value.minute,
                                             seconds=value.second).total_seconds())
    noise_value = round(np.random.normal(time_in_seconds, percentage_noise_width * time_in_seconds))

    noise_value_hour = noise_value // 3600

    if noise_value_hour < 0:
        days = abs(noise_value_hour // 24)
        noise_value_hour = noise_value_hour + (days * 24)

    elif noise_value_hour > 23:
        days = noise_value_hour // 24
        noise_value_hour = noise_value_hour - (days * 24)

    noise_value_time = datetime.time(noise_value_hour, (noise_value % 3600) // 60, noise_value % 60)

    return noise_value_time