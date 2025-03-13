import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

st.markdown("""
    <style>
    .header {
        background-color: #D6D6F5; padding: 10px; text-align: center; border-radius: 7px;
    }
    .header img {
        width: 60px;
    }
    </style>
    <div class="header">
        <img src="https://upload.wikimedia.org/wikipedia/id/2/2d/Undip.png" alt="Logo">
    </div>
    """,
    unsafe_allow_html=True)

# Navigasi Sidebar
st.sidebar.title("Navigasi")
menu = st.sidebar.radio("Pilih Menu", ["Beranda", "Indeks UV", "Panduan Perlindungan", "Data Historis"])

# Tampilan Beranda
if menu == "Beranda":
    st.subheader("Selamat Datang di Sistem Pemantauan Indeks UV")
    st.write("Gunakan navigasi di sebelah kiri untuk melihat data dan panduan perlindungan.")

elif menu == "Indeks UV":
    st.subheader("🌞 Kondisi UV Sekarang")
    last_index = 5  # Contoh nilai indeks UV
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=last_index, gauge={
            'axis': {'range': [0, 11]},
            'bar': {'color': "#3098ff"},
            'steps': [
                {'range': [0, 3], 'color': "#00ff00"},
                {'range': [3, 6], 'color': "#ffff00"},
                {'range': [6, 8], 'color': "#ff6600"},
                {'range': [8, 10], 'color': "#ff0000"},
                {'range': [10, 11], 'color': "#9900cc"},
            ]
        }
    ))
    fig.update_layout(margin=dict(t=30, b=30, l=30, r=30))
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div style="text-align: center; font-size: medium; margin-top: 10px; margin-bottom: 40px;">
        <p><b>Pukul:</b> 13:00 WIB</p>
    </div>
    """.format(pd.Timestamp.now().strftime('%H:%M')), unsafe_allow_html=True)
    
    st.subheader("⏳ Prediksi Indeks UV")
    data = {
        "Datetime": ["14:00", "15:00", "16:00", "17:00", "18:00"],
        "Predicted_Index": [7, 5, 4, 0, 0]
    }
    df = pd.DataFrame(data)

    # Fungsi kategori UV
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

    cols = st.columns(len(df))
    for i, row in df.iterrows():
        icon, desc, bg_color = get_uv_category(row["Predicted_Index"])
        with cols[i]:
            st.markdown(f"""
            <div style="text-align:center; padding:12px; border-radius:10px;
                        background-color:{bg_color}; box-shadow: 3px 3px 8px rgba(0,0,0,0.2);">
                <h3 style="color:white; margin: 0;">{row['Datetime']}</h3>
                <h2 style="color:white; margin: 5px 0;">{icon} {row['Predicted_Index']}</h2>
                <p style="color:white; font-size:14px;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

elif menu == "Panduan Perlindungan":
    st.subheader("🌞 Panduan Perlindungan terhadap UV")
    st.write("Informasi mengenai perlindungan dari paparan sinar UV.")

elif menu == "Data Historis":
    st.subheader("📊 Data Historis Indeks UV")
    st.write("Menampilkan data historis indeks UV yang telah dikumpulkan.")

# Custom Footer
st.markdown("""
    <style>
    .footer {
        position: fixed; bottom: 0; right: 70px; font-size: 12px; text-align: left; margin: 0; padding: 5px 10px;
    }
    </style>
    <div class="footer">
        <p>Universitas Diponegoro<br>Fakultas Sains dan Matematika<br>Departemen Fisika</p>
        <p>Nastangini<br>20440102130112</p>
    </div>
    """, unsafe_allow_html=True)
