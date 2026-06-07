import streamlit as st
import sqlite3
import pandas as pd
import requests

st.set_page_config(page_title="Banka Yönetim Sistemi", layout="wide")
st.title("🏦 Banka Operasyonel Yönetim Paneli")

# İnternetteki veritabanını çekme taktiği
db_url = "https://raw.githubusercontent.com/gkybh/banking-database-project/main/banka_operasyonel.db"

@st.cache_resource
def download_db():
    r = requests.get(db_url)
    with open("banka.db", "wb") as f:
        f.write(r.content)

try:
    download_db()
    conn = sqlite3.connect('banka.db')
    
    st.subheader("📊 Aktif Hesaplar Listesi")
    st.write("Veritabanından canlı olarak çekilen 'v_active_accounts' verileri:")
    
    df = pd.read_sql_query("SELECT * FROM v_active_accounts", conn)
    st.dataframe(df, use_container_width=True)
    
    conn.close()
except Exception as e:
    st.error(f"Veritabanı yüklenirken bir hata oluştu: {e}")
    st.info("Lütfen GitHub'daki veritabanı linkinizi kontrol edin.")
