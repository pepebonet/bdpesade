# BDP Valcoiberia 
Final project EMIBA.  


# Contents
- [Installation](#Installation)
- [Usage](#Usage)
- [Example data](#Example-data)         

# Installation
## Clone repository
First download the repository:

        git clone https://github.com/pepebonet/bdpesade.git

## Install dependencies
We highly recommend to use a virtual environment to run the scripts: 

`Create environment and install bdpesade:`

        conda create --name bdpesade python=3.8
        conda activate bdpesade
        pip install -e .

# Usage


        python libs/data_exploration.py -d data/TotalSales.tsv -o   tests_8th_Nov/ -cc data/albaranes_de_venta/limpieza_cat_clientes.csv -nd data/albaranes_de_venta/datos_limipios/dict_names_final_10thSep.pickle


# Example data