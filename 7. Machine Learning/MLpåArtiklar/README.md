Hur man kör appen
Starta SQL-databasen:
Se till att din MySQL-databas är igång. Skapa en databas med namnet ArtiklarDB och en tabell news med de kolumner som behövs enligt projektets krav.

Kör hela pipelinen med DbTransfer_5.py:
Detta skript kör alla nödvändiga steg i pipelinen. Det hämtar nyhetsartiklar via RSS, bearbetar och strukturerar data, tränar maskininlärningsmodellen, predikterar kategorier och överför slutresultatet till databasen.

Kör följande kommando i terminalen:
python DbTransfer_5.py

Starta Streamlit-appen:
När pipelinen har körts och databasen är uppdaterad, starta Streamlit-appen för att visualisera och analysera data. Kör:
streamlit run streamlitapp1.py
