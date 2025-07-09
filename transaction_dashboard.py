import streamlit as st
import pandas as pd
import plotly.express as px

agg_transaction = pd.read_csv("aggregated_transaction.csv")
map_trans_hover = pd.read_csv("map_transaction_hover.csv")


# Create Quarter column
agg_transaction["quarter"] = agg_transaction["month"].apply(
    lambda x: 1 if x <= 3 else 2 if x <= 6 else 3 if x <= 9 else 4
)

# Title
st.title("PhonePe Transaction by State & District Dashboard")


# Preprocessing
agg_transaction['Year-Month'] = pd.to_datetime(agg_transaction[['year', 'month']].assign(day=1))
state_data = agg_transaction.groupby(['state', 'year', 'month', 'type']).agg({'amount': 'sum', 'count': 'sum'}).reset_index()

map_trans_hover['Year-Month'] = pd.to_datetime(map_trans_hover[['year', 'month']].assign(day=1))
district_data = map_trans_hover[map_trans_hover['district'].notna()]



# ----------------- Top States -----------------
st.markdown("###  Top 10 States by Transaction Amount")
top_states = agg_transaction.groupby('state')['amount'].sum().nlargest(10).reset_index()
fig1 = px.bar(top_states, x='state', y='amount', color='amount', title="Top 10 States by Transaction Amount",
              labels={'amount': 'Transaction Amount', 'state': 'State'})
st.plotly_chart(fig1, use_container_width=True)

# ----------------- Top Districts -----------------
st.markdown("###  Top 10 Districts by Transaction Amount")
top_districts = district_data.groupby('district')['amount'].sum().nlargest(10).reset_index()
fig2 = px.bar(top_districts, x='district', y='amount', color='amount', title="Top 10 Districts by Transaction Amount",
              labels={'amount': 'Transaction Amount', 'district': 'District'})
st.plotly_chart(fig2, use_container_width=True)

# ----------------- Transaction amount by State -----------------
st.markdown("###  Transaction Amount Comparison by State")
selected_states = st.multiselect("Select States", options=agg_transaction['state'].unique(), default=['Maharashtra', 'Karnataka'])
type_df = agg_transaction[agg_transaction['state'].isin(selected_states)].groupby(['state', 'type'])['amount'].sum().reset_index()
fig3 = px.bar(type_df, x='state', y='amount', color='type', barmode='stack',
              title="Transaction Amount Comparison by State")
st.plotly_chart(fig3, use_container_width=True)

# ----------------- Trend Over Time -----------------
st.markdown("###  Transaction Trend Over Time")

tab1, tab2 = st.tabs(["Top 5 States", "Top 5 Districts"])

with tab1:
    top5_states = agg_transaction.groupby('state')['amount'].sum().nlargest(5).index.tolist()
    state_trend = agg_transaction[agg_transaction['state'].isin(top5_states)].groupby(['Year-Month', 'state'])['amount'].sum().reset_index()
    fig4 = px.line(state_trend, x='Year-Month', y='amount', color='state',
                   title="Transaction Trend Over Time - Top 5 States")
    st.plotly_chart(fig4, use_container_width=True)

with tab2:
    top5_districts = map_trans_hover.groupby('district')['amount'].sum().nlargest(5).index.tolist()
    dist_trend = map_trans_hover[map_trans_hover['district'].isin(top5_districts)].groupby(['Year-Month', 'district'])['amount'].sum().reset_index()
    fig5 = px.line(dist_trend, x='Year-Month', y='amount', color='district',
                   title="Transaction Trend Over Time - Top 5 Districts")
    st.plotly_chart(fig5, use_container_width=True)

# ----------------- Monthly Transaction Volume -----------------
st.markdown("### Total Monthly Transaction Trend")
monthly = agg_transaction.groupby('Year-Month').agg({'count': 'sum'}).reset_index()
fig6 = px.area(monthly, x='Year-Month', y='count',
               title='Total Monthly Transaction Volume',
               labels={'count': 'Transaction Count'})
st.plotly_chart(fig6, use_container_width=True)
