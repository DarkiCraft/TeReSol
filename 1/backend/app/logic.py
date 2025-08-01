from pathlib import Path
import pandas as pd
from typing import Dict
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from datetime import timedelta
# import tensorflow as tf
# from tensorflow import keras
# from tensorflow import layers
# from sklearn.preprocessing import MinMaxScaler

df_files_list : Dict[str, pd.DataFrame] = {}

def df_meta_init(df: pd.DataFrame) -> pd.DataFrame:
    df = df[["Symbol",
             "Security Name",
             "ETF",
             "Listing Exchange",
             "Market Category",
             "Round Lot Size",
             "Lot Complexity Score",
             "Execution Time Estimate (ms)",
             "Synthetic Friction Index"]
            ].copy()
    df["Market Category"] = df["Market Category"].fillna("Missing")

    df.set_index("Symbol", inplace=True)

    return df

def df_file_init(df: pd.DataFrame) -> pd.DataFrame:
    df.dropna(inplace=True)
    df["Date"] = pd.to_datetime(df["Date"])

    df.set_index("Date", inplace=True)

    return df

df_meta = df_meta_init(pd.read_csv("app/.data/symbols_valid_meta.csv", na_values=[" "]))

def get_meta_info():
    global df_meta
    return df_meta

def get_file_data(symbol: str):
    symbol = symbol.upper()
    path = Path(f"app/.data/stocks/{symbol}.csv")

    if not path.exists():
        raise FileNotFoundError(f"File does not exist: {path}")

    df = pd.read_csv(path, na_values=[" "])
    df_files_list[symbol] = df_file_init(df)
    return df_files_list[symbol]

#to calculate daily return

def get_calculation_data(df: pd.DataFrame) -> dict:
    df = df.copy()
    df['Daily return'] = df["Close"].pct_change()

    avg_return = df["Daily return"].mean()
    volatility = df["Daily return"].std()

    if volatility == 0 or pd.isna(volatility):
        sharpe = float('nan')
    else:
        sharpe = avg_return / volatility

    var_95 = avg_return - 1.65 * volatility

    return {
        "Average Daily Return": avg_return,
        "Volatility": volatility,
        "Sharpe Ratio": sharpe,
        "Value At Risk 95%": var_95
    }
# basic future prediction

# def train_and_predict(df: pd.DataFrame) -> dict:
#     # try:
#         prices = df['close'].values

#         if len(prices)<100:
#             return{"error":"not enough data"}
        
#         x=[]
#         y=[]
        
#         for i in range(5,len(prices)):
#                 x.append(prices[i-5:i])
#                 y.append(prices[i])

#         x=np.array(x)
#         y=np.array(y)

#         scaler_x= MinMaxScaler()
#         scaler_y= MinMaxScaler()

#         x_scaled=scaler_x.fit_transform(x)
#         y_scaled=scaler_y.fit_transform(y.reshape(-1,1)).flatten() 

#         split = int(0.8*len(x_scaled))
#         X_train = x_scaled[:split]      
#         X_test = x_scaled[split:]       
#         y_train = y_scaled[:split]      
#         y_test = y_scaled[split:] 
    