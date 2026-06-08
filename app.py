import streamlit as st
import sqlite3
import pandas as pd

# ==========================================
# SAYFA AYARLARI VE BAŞLIK
# ==========================================
st.set_page_config(page_title="Banka Yönetim Paneli", layout="wide")
st.title("🏦 Banka Operasyonel Yönetim Paneli")

st.markdown("""
**Proje Özeti:** Bu uygulama, banka veritabanındaki aktif hesapları, şube performanslarını ve müşteri işlem hacimlerini anlık olarak takip etmek için geliştirilmiştir. 
Arka planda SQLite veritabanı ve gelişmiş SQL sorguları (VIEW, CTE, JOIN, AGGREGATE) çalışmaktadır.
""")

st.divider()

# ==========================================
# VERİTABANI BAĞLANTISI VE VİTRİN
# (Dosyalar GitHub'da yan yana olduğu için direkt bağlanıyoruz)
# ==========================================
try:
    conn = sqlite3.connect('sqlproject.db')
    
    # Hocaya şov yapmak için 3 farklı sekme
    tab1, tab2, tab3 = st.tabs(["📊 Aktif Hesaplar (View)", "📈 Şube Performansı (Aggregate)", "👥 Müşteri Segmentasyonu (CTE & CASE)"])
    
    with tab1:
        st.subheader("Aktif Hesaplar Listesi")
        st.caption("Veriler 'customers', 'accounts' ve 'branches' tablolarının JOIN edilmesiyle oluşturulan sanal görünümden (VIEW) çekilmektedir.")
        try:
            # Önce view'dan çekmeyi dener
            df1 = pd.read_sql_query("SELECT * FROM v_active_accounts", conn)
            st.dataframe(df1, use_container_width=True)
        except:
            # Eğer view veritabanında yoksa, anında o karmaşık SQL'i kendi çalıştırır (Güvenlik ağı)
            fallback_query = """
            SELECT a.account_id, a.account_number, a.account_type, 
                   PRINTF('%.2f', a.balance / 100.0) AS balance_try, 
                   c.first_name || ' ' || c.last_name AS customer_name, 
                   b.branch_name
            FROM accounts a
            JOIN customers c ON a.customer_id = c.customer_id
            JOIN branches b ON a.branch_id = b.branch_id
            WHERE a.status = 'active';
            """
            df1 = pd.read_sql_query(fallback_query, conn)
            st.dataframe(df1, use_container_width=True)

    with tab2:
        st.subheader("Şube Performans Analizi")
        st.caption("LEFT JOIN ve COUNT/GROUP BY kullanılarak şubelerin işlem hacimleri listelenmektedir.")
        try:
            df2 = pd.read_sql_query("SELECT * FROM v_branch_performance", conn)
            st.dataframe(df2, use_container_width=True)
        except:
            fallback_query2 = """
            SELECT b.branch_id, b.branch_name, b.city, 
                   COUNT(DISTINCT a.account_id) AS total_accounts, 
                   COUNT(t.transaction_id) AS total_transactions
            FROM branches b
            LEFT JOIN accounts a ON b.branch_id = a.branch_id
            LEFT JOIN transactions t ON a.account_id = t.account_id
            GROUP BY b.branch_id, b.branch_name, b.city;
            """
            df2 = pd.read_sql_query(fallback_query2, conn)
            st.dataframe(df2, use_container_width=True)
            
    with tab3:
        st.subheader("Müşteri Aktivite Segmentasyonu")
        st.caption("İleri seviye SQL kullanılmıştır: Ortak Tablo İfadeleri (CTE - WITH) ve CASE WHEN mantığı ile anlık segmentasyon yapılmaktadır.")
        cte_query = """
        WITH customer_activity AS (
            SELECT c.customer_id, c.first_name || ' ' || c.last_name AS customer_name, 
                   COUNT(t.transaction_id) AS transaction_count, 
                   SUM(t.amount) AS total_volume_cents
            FROM customers c 
            JOIN accounts a ON c.customer_id = a.customer_id 
            JOIN transactions t ON a.account_id = t.account_id
            GROUP BY c.customer_id, c.first_name, c.last_name
        )
        SELECT customer_name, transaction_count, 
               PRINTF('%.2f', total_volume_cents / 100.0) AS total_volume_try,
               CASE
                   WHEN transaction_count >= 8 OR total_volume_cents >= 100000 THEN 'Yüksek Aktivite (High)'
                   WHEN transaction_count >= 4 THEN 'Orta Aktivite (Medium)'
                   ELSE 'Normal Aktivite (Normal)'
               END AS activity_segment
        FROM customer_activity 
        ORDER BY total_volume_cents DESC;
        """
        try:
            df3 = pd.read_sql_query(cte_query, conn)
            st.dataframe(df3, use_container_width=True)
        except Exception as e:
            st.error(f"Sorgu hatası (Veriler boş olabilir): {e}")

    conn.close()

except Exception as e:
    st.error(f"Veritabanına bağlanılamadı. Hata detayı: {e}")
