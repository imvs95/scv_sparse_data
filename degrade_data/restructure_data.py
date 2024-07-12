import pandas as pd

def read_and_shape_data(file_name):
    """This function reads and reshapes the Excel file from the Simio simulation model. It reshapes the DateTime
    retrieved from Simio and restructures the columns.
    
    Parameters:
        file_name (str): Name of excel input file of type ".xlsx".
    
    Returns:
        observed_data: Dataframe from reshaped excel input file."""

    #observed_data = pd.read_excel("data/"+file_name+".xlsx").dropna(axis=0, how = "all")
    observed_data = pd.read_excel(file_name+".xlsx").dropna(axis=0, how = "all")

    observed_data['Date'] = [d.date().strftime("%Y-%m-%d") for d in observed_data["DateTime"]]
    observed_data['Time'] = [d.time() for d in observed_data["DateTime"]]

    observed_data = observed_data.astype({"NumChainPosition":"int64"})
    observed_data = observed_data.drop(columns=["DateTime", "ChainPosition", "Location"])

    #Reshape dataframe
    column_name = observed_data.columns.tolist()
    reshape_cols = column_name[-2:] + column_name[:-2]
    observed_data = observed_data[reshape_cols]

    del column_name, reshape_cols

    return observed_data

def create_dict_alternatives(dataframe, column_names, add_alt=None):
    """This function creates a dictionary for alternatives of categorial
    units given column names. This function automatically generates the alternatives based
    on the unique values of the column in a dataframe. When more alternatives occur for a specific
    column, this can be assigned via "add_alt". 
    
    Parameters:
        dataframe                   : Pandas DataFrame. 
        column_names (list)         : Name of columns which require alternatives.
        add_alt(dict)               : Additional alternatives with column name as key and a list of alternatives as value
    
    Returns:
        dict_alternatives           : Dictonairy with column name as key and a list of alternatives as value.
"""
    dict_alternatives = {}

    for name in column_names:
        list_alternatives = list(dataframe[name].dropna().unique())

        if str(name) in add_alt.keys():
            list_alternatives.append(add_alt[name])

        dict_alternatives[name] = list_alternatives
        continue 

    return dict_alternatives

def combine_lat_lon(dataframe):
    """This function combines the Latitude and Longitude column into one column.
    
    Parameters:
        dataframe       : Dataframe with Latitude and Longitude as individual column 
                          as type float.
                         
    Returns:
        new_dataframe   : Dataframe with Latitude and Longitude in one column 
                          as type tuple. """

    dataframe["Lat,Lon"] = list(zip(dataframe.Latitude, dataframe.Longitude))
    new_dataframe = dataframe.drop(columns=["Latitude", "Longitude"])

    return new_dataframe
