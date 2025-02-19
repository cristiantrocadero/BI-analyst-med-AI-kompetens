import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import datetime
import plotly.graph_objects as go
from wordcloud import WordCloud
import regex as re
import nltk
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
# nltk.download("stopwords") # se till att den är nerladdad innan du kör allt

# Funktion för att ansluta till MySQL-databasen (NU MED SQLALCHEMY)
def db_connection():
    try:
        database_url = "mysql+mysqlconnector://root:dinmamma@localhost/ArtiklarDB"
        engine = create_engine(database_url)
        return engine
    except Exception as err:
        st.error(f"Database connection error: {err}")
        return None

# Hämta data från MySQL och ändra kolumnnamn direkt
def get_data():
    engine = db_connection()
    if engine:
        query = "SELECT * FROM News"
        df = pd.read_sql(query, engine, index_col="id")  

        # Byt kolumnnamn direkt vid inläsning
        column_rename_map = {
            "id": "Index",
            "title": "Titel",
            "summary": "Summering",
            "link": "Länk",
            "published": "Publicerad",
            "topic": "Ämne",
            "politik": "Politik",
            "utbildning": "Utbildning",
            "religion": "Religion",
            "miljo": "Miljö",
            "ekonomi": "Ekonomi",
            "livsstilfritt": "Fritid & Nöje",
            "samhallekonflikter": "Samhälle & Konflikter",
            "halsa": "Hälsa",
            "idrott": "Idrott",
            "vetenskapteknik": "Vetenskap & Teknik"
        }

        df.rename(columns=column_rename_map, inplace=True)

        # Konvertera "Publicerad" till datetime och skapa en ren datumkolumn
        if "Publicerad" in df.columns:
            df["Publicerad"] = pd.to_datetime(df["Publicerad"], errors="coerce")
            df["Datum"] = df["Publicerad"].dt.date

        return df
    else:
        return pd.DataFrame()


# Streamlit Konfiguration
st.set_page_config(page_title="ML av Grupp 3", layout="wide")
df = get_data()

