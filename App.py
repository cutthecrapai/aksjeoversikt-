import streamlit as st
import yfinance as yf
import pandas as pd
from forex_python.converter import CurrencyRates
from openai import OpenAI
from datetime import datetime

st.set_page_config(page_title="Oles porteføljeassistent", layout="wide")
st.title("Oles aksjeoversikt og markedsvurdering")

# === OpenAI API-nøkkel ===
api_key = st.text_input("OpenAI API-nøkkel (vises ikke)", type="password")
if api_key:
    client = OpenAI(api_key=api_key)

# === Hent valutakurs EUR→NOK ===
c = CurrencyRates()
try:
    eur_to_nok = c.get_rate('EUR', 'NOK')
except:
    eur_to_nok = 11.50

# === Porteføljeinfo ===
portfolio = {
    "BlueNord": {"ticker": "BNOR.OL", "antall": 166},
    "TGS": {"ticker": "TGS.OL", "antall": 376},
    "Elliptic Labs": {"ticker": "ELABS.OL", "antall": 700},
    "GZUR": {"ticker": "GZUR.OL", "antall": 62},
    "Celestica": {"ticker": "CLS", "antall": 4},
    "Coinbase": {"ticker": "COIN", "antall": 2},
    "WisdomTree Gold": {"ticker": "VZLD.DE", "antall": 62, "valuta": "EUR"}
}

data = []

# === Hent kurs og beregn verdi ===
for navn, info in portfolio.items():
    ticker = yf.Ticker(info["ticker"])
    try:
        hist = ticker.history(period="
