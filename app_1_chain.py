"""
CAPA 1 — El LLM escribe el SQL (todavía SIN agente) 🟢

Idea: una sola llamada al modelo.
  1. Le damos el ESQUEMA de la base de datos dentro del prompt.
  2. El modelo devuelve UNA consulta SQL.
  3. Nosotros la ejecutamos (solo lectura) y mostramos la tabla.

Esto ya es útil... pero el modelo no puede explorar, ni corregirse si se
equivoca. Eso lo arreglamos en la Capa 2 con un agente.

Correr:   streamlit run app_1_chain.py
"""

import os
import re
import sqlite3

import pandas as pd
import streamlit as st
from langchain_groq import ChatGroq

st.set_page_config(page_title="Capa 1 · El LLM escribe SQL", page_icon="🟢")

# La API key se lee de .streamlit/secrets.toml
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

DB = "file:data/bodega.db?mode=ro"
MODELO = "llama-3.3-70b-versatile"

PROMPT = """Eres un experto en SQL para SQLite. Esta es la estructura de la base de datos:

{schema}

Escribe UNA sola consulta SQL (solo SELECT) que responda la pregunta del usuario.
Devuelve ÚNICAMENTE el SQL, sin explicaciones ni ```.

Pregunta: {pregunta}
SQL:"""


# @st.cache_resource: crea el modelo UNA vez y lo reutiliza entre re-ejecuciones
@st.cache_resource
def get_llm():
    return ChatGroq(model=MODELO, temperature=0)


@st.cache_data
def get_schema() -> str:
    """Devuelve los CREATE TABLE de la base, que es lo que el LLM necesita ver."""
    con = sqlite3.connect(DB, uri=True)
    filas = con.execute(
        "SELECT sql FROM sqlite_master WHERE type='table'"
    ).fetchall()
    con.close()
    return "\n\n".join(f[0] for f in filas if f[0])


def limpiar_sql(texto: str) -> str:
    """El modelo a veces envuelve el SQL en ```sql ... ```; lo quitamos."""
    return re.sub(r"```sql|```", "", texto).strip()


st.title("🟢 Capa 1 — El LLM escribe el SQL")
st.caption(
    "Una sola llamada: el modelo ve el esquema y genera el SELECT; "
    "nosotros lo ejecutamos."
)

pregunta = st.text_input(
    "Pregunta en español:", "¿Cuáles son los 5 productos más vendidos?"
)

if st.button("Consultar") and pregunta:
    llm = get_llm()
    with st.spinner("Pensando el SQL..."):
        respuesta = llm.invoke(
            PROMPT.format(schema=get_schema(), pregunta=pregunta)
        )
        sql = limpiar_sql(respuesta.content)

    st.code(sql, language="sql")

    # Guardia de seguridad simple: solo permitimos SELECT
    if not sql.lower().lstrip().startswith("select"):
        st.error("Por seguridad solo ejecutamos consultas SELECT.")
    else:
        try:
            con = sqlite3.connect(DB, uri=True)
            df = pd.read_sql_query(sql, con)
            con.close()
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"El SQL falló: {e}")
            st.info(
                "👀 Fíjate: si el modelo se equivoca, aquí la app simplemente "
                "muestra el error. En la Capa 2 el agente lo verá y se corregirá solo."
            )
