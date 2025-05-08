import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
from forex_python.converter import CurrencyRates
from datetime import datetime, timedelta

st.set_page_config(page_title="Oles portefølje", layout="wide")
st.title("Oles aksjeoversikt")

# Hent live EUR→NOK-kurs
c = CurrencyRates()
try:
    eur_to_nok = c.get_rate('EUR', 'NOK')
except:
    eur_to_nok = 11.50  # fallback hvis API feiler

# Porteføljeinfo
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

# Pris og verdi
for navn, info in portfolio.items():
    ticker = yf.Ticker(info["ticker"])
    try:
        hist = ticker.history(period="1d")
    except:
        hist = pd.DataFrame()

    if not hist.empty:
        pris = hist["Close"].iloc[-1]
        valuta = info.get("valuta", "NOK")
        if valuta == "EUR":
            pris_nok = pris * eur_to_nok
        else:
            pris_nok = pris
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

# Nyheter – samlet visning med dagens dato
st.markdown("### Dagens nyheter")

nyhetskilder = {
    "BlueNord": "https://news.google.com/rss/search?q=BlueNord",
    "TGS": "https://news.google.com/rss/search?q=TGS+ASA",
    "Elliptic Labs": "https://news.google.com/rss/search?q=Elliptic+Labs",
    "GZUR": "https://news.google.com/rss/search?q=GSP+Resource+Corp+stock",
    "Celestica": "https://news.google.com/rss/search?q=Celestica",
    "Coinbase": "https://news.google.com/rss/search?q=Coinbase",
    "WisdomTree Gold": "https://news.google.com/rss/search?q=WisdomTree+Physical+Swiss+Gold"
}

i_dag = datetime.utcnow().date()
nyheter = []

for navn, rss_url in nyhetskilder.items():
    feed = feedparser.parse(rss_url)
    for entry in feed.entries:
        publ_dato = entry.get("published_parsed")
        if publ_dato:
            nyhetsdato = datetime(*publ_dato[:6]).date()
            if nyhetsdato == i_dag:
                nyheter.append((navn, entry.title, entry.link))

# Vis nyheter i sortert rekkefølge
for navn, tittel, link in sorted(nyheter, key=lambda x: x[0]):
    st.markdown(f"- **[{navn}]**: [{tittel}]({link})")

