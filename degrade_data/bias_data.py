import random
import numpy as np
import pandas as pd

from degrade_data.restructure_data import read_and_shape_data, combine_lat_lon

def sample_bias(dataframe, bias_percentage):
    """This functions draws an user-defined biased sample from the dataset and combines this with the normal dataset.
    The distribution used for this biased sample set is a LogNormal distribution."""

    lognormal = np.random.lognormal(size=len(dataframe))
    rows_to_sample = round(len(dataframe)*bias_percentage)
    sample = dataframe.sample(rows_to_sample, weights=lognormal, replace=True)

    replace = dataframe.sample(sample.shape[0])
    df = dataframe.copy()
    df.loc[replace.index] = sample.values
    df = df.reset_index(drop=True)
    return df



def assign_bias(dataframe, bias_percentage, highest_count, **kwargs):
    """ This function assigns an user-defined percentage of bias to a dataframe. The percentage bias in each
     column is calculated by the bias percentage divided by the number of data fields. When the highest
     count is True, the attribute with the highest count in a column represents an user-defined percentage of values
     in the dataframe. When highest count is False, the attribute that represents bias is randomly chosen by
     alternatives. Bias is incorporated by changing random value to convert to the bias attribute.

    Parameters:
        dataframe       : Dataframe
        bias_percentage : Percentage of bias
        highest_count   : Determine whether the attribute with the highest count
                          represent the bias or a randomly chosen attribute. Default is True.
        **kwargs        :

    Returns:
        bias_df      : Dataframe with bias given the column and percentage. """

    bias_percentage_column = bias_percentage/len(dataframe.columns)
    for column_name in dataframe.columns:

        dict_count = {value: dataframe[column_name].value_counts()[value] for value in \
                      dataframe[column_name].value_counts().index.tolist()}

        if highest_count:
            attribute_bias = max(dict_count, key=dict_count.get)

        else:
            attribute_bias = random.sample(dict_count.keys(), k=1)[0]

        total_rows_bias = round(int(len(dataframe)) * bias_percentage_column)
        rows_to_change = total_rows_bias - dict_count[attribute_bias]
        n = -2
        while rows_to_change < 0:
            try:
                attribute_bias = sorted(dict_count.items(), key=(lambda i: i[1]))[n][0]
                rows_to_change = total_rows_bias - dict_count[attribute_bias]
                n -= 1
            except IndexError:
                rows_to_change = 0

        # Sample the index of rows to remove
        index_to_choose = dataframe.index[dataframe[column_name] != attribute_bias].tolist()
        sampling = random.sample(index_to_choose, k=rows_to_change)

        for i in sampling:
            dataframe[column_name][i] = attribute_bias

        # print("Added bias to percentage {0:.3f} of the {1} values on {2} "
        #       "(highest count {3})".format(bias_percentage_column, column_name, attribute_bias, highest_count))

    return dataframe

def assign_bias_change_one_column(dataframe, bias_percentage, highest_count, **kwargs):
    """ This function assigns an user-defined percentage of bias to a column. When the highest
     count is True, the attribute with the highest count in a column represents an user-defined percentage of values
     in the dataframe. When highest count is False, the attribute that represents bias is randomly chosen by
     alternatives. Bias is incorporated by changing random value to convert to the bias attribute in one column. The
     column is randomly assigned when the user did not define it.

    Parameters:
        dataframe       : Dataframe
        column_name     : Name of the column on which bias applies.
        bias_percentage : Percentage of bias
        highest_count   : Determine whether the attribute with the highest count
                          represent the bias or a randomly chosen attribute. Default is True.
        **kwargs        :

    Returns:
        bias_df      : Dataframe with bias given the column and percentage. """

    column_name = random.sample(set(dataframe.columns), k=1)[0]
    if "column_name" in kwargs:
        column_name = kwargs["column_name"]

    dict_count = {value: dataframe[column_name].value_counts()[value] for value in \
                  dataframe[column_name].value_counts().index.tolist()}

    if highest_count:
        attribute_bias = max(dict_count, key=dict_count.get)

    else:
        attribute_bias = random.sample(dict_count.keys(), k=1)[0]

    total_rows_bias = round(int(len(dataframe)) * bias_percentage)
    rows_to_change = total_rows_bias - dict_count[attribute_bias]
    n = -2
    while rows_to_change < 0:
        try:
            attribute_bias = sorted(dict_count.items(), key=(lambda i: i[1]))[n][0]
            rows_to_change = total_rows_bias - dict_count[attribute_bias]
            n -= 1
        except IndexError:
            rows_to_change = 0

    # Sample the index of rows to remove
    index_to_choose = dataframe.index[dataframe[column_name] != attribute_bias].tolist()
    sampling = random.sample(index_to_choose, k=rows_to_change)

    for i in sampling:
        dataframe[column_name][i] = attribute_bias

    print("Added bias to percentage {0:.2f} of the {1} values on {2} "
          "(highest count {3})".format(bias_percentage, column_name, attribute_bias, highest_count))

    return dataframe


def assign_bias_remove(dataframe, bias_percentage, highest_count, **kwargs):
    """ This function assigns an user-defined percentage of bias to an user-defined column.  When the highest
     count is True, the attribute with the highest count in a column represents an user-defined percentage of values
     in the dataframe. When highest count is False, the attribute that represents bias is randomly chosen by
     alternatives. Bias is incorporated by reducing the length of the dataframe; rows are removed
     and not added to ensure a percentage of bias. Rows are randomly removed.

    Parameters:
        dataframe       : Dataframe
        column_name     : Name of the column on which bias applies.
        bias_percentage : Percentage of bias
        highest_count   : Determine whether the attribute with the highest count
                          represent the bias or a randomly chosen attribute. Default is True.
        **kwargs        :

    Returns:
        bias_df      : Dataframe with bias given the column and percentage. """

    column_name = random.sample(set(dataframe.columns), k=1)[0]
    if "column_name" in kwargs:
        column_name = kwargs["column_name"]

    dict_count = {value: dataframe[column_name].value_counts()[value] for value in \
                  dataframe[column_name].value_counts().index.tolist()}

    if highest_count:
        attribute_bias = max(dict_count, key=dict_count.get)

    else:
        attribute_bias = random.sample(dict_count.keys(), k=1)[0]

    rows_to_remove = int(len(dataframe) - round(dict_count[attribute_bias] / bias_percentage))
    n = -2
    while rows_to_remove < 0:
        try:
            attribute_bias = sorted(dict_count.items(), key=(lambda i: i[1]))[n][0]
            rows_to_remove = int(len(dataframe) - round(dict_count[attribute_bias] / bias_percentage))
            n -= 1
        except IndexError:
            rows_to_remove = 0

    # Sample the index of rows to remove
    index_to_choose = dataframe.index[dataframe[column_name] != attribute_bias].tolist()
    sampling = random.sample(index_to_choose, k=rows_to_remove)

    bias_df = dataframe.drop(dataframe.index[sampling], axis=0)

    print("Added bias to percentage {0:.2f} of the {1} values on {2} "
          "(highest count {3})".format(bias_percentage, column_name, attribute_bias, highest_count))

    return bias_df

