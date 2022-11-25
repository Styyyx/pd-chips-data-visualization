import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

# Initial Setup
st.set_page_config(
    page_title='Chips Data',
    page_icon=Image.open('res/icon.png'),
    layout='wide',
    initial_sidebar_state='auto'
)

st.markdown("""
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """, unsafe_allow_html=True)

# Load Data
@st.cache
def getData():
    df = pd.read_csv('./chips.csv').drop(columns='Unnamed: 0')
    return df
df = getData()

TYPE_VALUES = df['Type'].unique()
VENDOR_VALUES = df['Vendor'].unique()
FOUNDRY_VALUES = df['Foundry'].unique()

# Remove whitespace from the top of the page and sidebar
st.markdown("""
        <style>
               .css-18e3th9 {
                    padding-top: 0rem;
                    padding-bottom: 0rem;
                    padding-left: 1.5rem;
                    padding-right: 1.5rem;
                }
        </style>
        """, unsafe_allow_html=True)

tabOverview, tabData = st.tabs(['Overview', 'Data'])

# Tab Overview
with tabOverview:
    with st.expander(label='Details', expanded=True):
        st.write(f'Total Entries: {df.shape[0]}')
        st.write(f'Chip Types: {", ".join(TYPE_VALUES)}')
        st.write(f'Vendors: {", ".join(sorted(VENDOR_VALUES))}')
        st.write(f'Foundries: {", ".join(sorted(FOUNDRY_VALUES))}')

    col1, col2, col3= st.columns([1,2,1])
    with col1:
        data = {
            'ids': ['GPU', 'CPU'],
            'labels': ['GPU', 'CPU'],
            'parents': ['', ''],
            'value': df['Type'].value_counts().tolist()
        }

        for i in TYPE_VALUES:
            vals = df.loc[df['Type'] == i]['Vendor'].value_counts()
            for j in VENDOR_VALUES:
                if j in vals.index:
                    data['ids'].append(f'{i} - {j}')
                    data['parents'].append(i)
                    data['labels'].append(j)
                    data['value'].append(vals[j])

        # st.plotly_chart(px.sunburst(data, 
        #     names='labels', parents='parents', values='value', 
        #     color='labels', color_discrete_sequence=px.colors.qualitative.Pastel,
        #     title='Chip Vendors'
        #     ))
        st.markdown('### Vendors')
        st.plotly_chart(
            go.Figure(go.Sunburst(
            ids=data['ids'],
            labels=data['labels'],
            parents=data['parents'],
            branchvalues='remainder',
            values=data['value'],
            marker={'colors':px.colors.qualitative.Pastel}
            )), use_container_width=True
        )

    with col2:
        st.markdown('### Chip Frequency and Release Date')
        st.plotly_chart(px.scatter(df, x='Release Date', y='Freq (MHz)', color='Type'))
    
# Tab Data
with tabData:
    query = ""
    with st.container():
        st.write('Filter Data')
        
        filterType = st.multiselect('Type', 
            options=TYPE_VALUES, default=TYPE_VALUES)
        filterFoundry = st.multiselect('Foundry', 
            options=FOUNDRY_VALUES, default=FOUNDRY_VALUES)
        filterVendor = st.multiselect('Vendor', 
            options=VENDOR_VALUES, default=VENDOR_VALUES)

        query = df.query(
            'Type == @filterType & Foundry == @filterFoundry & Vendor == @filterVendor'
        )

    st.dataframe(query, use_container_width=True)
    st.write(f'Total Rows: {query.shape[0]}')