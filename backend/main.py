from fastapi import FastAPI, Query
from etl_yfinance.db import get_db_connection
from backend.queries import get_filtered_dates, get_index_returns,get_index_performance_monthly
from fastapi import HTTPException


app = FastAPI()

@app.get("/dates")
def get_matching_dates(
    inflation_min: float, inflation_max: float,
    unemp_min: float, unemp_max: float,
    brent_min: float, brent_max: float,
    rate_min: float, rate_max: float,
    coffee_min: float, coffee_max: float
):
    conn = get_db_connection()
    dates = get_filtered_dates(conn, inflation_min, inflation_max, unemp_min, unemp_max, brent_min, brent_max, rate_min, rate_max, coffee_min, coffee_max)
    conn.close()
    return {"dates": dates}

@app.get("/returns")
def get_returns(start_date: str):
    conn = get_db_connection()
    data = get_index_returns(conn, start_date)
    conn.close()
    return {"returns": data}

@app.get("/monthly_returns")
def get_monthly_returns(start_date: str):
    conn = get_db_connection()
    try:
        data = get_index_performance_monthly(conn, start_date)
        return {"monthly_returns": data}
    except Exception as e:
        print(f"Error in /monthly_returns: {e}")  # Log the real error
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        conn.close()

