import streamlit as st
import yfinance as yf
import pandas as pd

st.title("Aksjeoversikt")

tickers = {
    "BlueNord": "BNOR.OL",
    "TGS": "TGS.OL",
    "Elliptic Labs": "ELABS.OL",
    "C3.ai": "AI",
    "Super Micro": "SMCI",
    "Coinbase": "COIN"
}

data = {}
for name, ticker in tickers.items():
    stock = yf.Ticker(ticker)
    hist = stock.history(period="5d")
    if not hist.empty:
        data[name] = {
            "Ticker": ticker,
            "Siste pris": round(hist["Close"][-1], 2)
        }

df = pd.DataFrame.from_dict(data, orient="index")
st.dataframe(df)

for name, ticker in tickers.items():
    stock = yf.Ticker(ticker)
    hist = stock.history(period="5d")
    if not hist.empty:
        st.subheader(name)
        st.line_chart(hist["Close"])
