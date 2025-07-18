import streamlit as st
import pandas as pd
import requests
import time
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=5000, key="refresh")
st.set_page_config(page_title="Дашборд транзакций", layout="wide")
st.title("📊 Дашборд транзакций")

api_url = st.text_input("Введите URL API", "http://localhost:8000/transactions")
refresh_rate = st.slider("⏱ Интервал обновления (сек)", 5, 60, 15)

# Контейнер для всей страницы
placeholder = st.empty()

def render_dashboard():
    try:
        r = requests.get(api_url)
        r.raise_for_status()
        data = pd.DataFrame(r.json())

        if data.empty:
            st.warning("Нет транзакций.")
        else:
            data["timestamp"] = pd.to_datetime(data["timestamp"])
            data = data.sort_values("timestamp", ascending=False)

            st.subheader("📋 Таблица")
            with st.expander("Фильтры", expanded=True):
                ip_filter = st.multiselect("IP", data["ip"].dropna().unique())
                currency_filter = st.multiselect("Валюта", data["currency"].unique())
                date_filter = st.date_input("Дата", [])

                if ip_filter:
                    data = data[data["ip"].isin(ip_filter)]
                if currency_filter:
                    data = data[data["currency"].isin(currency_filter)]
                if date_filter and len(date_filter) == 2:
                    data = data[
                        (data["timestamp"].dt.date >= date_filter[0]) &
                        (data["timestamp"].dt.date <= date_filter[1])
                    ]

            st.dataframe(data, use_container_width=True)

            st.subheader("🔢 Цифры")
            a, b, c = st.columns(3)
            a.metric("💰 Общая сумма", f"{data['amount'].sum():,.2f}")
            b.metric("📦 Кол-во транзакций", len(data))
            c.metric("📊 Средняя сумма", f"{data['amount'].mean():,.2f}")

            st.subheader("💱 Валюта")
            currency_stats = data.groupby("currency")["amount"].sum().reset_index()
            st.bar_chart(currency_stats.set_index("currency"))

            # st.subheader("🕒 По времени")
            # time_stats = data.groupby(data["timestamp"].dt.date)["amount"].sum()
            # st.line_chart(time_stats)


            if "is_suspicious" in data.columns:
                st.subheader("🚨 Подозрительные транзакции")

                suspicious_data = data[data["is_suspicious"] == True]

                if suspicious_data.empty:
                    st.info("Подозрительных транзакций не найдено.")
                else:
                    st.dataframe(suspicious_data, use_container_width=True)

                    # Анализ причин
                    st.subheader("📌 Причины тревоги")
                    reasons = suspicious_data.explode("alerts")["alerts"].value_counts()
                    st.bar_chart(reasons)

                    # Риск
                    st.subheader("📉 Распределение по уровню риска")
                    st.bar_chart(suspicious_data["risk_score"].value_counts().sort_index())

                    with st.expander("📖 Описание правил"):
                        st.markdown("""
- `HIGH_AMOUNT`: Сумма превышает допустимый лимит.
- `CRYPTO_CURRENCY`: Криптовалюта, сумма выше $2000.
- `NIGHT_OPERATION`: Транзакция до 6 утра.
- `MICROTRANSACTIONS_FLOOD`: Много микротранзакций.
- `STRUCTURING`: Сумма близка к пороговой.
- `REPEATED_TRANSACTIONS`: Повторяющиеся операции за короткое время.
- `OFFSHORE_OPERATION`: IP из офшорных диапазонов.
                        """)



    except Exception as e:
        st.error(f"❌ Ошибка при загрузке данных: {e}")


while True:
    with placeholder.container():
        render_dashboard()
    time.sleep(refresh_rate)
    st.rerun()
