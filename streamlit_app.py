#1 Import Library
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import plotly.graph_objects as go

# Koneksi ke Google Sheets
url = "https://docs.google.com/spreadsheets/d/1W9WYq245Q7g4VYn0BWt7x5DcMnhba3-rugeMu2TPM60/edit?gid=0#gid=0"
conn = st.connection("gsheets", type=GSheetsConnection)
data = conn.read(spreadsheet=url, usecols=[0, 1, 2, 3], ttl=0)

# 3 Pre-Processing
if data is not None and not data.empty:
    data.columns = ["Date", "Time", "Intensity", "Index"]
    data["Waktu"] = pd.to_datetime(data["Date"] + " " + data["Time"])
    data = data.sort_values(by="Waktu")
    data_asli = data.copy()
    data.set_index("Waktu", inplace=True)
    last_index = data['Index'].iloc[-1]
    last_time = data.index[-1]
    data = data[['Index']].copy()
    data = data.between_time('06:00', '18:05')
    date_range = pd.date_range(start=data.index.min(), end=data.index.max(), freq='2min')
    data = data.reindex(date_range)
    data['Index'].interpolate(method='linear', inplace=True)

#4 Normalisasi Data
scaler = MinMaxScaler(feature_range=(0, 1))
data ['Index_scaled'] = scaler.fit_transform(data[['Index']])

#5 Inisialisasi Timestep
def prepare_data(series, n_steps):
    X, y = [], []
    for i in range(len(series)-n_steps):
        X.append(series[i:i+n_steps])
        y.append(series[i+n_steps])
    return np.array(X), np.array(y)
n_steps = 7
X, y = prepare_data(data['Index_scaled'].values, n_steps)

#6 Split Data
split = int(len(X) * 0.8)
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]
X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

#7 Bangun LSTM
model = Sequential([
    LSTM(50, activation='relu', input_shape=(n_steps, 1), return_sequences=True),
    Dropout(0.2),
    LSTM(50, activation='relu'),
    Dense(1)
])

#8 Pembuatan Model dan Kompilasi Model
model.compile(optimizer='adam', loss='mean_squared_error')

#9 Pelatihan Model
history=model.fit(X_train, y_train, epochs=10, batch_size=8, validation_data=(X_test, y_test), verbose=1)

#10 Prediksi Model
train_predicted = model.predict(X_train)
test_predicted = model.predict(X_test)

#11 Denormalisasi
train_predicted_dnm = scaler.inverse_transform(train_predicted)
test_predicted_dnm = scaler.inverse_transform(test_predicted)
y_train_dnm = scaler.inverse_transform(y_train.reshape(-1, 1))
y_test_dnm = scaler.inverse_transform(y_test.reshape(-1, 1))

#12 Prediksi Masa Depan
future_steps = 150  # Tentukan jumlah langkah ke depan yang ingin diprediksi
future_input = X_test[-1].reshape(1, n_steps, 1)
future_predictions = []
future_timestamps = [last_time + pd.Timedelta(minutes=2 * (i + 1)) for i in range(future_steps)]

for _ in range(future_steps):
    future_pred = model.predict(future_input, verbose=0)
    future_predictions.append(future_pred[0, 0])
    future_input = np.roll(future_input, -1, axis=1)
    future_input[0, -1, 0] = future_pred[0, 0]

# Denormalisasi hasil prediksi masa depan
future_predictions_dnm = np.round (scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1))).astype(int)

# Tampilkan hasil prediksi masa depan dengan waktu
future_results = pd.DataFrame({'Datetime': future_timestamps, 'Predicted_Index': future_predictions_dnm.flatten()})

# Mulai dari 1 jam setelah last_time
start_time = last_time + pd.Timedelta(hours=1)

# Tentukan 5 titik waktu (setiap 1 jam)
target_times = [start_time + pd.Timedelta(hours=i) for i in range(5)]

# Cari data prediksi yang paling dekat dengan target waktu
selected_rows = []
for target_time in target_times:
    closest_index = (future_results['Datetime'] - target_time).abs().idxmin()
    selected_rows.append(future_results.loc[closest_index])

# Buat DataFrame hasilnya
filtered_results_1hour = pd.DataFrame(selected_rows)



#st.dataframe(filtered_results_1hour)

# Fungsi untuk menentukan kategori UV
def get_uv_category(uv_level):
    if uv_level < 3:
        return "🟢", "Low", "#00ff00"
    elif uv_level < 6:
        return "🟡", "Moderate", "#ffe600"
    elif uv_level < 8:
        return "🟠", "High", "#ff8c00"
    elif uv_level < 11:
        return "🔴", "Very High", "#ff0000"
    else:
        return "🟣", "Extreme", "#9900cc"

# Streamlit UI
st.title("UV Index Forecast")

# Tampilkan hasil prediksi dalam format horizontal
cols = st.columns(5)

for i, (index, row) in enumerate(filtered_results_1hour.iterrows()):
    icon, desc, bg_color = get_uv_category(row["Predicted_Index"])
    with cols[i]:
        st.markdown(
            f"""
            <div style="background-color:{bg_color}; padding:10px; border-radius:10px; text-align:center;">
                <h3>{icon} {desc}</h3>
                <p><strong>Time:</strong> {row['Datetime'].strftime('%H:%M')}</p>
                <p><strong>UV Index:</strong> {row['Predicted_Index']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
