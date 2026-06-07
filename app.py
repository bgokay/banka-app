import streamlit as st
import sqlite3
import pandas as pd
import os

st.set_page_config(page_title="Banka Yönetim Sistemi", layout="wide")
st.title("🏦 Banka Operasyonel Yönetim Paneli")

st.sidebar.header("📁 Veritabanı Yükleme")
uploaded_file = st.sidebar.file_uploader("Lütfen banka_operasyonel.db dosyanızı buraya sürükleyin", type=["db", "sqlite", "sqlite3"])

if uploaded_file is not None:
    # Yüklenen dosyayı geçici olarak sisteme kaydet
    with open("temp_banka.db", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    conn = sqlite3.connect("temp_banka.db")
    
    # Sekmeler oluştur (Hocaya şov yapmak için)
    tab1, tab2, tab3 = st.tabs(["📊 Aktif Hesaplar", "📈 Şube Performansı", "👥 Müşteri Segmentasyonu"])
    
    with tab1:
        st.subheader("Aktif Hesaplar Listesi")
        try:
            df1 = pd.read_sql_query("SELECT * FROM v_active_accounts", conn)
            st.dataframe(df1, use_container_width=True)
        except Exception as e:
            st.warning("v_active_accounts görünümü bulunamadı. Lütfen DB Browser'da views.sql kodunu çalıştırdığınızdan emin olun.")

    with tab2:
        st.subheader("Şube Performans Analizi")
        try:
            df2 = pd.read_sql_query("SELECT * FROM v_branch_performance", conn)
            st.dataframe(df2, use_container_width=True)
        except Exception as e:
            st.warning("v_branch_performance görünümü bulunamadı.")
            
    with tab3:
        st.subheader("Müşteri İşlem Aktivite Segmentleri")
        try:
            # CTE içeren queries.sql'deki 8. sorguyu direkt buraya gömdük
            cte_query = """
            WITH customer_activity AS (
                SELECT
                    c.customer_id,
                    c.first_name || ' ' || c.last_name AS customer_name,
                    COUNT(t.transaction_id) AS transaction_count,
                    SUM(t.amount) AS total_volume_cents
                FROM customers c
                JOIN accounts a ON c.customer_id = a.customer_id
                JOIN transactions t ON a.account_id = t.account_id
                GROUP BY c.customer_id, c.first_name, c.last_name
            )
            SELECT
                customer_id,
                customer_name,
                transaction_count,
                PRINTF('%.2f', total_volume_cents / 100.0) AS total_volume_try,
                CASE
                    WHEN transaction_count >= 8 OR total_volume_cents >= 100000 THEN 'High Activity'
                    WHEN transaction_count >= 4 THEN 'Medium Activity'
                    ELSE 'Normal Activity'
                END AS activity_segment
            FROM customer_activity
            ORDER BY total_volume_cents DESC;
            """
            df3 = pd.read_sql_query(cte_query, conn)
            st.dataframe(df3, use_container_width=True)
        except Exception as e:
            st.error(f"Sorgu çalıştırılırken hata oluştu: {e}")
            
    conn.close()
else:
    st.info("💡 Sol taraftaki menüyü kullanarak 'banka_operasyonel.db' (veya sqlproject.db) veritabanı dosyanızı yüklediğinizde, uygulamanız canlı olarak çalışacaktır.")
