"""
CAPA 0 — Hola, Streamlit 👋

Objetivo: entender el modelo de Streamlit ANTES de meter IA.
  - El script se vuelve a ejecutar de arriba a abajo en CADA interacción.
  - Por eso, lo que quieras conservar entre clics va en `st.session_state`.
  - De paso, conocemos la base de datos de la bodega.

Correr:   streamlit run app_0_hola.py
"""

import sqlite3

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Capa 0 · Hola", page_icon="👋")

# Conexión SOLO LECTURA a la bodega (mode=ro => nadie puede modificarla)
DB = "file:data/bodega.db?mode=ro"

st.title("👋 Hola, Python Lima")
st.write(
    "Esta es nuestra primera app. Sin IA todavía: solo entendamos cómo "
    "funciona Streamlit."
)

# --- 1) El modelo de re-ejecución + session_state ----------------------------
st.subheader("1. ¿Por qué necesito `session_state`?")
st.write(
    "Cada vez que tocas un botón, Streamlit **vuelve a correr todo el script**. "
    "Para que el contador no se reinicie, guardamos su valor en `session_state`."
)

if "clicks" not in st.session_state:
    st.session_state.clicks = 0

if st.button("Súmame uno ➕"):
    st.session_state.clicks += 1

st.metric("Veces que hiciste clic", st.session_state.clicks)

st.divider()

# --- 2) Conozcamos la base de datos ------------------------------------------
st.subheader("2. Nuestra base de datos: la bodega 🏪")

con = sqlite3.connect(DB, uri=True)
tablas = pd.read_sql_query(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name", con
)
st.write("**Tablas disponibles:**", ", ".join(tablas["name"]))

tabla = st.selectbox("Elige una tabla para curiosear:", tablas["name"])
df = pd.read_sql_query(f"SELECT * FROM {tabla} LIMIT 50", con)
con.close()

st.dataframe(df, use_container_width=True)
st.caption(
    "👉 En las siguientes apps, en vez de elegir la tabla a mano, le vamos a "
    "**preguntar en español** y un agente de IA escribirá el SQL por nosotros."
)
