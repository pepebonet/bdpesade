# BDP Esade 
The objective of the following software is to predict the product demand of a retail company. We developed three simple models to work towards this problem and summarize below how to use them. 


# Contents
- [Installation](#Installation)
- [Usage](#Usage)      

# Installation
## Clone repository
First download the repository:

        git clone https://github.com/pepebonet/bdpesade.git

## Install dependencies
We highly recommend to use a virtual environment to run the scripts: 

`Create environment and install bdpesade:`

        conda create --name bdpesade python=3.8
        conda activate bdpesade
        pip install -r requirements.txt

# Usage
In order to use the developed software the following steps need to be followed. 

## Unify data into one file
First, the data which is contained in different folders --one for each year-- is downloaded. Once the data is available, it needs to be put as a unique dataframe to work with it easily. In order to do so, the following command is run (please ensure the folder containing the data is properly added): 

```
python libs/join_clean_data.py -fd folder/containg/data/ -o output_folder/
```

This command will generate a tsv file named TotalSales.tsv containig all the information in the folder named output_folder. 

## ETL Process

Next, in order to clean up and perform the ETL process, a different script is used, data_exploration.py. Using the previously generated file as input, together with an additional dictionary containing information of columns to delete and rename and a file to filter out some clients, the following command can be run: 

```
python libs/data_exploration.py -d output_folder/TotalSales.tsv -o output_folder/ -cc output_folder/limpieza_cat_clientes.csv -nd output_folder/dict_names_final_10thSep.pickle
```

This commnad generates a cleaned version of the data (final_cleaned_data.tsv) that can be used as input to carry out the forecasting of different products. 

## Product Forecasting

To predict product demand of the company one can use any of the models developed (ARIMA, Gradient Boosting Machines or LSTMs). To simplify the commands to make the predictions, the commands below will run for the default hyperparameters of the models and for a particular product (Mozzarela per pizza).  


`Option 1:` ARIMA model
```
python libs/model_demand.py -dt output_folder/final_cleaned_data.tsv -c after -m arima -tw 22 -o output_folder/
```

`Option 2:` Gradient Boosting Machines
```
python libs/model_demand.py -dt output_folder/final_cleaned_data.tsv -c after -m gbm -tw 22 -o output_folder/
```

`Option 3:` LSTMs
```
python libs/model_demand.py -dt output_folder/final_cleaned_data.tsv -c after -m lstm -tw 22 -o output_folder/
```

Hyperparameters and additional commands are not discussed here but can be found in the model_demand.py script and adjusted to render different information. Outputs from the running the commands above can be used to investigate and comapre the accuracy of the models and how they compare to how well the company does it.