import streamlit as st
from PIL import Image
import pandas as pd
import base64
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import json

st.set_page_config(layout="wide")
image = Image.open('logo.jpg')
st.image(image, width=500)

st.title('Crypto Price App')
st.markdown("""
This app retrieves cryptocurrency prices for the top 100 cryptocurrencies from **CoinMarketCap**!
""")

expander_bar = st.expander("About")
expander_bar.markdown("""
* **Python libraries:** base64, pandas, streamlit, matplotlib, BeautifulSoup, requests, json
* **Data source:** [CoinMarketCap](https://coinmarketcap.com)
* **Credit:** Web scraper adapted from [this article](https://towardsdatascience.com/web-scraping-crypto-prices-with-python-41072ea5b5bf)
""")

col1 = st.sidebar
col2, col3 = st.columns((2,1))

col1.header('Input Options')
currency_price_unit = col1.selectbox('Select currency for price', ('USD', 'BTC', 'ETH'))

@st.cache_data
def load_data():
    url = 'https://coinmarketcap.com'
    cmc = requests.get(url)
    soup = BeautifulSoup(cmc.content, 'html.parser')
    try:
        data = soup.find('script', id='__NEXT_DATA__', type='application/json')
        coin_data = json.loads(data.contents[0])
        listings = coin_data['props']['initialState']['cryptocurrency']['listingLatest']['data']
    except Exception:
        st.error("Unable to retrieve data. CoinMarketCap's structure might have changed.")
        return pd.DataFrame()
    coin_name, coin_symbol, price, percent_change_1h, percent_change_24h, percent_change_7d, market_cap, volume_24h = [], [], [], [], [], [], [], []
    for i in listings:
        coin_name.append(i['slug'])
        coin_symbol.append(i['symbol'])
        price.append(i['quote'][currency_price_unit]['price'])
        percent_change_1h.append(i['quote'][currency_price_unit]['percent_change_1h'])
        percent_change_24h.append(i['quote'][currency_price_unit]['percent_change_24h'])
        percent_change_7d.append(i['quote'][currency_price_unit]['percent_change_7d'])
        market_cap.append(i['quote'][currency_price_unit]['market_cap'])
        volume_24h.append(i['quote'][currency_price_unit]['volume_24h'])
    df = pd.DataFrame({
        'coin_name': coin_name,
        'coin_symbol': coin_symbol,
        'price': price,
        'percent_change_1h': percent_change_1h,
        'percent_change_24h': percent_change_24h,
        'percent_change_7d': percent_change_7d,
        'market_cap': market_cap,
        'volume_24h': volume_24h
    })
    return df

df = load_data()
if df.empty:
    st.stop()

sorted_coin = sorted(df['coin_symbol'])
selected_coin = col1.multiselect('Cryptocurrency', sorted_coin, sorted_coin)
df_selected_coin = df[df['coin_symbol'].isin(selected_coin)]
num_coin = col1.slider('Display Top N Coins', 1, 100, 100)
df_coins = df_selected_coin[:num_coin]
percent_timeframe = col1.selectbox('Percent change time frame', ['7d','24h','1h'])
percent_dict = {"7d":'percent_change_7d', "24h":'percent_change_24h', "1h":'percent_change_1h'}
selected_percent_timeframe = percent_dict[percent_timeframe]
sort_values = col1.selectbox('Sort values?', ['Yes', 'No'])

col2.subheader('Price Data of Selected Cryptocurrency')
col2.write(f'Data Dimension: {df_coins.shape[0]} rows and {df_coins.shape[1]} columns.')
col2.dataframe(df_coins)

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="crypto.csv">Download CSV File</a>'

col2.markdown(filedownload(df_selected_coin), unsafe_allow_html=True)

col2.subheader('Table of % Price Change')
df_change = df_coins[['coin_symbol', 'percent_change_1h', 'percent_change_24h', 'percent_change_7d']]
df_change = df_change.set_index('coin_symbol')
df_change['positive_percent_change_1h'] = df_change['percent_change_1h'] > 0
df_change['positive_percent_change_24h'] = df_change['percent_change_24h'] > 0
df_change['positive_percent_change_7d'] = df_change['percent_change_7d'] > 0
col2.dataframe(df_change)

col3.subheader('Bar plot of % Price Change')
if percent_timeframe == '7d':
    if sort_values == 'Yes':
        df_change = df_change.sort_values(by='percent_change_7d')
    col3.write('*7 days period*')
    plt.figure(figsize=(5, 25))
    df_change['percent_change_7d'].plot(kind='barh', color=df_change.positive_percent_change_7d.map({True: 'g', False: 'r'}))
elif percent_timeframe == '24h':
    if sort_values == 'Yes':
        df_change = df_change.sort_values(by='percent_change_24h')
    col3.write('*24 hour period*')
    plt.figure(figsize=(5, 25))
    df_change['percent_change_24h'].plot(kind='barh', color=df_change.positive_percent_change_24h.map({True: 'g', False: 'r'}))
else:
    if sort_values == 'Yes':
        df_change = df_change.sort_values(by='percent_change_1h')
    col3.write('*1 hour period*')
    plt.figure(figsize=(5, 25))
    df_change['percent_change_1h'].plot(kind='barh', color=df_change.positive_percent_change_1h.map({True: 'g', False: 'r'}))

col3.pyplot(plt)
