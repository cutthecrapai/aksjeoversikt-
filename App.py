import streamlit as st
import yfinance as yf
import pandas as pd
from forex_python.converter import CurrencyRates
from openai import OpenAI
from datetime import datetime

st.set_page_config(page_title="Oles porteføljeassistent", layout="wide")
st.title("Oles aksjeoversikt og markedsvurdering")

api_key = st.text_input("OpenAI API-nøkkel (vises ikke)", type="password")
if api_key:
    client = OpenAI(api_key=api_key)

c = CurrencyRates()
try:
    eur_to_nok = c.get_rate('EUR', 'NOK')
except:
    eur_to_nok = 11.50

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

for navn, info in portfolio.items():
    ticker = yf.Ticker(info["ticker"])
    try:
        hist = ticker.history(period="1d")
    except:
        hist = pd.DataFrame()

    if not hist.empty:
        pris = hist["Close"].iloc[-1]
        valuta = info.get("valuta", "NOK")
        pris_nok = pris * eur_to_nok if valuta == "EUR" else pris
        verdi = pris_nok * info["antall"]
        data.append({
            "Aksje": navn,
            "Ticker": info["ticker"],
            "Antall": info["antall"],
            "Siste pris": f"{pris:.2f} {valuta}",
            "Verdi (NOK)": round(verdi, 2)
        })
    else:
        data.append({
            "Aksje": navn,
            "Ticker": info["ticker"],
            "Antall": info["antall"],
            "Siste pris": "Ingen data",
            "Verdi (NOK)": 0
        })

df = pd.DataFrame(data).sort_values("Verdi (NOK)", ascending=False).set_index("Aksje")
st.dataframe(df, use_container_width=True)

totalverdi = df["Verdi (NOK)"].sum()
st.subheader(f"Total porteføljeverdi: **{round(totalverdi, 2)} kr**")

if api_key:
    if st.button("Vis dagens vurdering"):
        aksjeliste = "\n".join(
            [f"- {row.name} ({row['Ticker']}): {row['Verdi (NOK)']} NOK" for _, row in df.iterrows()]
        )
        prompt = f"""
Du er en erfaren finansrådgiver. Her er brukerens aksjeportefølje i dag:

{aksjeliste}

Gi en profesjonell, ærlig og kort vurdering av hver aksje basert på dagens marked.
Kommentér på risiko, stabilitet og eventuell bevegelse.
"""
        with st.spinner("Henter vurdering..."):
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content":]()
