import pandas as pd

# This is set in the main.py
# retrieving all the codes and names of KOSPI and KOSDAQ
# Ticker_Dict = {"005930": {"종목명": "삼성전자"},
#                   "373220": {"종목명": "LG에너지솔루션"},
#                   ...}
Ticker_Dict = {}

# This is set in the tr_data_handler.py
# sotck basic info (Dataframe) which will be set by TR request
Stock_Info = None


# This is set in the tr_data_handler.py
My_Stock_Df = None
