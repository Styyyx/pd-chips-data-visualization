import pandas as pd
import plotly.express as px
import streamlit as st

@st.cache
def getData():
    df = pd.read_csv('chips.csv')
    return df

df = getData()

