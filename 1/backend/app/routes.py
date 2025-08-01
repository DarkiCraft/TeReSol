from io import StringIO
from datetime import datetime
from functools import wraps
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from app.logic import get_meta_info, get_calculation_data, get_file_data, df_file_init
import pandas as pd
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter()

def safe_symbol_access(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        symbol = kwargs.get("symbol", "").upper()
        kwargs["symbol"] = symbol
        try:
            return func(*args, **kwargs)
        except KeyError:
            return JSONResponse(status_code=404, content={"error": f"Symbol '{symbol}' not found"})
        except FileNotFoundError:
            return JSONResponse(status_code=404, content={"error": f"Data file for symbol '{symbol}' not found"})
    return wrapper

@router.get("/favicon.ico")
def get_favicon():
    return RedirectResponse(url="/static/favicon.ico")

@router.get("/stocks")
def get_stocks():
    df = get_meta_info().copy()
    df["Symbol"] = df.index

    cols = df.columns.tolist()
    cols = ["Symbol"] + [col for col in cols if col != "Symbol"]    
    df = df[cols]

    return df.to_dict(orient="records")

@router.get("/stocks/unique")   
def get_stocks_unique():
    return {
        "unique_records": len(get_meta_info().to_dict(orient="records"))
    }

@router.get("/stocks/{symbol}")
@safe_symbol_access
def get_stocks_symbol(symbol: str):
    symbol = symbol.upper()

    df_meta = get_meta_info()
    return df_meta.loc[symbol].to_dict()
    
@router.get("/stocks/{symbol}/data")
@safe_symbol_access
def get_stocks_symbol_data(symbol: str, start: str = None, end: str = None):
    symbol = symbol.upper()

    df = get_file_data(symbol).copy()
    df["Date"] = df.index

    # Filter by date if provided
    if start:
        df = df[df.index >= pd.to_datetime(start)]
    if end:
        df = df[df.index <= pd.to_datetime(end)]

    # Reorder columns
    cols = df.columns.tolist()
    cols = ["Date"] + [col for col in cols if col != "Date"]    
    df = df[cols]

    return df.to_dict(orient="records")

    
@router.get("/stocks/{symbol}/data/{date}")
@safe_symbol_access
def get_stocks_symbol_data_date(symbol: str, date: datetime):
    symbol = symbol.upper()
    
    df_file = get_file_data(symbol)

    try:
        return df_file.loc[date].to_dict()
    except KeyError:
        return JSONResponse(status_code=404, content={"error": f"Date '{date.date()}' not found for symbol '{symbol}'"})

#volitility shapre ratio

@router.get("/stocks/{symbol}/analytics")
@safe_symbol_access
def get_stocks_symbol_analytics(symbol: str):
    symbol = symbol.upper()

    return get_calculation_data(get_file_data(symbol))

@router.get("/distribution/etf")
def get_distribution_etf():
    df = get_meta_info()
    return df["ETF"].value_counts().to_dict()
# market categrories Q N
@router.get("/distribution/exchanges")
def get_distribution_exchanges():
    df = get_meta_info()

    return df["Listing Exchange"].value_counts().to_dict()
# missing 

@router.get("/distribution/categories")
def get_distribution_categories():
    df = get_meta_info()
    return df["Market Category"].value_counts().to_dict()




@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        decoded = content.decode("utf-8")
        symbol = file.filename.removesuffix(".csv")
        df = pd.read_csv(StringIO(decoded))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read CSV: {str(e)}")

    columns = df.columns.to_list()
    required = ["Date", "Open" , "High", "Low", "Close", "Adj Close", "Volume"]

    df_meta = get_meta_info()

    if set(columns) == set(required) and symbol in df_meta.index:
        return {
            "metadata": df_meta.loc[symbol].to_dict(),
            "analytics": get_calculation_data(df_file_init(df.copy())),
            "data": df.to_dict(orient="records")
        }

    else:
        raise HTTPException(status_code=400, detail=f"Failed to read CSV: Invalid columns")

    # return: meta, analytics, data