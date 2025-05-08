import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser

st.set_page_config(page_title="Oles portefølje", layout="wide")
st.title("Oles aksjeoversikt")

# Porteføljeinfo
portfolio = {
    "BlueNord": {"ticker": "BNOR.OL", "antall": 166},
    "TGS": {"ticker": "TGS.OL", "antall": 376},
    "Elliptic Labs": {"ticker": "ELABS.OL", "antall": 700},
    "GZUR": {"ticker": "GZUR.OL", "antall": 62},
    "Celestica": {"ticker": "CLS", "antall": 4},
    "Coinbase": {"ticker": "COIN", "antall": 2}
}

data = []

# Hent priser og beregn verdi
for navn, info in portfolio.items():
    ticker = yf.Ticker(info["ticker"])
    hist = ticker.history(period="1d")
    if not hist.empty:
        pris = hist["Close"].iloc[-1]
        verdi = pris * info["antall"]
        data.append({
            "Aksje": navn,
            "Ticker": info["ticker"],
            "Antall": info["antall"],
            "Siste pris": round(pris, 2),
            "Verdi": round(verdi, 2)
        })
    else:
        data.append({
            "Aksje": navn,
            "Ticker": info["ticker"],
            "Antall": info["antall"],
            "Siste pris": "Ingen data",
            "Verdi": 0
        })

df = pd.DataFrame(data).sort_values("Verdi", ascending=False).set_index("Aksje")
st.dataframe(df, use_container_width=True)

totalverdi = df["Verdi"].sum()
st.subheader(f"Total porteføljeverdi: **{round(totalverdi, 2)} kr**")

# Nyhetsoversikt
st.markdown("### Nyheter om aksjene")
nyhetskilder = {
    "BlueNord": "https://news.google.com/rss/search?q=BlueNord",
    "TGS": "https://news.google.com/rss/search?q=TGS+ASA",
    "Elliptic Labs": "https://news.google.com/rss/search?q=Elliptic+Labs",
    "GZUR": "https://news.google.com/rss/search?q=GZUR",
    "Celestica": "https://news.google.com/rss/search?q=Celestica",
    "Coinbase": "https://news.google.com/rss/search?q=Coinbase"
}

for navn, rss_url in nyhetskilder.items():
    st.markdown(f"#### {navn}")
    feed = feedparser.parse(rss_url)
    for entry in feed.entries[:3]:
        st.markdown(f"- [{entry.title}]({entry.link})")
