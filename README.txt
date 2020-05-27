********************************************* INSTALLATION AND USAGE **************************************************
***********************************************************************************************************************


-> Prgramming Language Required : Python 3.6
	-> Python Dependencies Required : 
		1) pandas - 1.0.3 - For handling datasets
		2) mysql - 1.4.6 - Python MySQL Connector 
		3) matplotlib - 3.2.1 - For Plots/visualizations

-> Database Tools : 
	-> MySQL Server 8.0
	-> MySQL WorkBench 8.0 (optional for ease of importing and exporting)

-> Visualization Tools : 
	-> Tableau 2019


USAGE :

-> Fire up the MySQL Server and set up the database and user credentials. 
-> Run SQLConnector.py. This will set up the SQL connection, create the schema and store the data in the tables.
-> Run the files specified below for further exploration.


File descriptions 

SQL Connector.py :  contains code for Python-MySQL connection mechanism.
Classification.py : Contains SVM classification code and  generates confusion matrix.
preprocessor.py : Contains data preprocessing functions such as stemming, cleaning data, etc.
Dataprocessor.py : Merges the datasets from two separate sources, converts them into a common format and stores them in the SQL database.
Clustering.py : Contains code for birch clustering and its analysis.


CONTRIBUTIONS : 

Amritha : 
-> Presentation
-> Data management component (Python/MySQL)
-> Report.

Satya : 
-> SVM classification (Python)
-> Birch clustering (Python)
-> Report

Vaibhav : 
-> Visualizations (Tableau/Python)
-> Data preprocessing
-> Report 

