import pandas as pd
from forecast.train import train_and_evaluate
from database.connection import engine

def get_all_gram_variants():
    query = "SELECT DISTINCT gram FROM historis_harga_antam ORDER BY gram ASC"
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    return df['gram'].tolist()

def generate_forecast_all_grams():
    gram_list = get_all_gram_variants()
    all_forecasts = []
    all_metrics = []

    for gram in gram_list:
        model, metrics = train_and_evaluate(gram_variant=gram)
        if not model:
            continue
            
        metrics['gram'] = gram
        all_metrics.append(metrics)

        future = model.make_future_dataframe(periods=7, freq='D')
        forecast = model.predict(future)
        hasil_ramalan = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(7).copy()
        hasil_ramalan['gram'] = gram
        all_forecasts.append(hasil_ramalan)

    if all_forecasts:
        df_final_forecast = pd.concat(all_forecasts, ignore_index=True)
        df_final_forecast['yhat'] = df_final_forecast['yhat'].astype(int)
        df_final_forecast['yhat_lower'] = df_final_forecast['yhat_lower'].astype(int)
        df_final_forecast['yhat_upper'] = df_final_forecast['yhat_upper'].astype(int)
        df_final_forecast = df_final_forecast.rename(columns={'ds': 'tanggal_prediksi', 'yhat': 'harga_prediksi'})

        with engine.connect() as conn:
            df_final_forecast.to_sql('prediksi_harga_antam', conn, if_exists='replace', index=False)
            
    if all_metrics:
        df_metrics = pd.DataFrame(all_metrics)
        with engine.connect() as conn:
            df_metrics.to_sql('detail_prediksi', conn, if_exists='replace', index=False)
            
        print("Semua data berhasil diperbarui di database.")
        
    return df_final_forecast

if __name__ == "__main__":
    generate_forecast_all_grams()