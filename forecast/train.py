import pandas as pd
from sqlalchemy import text
from prophet import Prophet
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error, mean_absolute_error
from database.connection import engine

def load_historical_data(gram_variant=1.0):
    query = text("""
        SELECT tanggal AS ds, harga_antam AS y 
        FROM historis_harga_antam 
        WHERE gram = :gram
        ORDER BY tanggal ASC
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"gram": gram_variant})
    return df

def train_and_evaluate(gram_variant=1.0):
    df = load_historical_data(gram_variant=gram_variant)
    
    if len(df) < 20:
        print(f"Data untuk {gram_variant} gram terlalu sedikit ({len(df)} records) untuk evaluasi.")
        return None

    train_size = int(len(df) * 0.8)
    train_df = df.iloc[:train_size]
    test_df = df.iloc[train_size:]

    model = Prophet(
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=False 
    )
    model.fit(train_df)

    future_test = test_df[['ds']].copy()
    forecast_test = model.predict(future_test)

    y_true = test_df['y'].values
    y_pred = forecast_test['yhat'].values

    try:
        rmse = mean_squared_error(y_true, y_pred, squared=False)
    except TypeError:
        from sklearn.metrics import root_mean_squared_error
        rmse = root_mean_squared_error(y_true, y_pred)
    
    mae = mean_absolute_error(y_true, y_pred) 
    mape = mean_absolute_percentage_error(y_true, y_pred) * 100

    final_model = Prophet(daily_seasonality=False, weekly_seasonality=True, yearly_seasonality=False)
    final_model.fit(df)
    
    return final_model, {"mae": int(mae), "rmse": int(rmse), "mape": round(mape, 2)}