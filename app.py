import streamlit as st
import json2object
from pages import reservation_film
st.set_page_config(
    page_title="Réservation",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    """
    <style>
        [data-testid="collapsedControl"] {
            display: none
        }
        section[data-testid="stSidebar"] {
            display: none;
        }
        div.block-container {
            padding-left: 2rem;
            padding-right: 2rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

movies  =json2object.jsonToObject('Films')

col1, col2, col3,col4,col5 = st.columns(5)
columns = [col1, col2, col3,col4,col5]
with st.empty():
    for i,movie in enumerate(movies) :
        with columns[i % 5]:
            st.image(movie.cover, width=600 )
            st.button(label="",icon=":material/confirmation_number:" ,key=i, width="stretch",on_click="")


