import pandas as pd
import numpy as np
import streamlit as st
import altair as alt
import plotly_express as px
location = 'IQVIA_Thailand total market_2024.02.01.xlsx'
df = pd.read_excel(location)
df.drop(34191,inplace=True)
df.columns = ['country','sector','prescription','manufacturer','brand','drug','su2020','usd2020','su2021','usd2021','su2022','usd2022']
df = df[['country','sector','prescription','manufacturer','brand','drug','su2020','su2021','su2022','usd2020','usd2021','usd2022']]
df = df[df.prescription == 'PRESCRIPTION BOUND']
df['cagr'] = np.sqrt(df['usd2022']/df['usd2020'])
df.reset_index(drop=True,inplace=True)
df_drug_group = df[['drug','usd2020','usd2021','usd2022']].groupby('drug').sum().reset_index()
list_drug_group_cagr = []
for i in range(len(df_drug_group)):
    if df_drug_group['usd2020'][i] == 0 and df_drug_group['usd2021'][i] == 0:
        list_drug_group_cagr.append(0)
    elif df_drug_group['usd2020'][i] == 0 and df_drug_group['usd2021'][i] != 0:
        list_drug_group_cagr.append(df_drug_group['usd2022'][i]/df_drug_group['usd2021'][i])
    else:
        list_drug_group_cagr.append(np.sqrt(df_drug_group['usd2022'][i]/df_drug_group['usd2020'][i]))
df_drug_group['cagr'] = list_drug_group_cagr
st.set_page_config(
    page_title='IMS IQVIA Thai Pharmaceutical Market',
    layout='wide',
    initial_sidebar_state='expanded')
alt.themes.enable('dark')
with st.sidebar:
    st.title('Total market')
    st.selectbox('Country:',['THAILAND'])
    drug_list = [i for i in df['drug'].unique()]
    selected_drug = st.selectbox('select a drug',drug_list)
    df_drug = df[df['drug']== selected_drug]
    st.selectbox('[Example function]: Please specify Disease',['Metabolism','Blood','Cardiovascular','Dermatology','GI','GU','...'])
col = st.columns((3,2),gap ='medium')
def quickcagr(df,drug):
    cagr = np.sqrt((df[df['drug'] == drug]['usd2022'].sum()/df[df['drug'] == drug]['usd2020'].sum()))
    return cagr
with col[0]:
    df_drug_total = df_drug[['drug','usd2020','usd2021','usd2022']].groupby('drug').sum()
    df_drug_total_long = df_drug_total.T
    st.markdown('General Total Market situation')
    st.metric(label='Latest market value (2022,USD)',value='{:0,.0f}'.format(df_drug['usd2022'].sum()),delta='{:.3f}%'.format((quickcagr(df_drug,selected_drug)-1)*100))
    st.plotly_chart(px.line(df_drug_total_long,x=df_drug_total_long.index,y=selected_drug,markers=True,height=300,width=450))
    selected_filter = st.selectbox('Filtering:',['Top 5 highest CAGR','Top 5 Values in USD in 2022'])
    if selected_filter == 'Top 5 highest CAGR':
        df_drug_group.sort_values('cagr',ascending=False,inplace=True)
        df_drug_group_filter = df_drug_group.iloc[:5]
    else:
        df_drug_group.sort_values('usd2022',ascending=False,inplace=True)
        df_drug_group_filter = df_drug_group.iloc[:5]
    st.dataframe(df_drug_group_filter,column_order=('drug','usd2020','usd2021','usd2022','cagr'),
                 hide_index=True,
                 width=None,
                 column_config={
                     'drug':st.column_config.TextColumn('Drug'),
                     'usd2020':st.column_config.TextColumn('USD in 2020'),
                     'usd2021':st.column_config.TextColumn('USD in 2021'),
                     'usd2022':st.column_config.TextColumn('USD in 2022'),
                     'cagr':st.column_config.TextColumn('CAGR')
                 })
    st.markdown('By sector situation. Please select market sector')
    selected_sector = st.selectbox('select sector',['TOTAL','HOSPITAL','RETAIL'])
    if selected_sector == 'TOTAL':
        df_drug_sector = df[df['drug'] == selected_drug]
    else:
        df_sector = df[df['sector'] == selected_sector]
        df_drug_sector = df_sector[df_sector['drug'] == selected_drug]
    df_drug_sector_total = df_drug_sector[['drug','usd2020','usd2021','usd2022']].groupby('drug').sum()
    df_drug_sector_total_long = df_drug_sector_total.T
    st.metric(label='Latest market value (2022,USD)',value='{:0,.0f}'.format(df_drug_sector['usd2022'].sum()),delta='{:.3f}%'.format((quickcagr(df_drug_sector,selected_drug)-1)*100))
    st.plotly_chart(px.line(df_drug_sector_total_long,x=df_drug_sector_total_long.index,y=selected_drug,markers=True,height=300,width=450))
with col[1]:
    st.markdown('In-depth market details')
    df_drug_brand = df_drug_sector[['brand','usd2020','usd2021','usd2022']].groupby('brand').sum().reset_index()
    selected_year = st.selectbox('Select interested year',['2022','2021','2020'])
    fig = px.pie(df_drug_brand,values='usd'+selected_year,names='brand',hole=0.3)
    fig.update_traces(textposition='inside')
    st.plotly_chart(fig)
    st.dataframe(df_drug_brand.describe(),column_order=('usd2020','usd2021','usd2022'),
                 column_config={
                     'usd2020':st.column_config.TextColumn('USD in 2020'),
                     'usd2021':st.column_config.TextColumn('USD in 2021'),
                     'usd2022':st.column_config.TextColumn('USD in 2022'),
                 })
    