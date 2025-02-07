import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import datetime
import plotly.graph_objects as go

# Funktion för att ansluta till MySQL-databasen
def db_connection():
    try:
        cnxn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="dinmamma",
            database="ArtiklarDB"
        )
        return cnxn
    except mysql.connector.Error as err:
        st.error(f"Database connection error: {err}")
        return None

# Hämta data från MySQL
def get_data():
    cnxn = db_connection()
    if cnxn:
        query = "SELECT * FROM News"
        df = pd.read_sql(query, cnxn, index_col="id")
        cnxn.close()
        
        # Konvertera "published" till datetime och skapa en ren datumkolumn
        if "published" in df.columns:
            df["published"] = pd.to_datetime(df["published"], errors="coerce")
            df["date"] = df["published"].dt.date
        return df
    else:
        return pd.DataFrame()

# Hämta data
st.set_page_config(page_title="ML 4 the win", layout="wide")
df = get_data()

# Banner överst
st.markdown("""
    <h1 style='text-align: center; background-color: #2C2C2F; color: white; padding: 15px;'>ML 4 the win</h1>
    """, unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# SIDOFÄLT - Filter
st.sidebar.header("🔍 Filter")

# Hämta kategorikolumner automatiskt
category_columns = [col for col in df.columns if col not in ["id", "title", "summary", "link", "published", "topic", "date"]]
category_dropdown_options = ["Alla"] + category_columns  # Separera dropdown och faktiska kolumner

# Skapa en dropdown för att välja kategori
category = st.sidebar.selectbox("Välj kategori", category_dropdown_options, key="category_filter")

# Skapa filtrerad DataFrame baserat på valt filter
if category == "Alla":
    df_filtered = df.copy()  # Behåll alla rader om "Alla" är vald
else:
    df_filtered = df[df[category] == 1]  # Filtrera efter vald kategori

# Datumintervall och sökning
date_range = st.sidebar.date_input("Välj datumintervall", [])
search_query = st.sidebar.text_input("Sök efter nyckelord", key="search_filter")

# KPI-Beräkningar
total_articles = len(df_filtered)
articles_with_topic = (df_filtered["topic"] != "").sum()  # Räknar alla som faktiskt fått en topic
percentage_with_topic = (articles_with_topic / total_articles) * 100 if total_articles > 0 else 0

# Anpassad KPI-design
kpi_template = """
    <div style="
        background-color: #2C2C2F;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
        font-size: 24px;
        font-weight: bold;
        margin: 30px 5px 10px 5px;
        box-shadow: 3px 3px 6px rgba(0, 0, 0, 0.2);
        width: 100%;
        display: block;">
        <h3 style='text-align: center; font-size: 28px; font-weight: normal;'>{title}</h3>
        <p style='text-align: center; font-size: 36px; color: #FFD700; font-weight: bold;'>{value}</p>
    </div>
"""

# Visa KPI:er
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(kpi_template.format(title="📊 Totalt antal artiklar", value=total_articles), unsafe_allow_html=True)
with col2:
    st.markdown(kpi_template.format(title="📝 Antal artiklar med ämne", value=articles_with_topic), unsafe_allow_html=True)
with col3:
    st.markdown(kpi_template.format(title="📈 Andel med ett ämne i %", value=f"{percentage_with_topic:.2f}%"), unsafe_allow_html=True)


# 📄 Visa filtrerad data utan att orsaka renderingsfel
st.subheader("📄 Dataförhandsvisning")

# Se till att df_filtered alltid existerar, även om det är tomt
if "df_filtered" not in locals():
    df_filtered = df.copy()  # Säkerhetsåtgärd för att undvika fel

st.dataframe(df_filtered)  # Rendera utan onödiga kontroller


# Skapa layout för diagram
col1, col2 = st.columns([1, 1])

startdatum = datetime.date(2025, 2, 1)  # Sätt till 1 februari 2025

# 📊 Diagram 1: Antal artiklar per kategori
st.subheader("📊 Antal artiklar per kategori")

if category_columns:
    articles_per_category = df_filtered[category_columns].sum().reset_index()
    articles_per_category.columns = ["Kategori", "Antal Artiklar"]

    fig1 = go.Figure()

    fig1.add_trace(go.Bar(
        x=articles_per_category["Kategori"],
        y=articles_per_category["Antal Artiklar"],
        marker_color="#FFD700",  # Guldig färg
        text=articles_per_category["Antal Artiklar"],  # Data labels
        textposition="outside"  # Placera labels ovanför staplarna
    ))

    fig1.update_layout(
        title="Antal artiklar per kategori",
        xaxis_title="Kategori",
        yaxis_title="Antal artiklar"
    )

    st.plotly_chart(fig1, use_container_width=True)
else:
    st.warning("Inga kategorier hittades i datasetet.")

# 📊 Diagram 2: Antal artiklar per dag
st.subheader("📊 Antal artiklar per dag")

if "date" in df_filtered.columns:
    articles_per_day = df_filtered.groupby("date").size().reset_index()
    articles_per_day.columns = ["Datum", "Antal Artiklar"]

    fig2 = go.Figure()

    fig2.add_trace(go.Bar(
        x=articles_per_day["Datum"],
        y=articles_per_day["Antal Artiklar"],
        marker_color="#FFD700",  # Guldig färg
        text=articles_per_day["Antal Artiklar"],  # Data labels
        textposition="outside"  # Placera labels ovanför staplarna
    ))

    fig2.update_layout(
        title="Antal artiklar per dag",
        xaxis_title="Datum",
        yaxis_title="Antal artiklar",
        xaxis=dict(range=[startdatum, articles_per_day["Datum"].max()])
    )

    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("Kolumnen 'date' saknas i datasetet!")

# 📈 Linjediagram för utveckling över tid
st.subheader("📈 Utveckling av antal artiklar över tid")

if "date" in df_filtered.columns:
    fig3 = go.Figure()

    fig3.add_trace(go.Scatter(
        x=articles_per_day["Datum"],
        y=articles_per_day["Antal Artiklar"],
        mode="lines+markers",  # Linje + punkter
        marker=dict(color="#FFD700", size=8),  # Guld färg på punkterna
        line=dict(color="#FFD700", width=2),  # Guld färg på linjen
        text=articles_per_day["Antal Artiklar"],  # Data labels
        textposition="top center"  # Placera labels ovanför punkterna
    ))

    fig3.update_layout(
        title="Utveckling av antal artiklar över tid",
        xaxis_title="Datum",
        yaxis_title="Antal artiklar",
        xaxis=dict(range=[startdatum, articles_per_day["Datum"].max()])
    )

    st.plotly_chart(fig3, use_container_width=True)
else:
    st.warning("Kan inte visa linjediagram – 'date'-kolumnen saknas.")