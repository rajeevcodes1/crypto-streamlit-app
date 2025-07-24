import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

st.set_page_config(page_title="Crypto Tracker", layout="wide")

st.title("💰 Real-Time Cryptocurrency Tracker")

@st.cache_data(ttl=300)
def fetch_data(vs_currency="usd", per_page=50):
    url = f"https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": 1,
        "sparkline": False
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        st.error("Failed to fetch data from CoinGecko.")
        return None
    return pd.DataFrame(response.json())

data = fetch_data()
if data is not None:
    st.dataframe(data[["name", "symbol", "current_price", "market_cap", "price_change_percentage_24h"]],
                 use_container_width=True)

    st.subheader("📈 Select a Coin to View Price History")
    coin_name = st.selectbox("Choose a Coin", data["id"].tolist())

    @st.cache_data(ttl=600)
    def get_price_history(coin_id):
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {"vs_currency": "usd", "days": "30"}
        res = requests.get(url, params=params)
        if res.status_code != 200:
            return None
        prices = res.json()["prices"]
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df

    chart_data = get_price_history(coin_name)
    if chart_data is not None:
        st.line_chart(chart_data.rename(columns={"timestamp": "index"}).set_index("index")["price"])
    else:
        st.error("Could not fetch price history.")
else:
    st.error("Could not load cryptocurrency data.")
