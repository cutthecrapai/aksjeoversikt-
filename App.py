import streamlit as st
import yfinance as yf
import pandas as pd
from forex_python.converter import CurrencyRates
import openai
from datetime import datetime

st.set_page_config(page_title="Oles porteføljeassistent", layout="wide")
st.title("Oles aksjeoversikt og markedsvurdering")

# === OpenAI API-nøkkel ===
api_key = st.text_input("OpenAI API-nøkkel (lim inn her – vises ikke)", type="password")
if api_key:
    openai.api_key = api_key

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

# === GPT-generert vurdering ===
if api_key:
    if st.button("Vis dagens vurdering"):
        aksjeliste = "\n".join([f"- {row.name} ({row['Ticker']}): {row['Verdi (NOK)']} NOK" for _, row in df.iterrows()])
        prompt = f"""
Du er en økonomisk rådgiver. Her er brukerens aksjeportefølje i dag:

{aksjeliste}

Basert på denne porteføljen, dagens markedsstemning og kjente faktorer – gi en rolig, ærlig vurdering av hver aksje.
Unngå hype, vær analytisk og kortfattet. Kommentér gjerne om aksjen er stabil, risikabel, verdt å følge, eller har ny potensiell bevegelse.

Vis det som én kort oversikt til eieren.
        """
        with st.spinner("Henter vurdering..."):
           from openai import OpenAI

client = OpenAI(api_key=api_key)
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}]
)
vurdering = response.choices[0].message.content

            st.markdown("### Dagens porteføljevurdering:")
            st.write(vurdering)

    if st.button("Vis dagens swing trade-forslag"):
        prompt = f"""
Du er en erfaren trader. Gi ett forslag til en mulig swing trade med tidsvindu 1–3 dager, basert på dagens markedsforhold (Norge og USA).
Ta hensyn til volum, momentum, eventuelle nyheter og risiko. Skriv kort og konkret. Bruk følgende format:

Aksje:  
Anbefaling:  
Bakgrunn:  
Risiko:  
Tidsvindu:
        """
        with st.spinner("Analyserer markedet..."):
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            tips = response.choices[0].message.content
            st.markdown("### Dagens swing trade-forslag:")
            st.write(tips)
else:
    st.info("Lim inn OpenAI API-nøkkelen for å aktivere vurdering og swing trade-analyse.")