st.markdown("""
    <style>
        /* Hela sidans bakgrund */
        .stApp {
            background: linear-gradient(135deg, #3B3E79, #242B64) !important;
            color: white;
        }

        /* Ta bort den vita linjen högst upp */
        header[data-testid="stHeader"] {
            background: linear-gradient(135deg, #3B3E79, #242B64) !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Banner överst
st.markdown("""
    <h1 style='text-align: center; background-color: #091043; border-radius: 10px; color: white; padding: 15px;'>Automatisk Nyhetsklassificering – Grupp 3</h1>
    """, unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# SIDOFÄLT - Navigation & Dynamiska Filter
st.sidebar.header("🔍 Navigation & Filter")

with st.sidebar:
    selected = option_menu(
        menu_title=None,
        options=["Start", "Data", "Analys", "Sammanfattning"],
        icons=["house", "database", "bar-chart", "file-text"],
        default_index=0,
        styles={
        "nav-link-selected": {
        "background-color": "#091043",  # Mörkblå bakgrund när vald
        "color": "white",  # Vit text när vald
    }
}

    )

st.markdown("""
    <style>
        /* Ändra endast bakgrundsfärgen på hela sidomenyn EFTER option_menu */
        section[data-testid="stSidebar"] {
            background-color: #242B64 !important;
        }
    </style>
    """, unsafe_allow_html=True)


# Dynamiska filter - visas bara när de behövs
st.markdown("""
    <style>
        /* Gör all text i sidofältets widgets vit */
        section[data-testid="stSidebar"] label {
            color: white !important;
        }
    </style>
    """, unsafe_allow_html=True)

startdatum = datetime.date(2025, 1, 25)
slutdatum = datetime.date(2025, 2, 28)

if selected in ["Data", "Analys"]:
    category_columns = [col for col in df.columns if col not in ["Index", "Titel", "Summering", "Länk", "Publicerad", "Ämne", "Datum"]]
    category_dropdown_options = ["Alla"] + category_columns
    category = st.sidebar.selectbox("Välj kategori", category_dropdown_options, key="category_filter")

    date_range = st.sidebar.date_input(
        "Välj datumintervall", 
        [startdatum, slutdatum], 
        min_value=startdatum, 
        max_value=slutdatum
    )

if selected == "Data":
    search_query = st.sidebar.text_input("Sök efter nyckelord", key="search_filter").strip().lower()
else:
    search_query = ""  # Om vi inte är på "Data", ställ in som tom sträng

# Fix: Ensure date range always has two values
if selected in ["Data", "Analys"]:
    if len(date_range) == 1:
        start_date = date_range[0]
        end_date = date_range[0]
    elif len(date_range) == 2:
        start_date = date_range[0]
        end_date = date_range[1]
    else:
        start_date = startdatum
        end_date = slutdatum
else:
    start_date = startdatum
    end_date = slutdatum

# Filtrera datasetet endast vid behov
df_filtered = df.copy()

if selected in ["Data", "Analys"]:
    if category != "Alla":
        df_filtered = df_filtered[df_filtered[category] == 1]
    df_filtered = df_filtered[(df_filtered["Datum"] >= start_date) & (df_filtered["Datum"] <= end_date)]

if selected == "Data" and search_query:
    df_filtered = df_filtered[
        df_filtered["Titel"].str.lower().str.contains(search_query, na=False) |
        df_filtered["Summering"].str.lower().str.contains(search_query, na=False)
    ]

# KPI-Beräkningar (göm KPIer om "Conclusion" är vald)
if selected != "Sammanfattning":
    total_articles = len(df_filtered)
    articles_with_topic = (df_filtered["Ämne"] != "").sum()
    percentage_with_topic = (articles_with_topic / total_articles) * 100 if total_articles > 0 else 0

    kpi_template = """
        <div style="background-color: #091043; padding: 20px; border-radius: 10px; text-align: center; color: white;
            font-size: 24px; font-weight: bold; margin: 30px 5px 10px 5px; box-shadow: 3px 3px 6px rgba(0, 0, 0, 0.2);
            width: 100%; display: block;">
            <h3 style='text-align: center; font-size: 28px; font-weight: normal;'>{title}</h3>
            <p style='text-align: center; font-size: 36px; color: #FFD700; font-weight: bold;'>{value}</p>
        </div>
    """
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(kpi_template.format(title="📊 Totalt antal artiklar", value=total_articles), unsafe_allow_html=True)
    with col2:
        st.markdown(kpi_template.format(title="📝 Artiklar med ämne", value=articles_with_topic), unsafe_allow_html=True)
    with col3:
        st.markdown(kpi_template.format(title="📈 Andel med ämne (%)", value=f"{percentage_with_topic:.2f}%"), unsafe_allow_html=True)

# MENYVAL
if selected == "Start":
    st.subheader("📄 Dataförhandsvisning (10 rader)")
    df_preview = df.head(10).drop(columns=["Datum"], errors="ignore")  # Ta bort "date" vid visning
    st.dataframe(df_preview)

elif selected == "Data":
    st.title("📊 Utforska hela datasetet")
    df_to_display = df_filtered.drop(columns=["Datum"], errors="ignore")  # Ta bort "date" vid visning
    st.dataframe(df_to_display)

elif selected == "Analys":
    st.title("📊 Dataanalys & Diagram")

    # Diagram 1: Antal artiklar per kategori
    if category_columns:
        articles_per_category = df_filtered[category_columns].sum().reset_index()
        articles_per_category.columns = ["Kategori", "Antal Artiklar"]

        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=articles_per_category["Kategori"],
            y=articles_per_category["Antal Artiklar"],
            marker_color="#FFD700",
            text=articles_per_category["Antal Artiklar"],
            textposition="outside"
        ))
        fig1.update_layout(title="Antal artiklar per kategori", xaxis_title="Kategori", yaxis_title="Antal artiklar")
        st.plotly_chart(fig1, use_container_width=True)

    # Diagram 2: Antal artiklar per dag
    articles_per_day = df_filtered.groupby("Datum").size().reset_index()
    articles_per_day.columns = ["Datum", "Antal Artiklar"]

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=articles_per_day["Datum"],
        y=articles_per_day["Antal Artiklar"],
        marker_color="#FFD700",
        text=articles_per_day["Antal Artiklar"],
        textposition="outside"
    ))
    fig2.update_layout(title="Antal artiklar per dag", xaxis_title="Datum", yaxis_title="Antal artiklar", xaxis=dict(range=[start_date, end_date]))
    st.plotly_chart(fig2, use_container_width=True)

    # Diagram 3: Utveckling över tid
    articles_per_day["Kumulativ Antal Artiklar"] = articles_per_day["Antal Artiklar"].cumsum()

    # Diagram 3: Utveckling över tid (Ackumulerad total)
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=articles_per_day["Datum"],
        y=articles_per_day["Kumulativ Antal Artiklar"],  # Ändrat till ackumulerad total
        mode="lines+markers",
        marker=dict(color="#FFD700", size=8),
        line=dict(color="#FFD700", width=2),
        text=articles_per_day["Kumulativ Antal Artiklar"],  # Uppdaterad text
        textposition="top center"
    ))
    fig3.update_layout(
        title="Utveckling av antal artiklar över tid",
        xaxis_title="Datum",
        yaxis_title="Ackumulerat antal artiklar",  # Uppdaterad y-titel
        xaxis=dict(range=[start_date, end_date])
    )
    st.plotly_chart(fig3, use_container_width=True)

    # wordcloud här plz
    st.subheader("☁️ Vanligast förekommande orden")

    if not df_filtered.empty and "Titel" in df_filtered.columns:  # Check if "topic" exists
        # Combine all topics into a single text string (removes NaN values)
        text = " ".join(df_filtered["Titel"].dropna())  # Uses "topic" instead of "title"

        # Remove HTML tags and special characters
        text = re.sub(r"<.*?>", "", text)  # Remove HTML tags
        text = re.sub(r"[^a-zA-ZåäöÅÄÖ\s]", "", text)  # Remove special characters and numbers

        # Load Swedish stopwords  
        swedish_stopwords = set(stopwords.words("swedish"))

        # Additional words to remove
        extra_stopwords = {
            "img", "jpg", "png", "https", "säger", "ska", "år", "bör", "kommer", "måste", 
            "kan", "ska", "vill", "finns", "bli", "får", "gör", "mer", "nya", "tar", "tog",
            "fick", "få", "fler", "första", "hela", "stor", "därför", "det", "du", "jag",
            "han", "hon", "den", "det", "de", "vi", "ni", "man", "en", "ett", "alla", 
            "så", "här", "inte", "att", "är", "och", "eller", "men", "som", "vad", "vilka",
            "vilket", "med", "till", "mot", "efter", "under", "före", "in", "ut", "på", 
            "av", "om", "vid", "från", "mellan", "mot", "över", "under", "någon", "något",
            "några", "hans", "hennes", "dess", "deras", "min", "mitt", "mina", "din", 
            "ditt", "dina", "vår", "vårt", "våra", "er", "ert", "era", "DN", "SvD", "GP", 
            "går", "ta", "se", "göra", "ökar", "nytt", "ny", "inför", "flera", "bra", "aldrig", "igen"
        }
        all_stopwords = swedish_stopwords.union(extra_stopwords)


        # Generate WordCloud
        wordcloud = WordCloud(width=1200, height=600, max_words=50, background_color="white",
                            colormap="coolwarm", stopwords=all_stopwords, 
                            contour_color="black", contour_width=1.5,
                            prefer_horizontal=0.9, font_path=None).generate(text)

        # Display WordCloud
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")  # Hide axes
        st.pyplot(fig)
    else:
        st.write("No data available or the 'topic' column is missing.")

elif selected == "Sammanfattning":
    st.title("📋 Sammanfattning")
    st.markdown("<h2 style='text-align: left;'>Resultat</h2>", unsafe_allow_html=True)

    st.write("""
    - **Övervikt av vissa kategorier:** De flesta nyhetsartiklar handlar om samhälle och konflikter, vilket kan göra det svårare för modellen att korrekt kategorisera andra ämnen, såsom religion eller utbildning.

    - **Påverkan av urvalet av tidningar:** Eftersom vissa tidningar fokuserar mer på samhälle och konflikter, kan modellen bli snedvriden mot dessa kategorier. Frågan är om den är tillräckligt tränad för att hantera andra ämnen.

    - **Tidsbegränsningens effekt:** Att alla nyheter samlades in under en kort tidsperiod kan ha påverkat fördelningen av kategorier. Exempelvis kan en stor händelse under insamlingsperioden ha dominerat nyhetsflödet och därmed påverkat modellens inlärning.

    - **Manuell datainsamling:** Eftersom vi saknar automatiserad inhämtning av artiklar finns en risk att vi missar nyheter som publiceras vid vissa tider på dygnet. Dessutom kan nyhetsflödet skilja sig mellan vardagar och helger.

    - **Felaktiga kategoriseringar:** Enstaka ord kan påverka modellens klassificering på ett missvisande sätt. Exempelvis kan ordet "COVID" göra att en artikel klassificeras som "Hälsa", även om den egentligen handlar om något annat.
    """)

    st.markdown("<h2 style='text-align: left;'>Förslag på förbättringar</h2>", unsafe_allow_html=True)

    st.write("""
    - **Införa sentimentanalys** för att se hur tonen i artiklar förändras över tid.
             
    - **Automatiserad datainsamling**, exempelvis en gång i timmen, för att säkerställa ett mer representativt dataset.
             
    - **Analysera om positiva eller negativa nyheter korrelerar** med tid på dygnet eller veckodag.
             
    - **Förbättra hanteringen av nyckelord** så att kategoriseringen baseras på sammanhang snarare än enstaka ord.
             
    - **Titta på andra NLP-modeller** som kan fungera bättre för kategorisering.
             
    - **Hantering av äldre artiklar** som återanvänds i RSS-flödet, för att undvika att de klassificeras som nya nyheter.
    """)