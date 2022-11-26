import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Initial Setup
st.set_page_config(
    page_title='Chips Data',
    page_icon=':bar_chart:',
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
    df['Release Date'] = pd.DatetimeIndex(df['Release Date'])
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

with st.empty():
    col1, col2 = st.columns([9, 1])
    with col1:
        st.markdown('# Chips Data Visualization')
    with col2:
        st.markdown('by: Patrick Alcantara')

tabOverview, tabData = st.tabs(['Overview', 'Data'])

# Tab Overview
with tabOverview:
    with st.container():
        st.write(f'Total Entries: {df.shape[0]}')
        st.write(f'Chip Types: {", ".join(TYPE_VALUES)}')

        _, col1, col2, _, col3, col4, _ = st.columns([1,4,8,1,4,8,1])

        with col1:
            st.markdown('# Vendors')
            sdf = df['Vendor'].value_counts().to_frame().rename(columns={'Vendor':'Count'})
            sdf.index.name = 'Vendor'
            st.table(sdf['Count'])

        with col3:
            st.markdown('# Foundries')
            sdf = df['Foundry'].value_counts().to_frame().rename(columns={'Foundry':'Count'})
            sdf.index.name = 'Foundry'
            st.table(sdf['Count'])

        with col2:
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

            st.plotly_chart(go.Figure(go.Sunburst(ids=data['ids'], labels=data['labels'], parents=data['parents'],
                branchvalues='total', values=data['value'], marker={'colors':px.colors.qualitative.Pastel}
                )).update_traces(textinfo='label+percent parent'), use_container_width=True)
        
        with col4:
            data = {
                'ids': ['GPU', 'CPU'],
                'labels': ['GPU', 'CPU'],
                'parents': ['',''],
                'value': df['Type'].value_counts().tolist()
            }

            for i in TYPE_VALUES:
                vals = df.loc[df['Type'] == i]['Foundry'].value_counts()
                for j in FOUNDRY_VALUES:
                    if j in vals.index:
                        data['ids'].append(f'{i} - {j}')
                        data['parents'].append(i)
                        data['labels'].append(j)
                        data['value'].append(vals[j])
            st.plotly_chart(go.Figure(go.Sunburst(ids=data['ids'], labels=data['labels'], parents=data['parents'],
                branchvalues='total', values=data['value'], marker={'colors':px.colors.qualitative.Pastel}
                )).update_traces(textinfo='label+percent parent'))

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('### No. of Chips Released Per Quartile')
            sdf = df.copy()
            sdf['quarter'] = sdf['Release Date'].dt.to_period('Q').astype(str)
            st.plotly_chart(px.histogram(
                sdf.loc[sdf['quarter'] != 'NaT'].sort_values(by=['quarter']),
                x='quarter', color='Type', barmode='overlay'))
        
        with col2:
            st.markdown('### Average Chip Frequency Per Release Date')
            gb = df.loc[df['Release Date'] != 'NaT'].groupby(
                ['Type', 'Release Date'], as_index=False)['Freq (MHz)'].mean().rename(
                    columns={'Freq (MHz)': 'Average Frequency (MHz)'})
            st.plotly_chart(px.line(gb, x='Release Date', y='Average Frequency (MHz)', color='Type', symbol='Type'))

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('### Process Size and TDP')
            sdf = df.loc[(df['Process Size (nm)'].notna()) & (df['TDP (W)'].notna())]
            st.plotly_chart(px.scatter(sdf.sort_values(by=['Process Size (nm)'], ascending=False),
                x='Process Size (nm)', y='TDP (W)', color='Type', symbol='Type',
                hover_data=['Product']))
    
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