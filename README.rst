Calculate Supply Chain Visibility with Sparse Data
==========================================================================================================
The repository is used to generate the results of the paper: van Schilt, I. M., Kwakkel, J. H., Mense, J. P., & Verbraeck, A. (2024).
Dimensions of data sparseness and their effect on supply chain visibility. *Computers & Industrial Engineering, 191*, 110108. doi:`10.1016/j.cie.2024.110108 <https://doi.org/10.1016/j.cie.2024.110108>`_
It present the code on how to calculate supply chain visibility for a given supply chain network with sparse data.

This repository is also part of the Ph.D. thesis of  `Isabelle M. van Schilt <https://www.tudelft.nl/staff/i.m.vanschilt/?cHash=74e749835b2a89c6c76b804683ffbbcf>`_, Delft University of Technology. The version of the code used in the Ph.D. thesis is available at doi: `10.4121/d491bee7-c911-4099-a60f-075327ebea23.v1 <https://doi.org/10.4121/d491bee7-c911-4099-a60f-075327ebea23.v1>`_.

Content
=====================================================
The repository contains the following files:

* *data*: This folder contains the ground truth data. This data is generated using a stylized supply chain simulation model in `pydsol-model <https://pydsol-model.readthedocs.io/en/latest/index.html>`_.
* *degrade_data*: This folder contains the .py files to degrade the ground truth data to sparse data. The data is degraded by removing a percentage of the data on the dimensions of bias, noise, and missing values.
* *calculate_scv.py*: This python file calculates the supply chain visibility for a given supply chain network with sparse data.
* *Run_Visualize_SCV_Individual_Dimensions.ipynb*: This Jupyter notebook presents the calculation and the visualization of the supply chain visibility when degrading the individual dimensions.
* *Run_Visualize_SCV_Scenarios.ipynb*: This Jupyter notebook presents the calculation and the visualization of the supply chain visibility when degrading for scenarios (presented in the paper).
* *requirements.txt*: This file contains the required packages to run the code.
