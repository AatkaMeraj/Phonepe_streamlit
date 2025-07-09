import streamlit as st
import pandas as pd
import plotly.express as px

# ---- Title ----
st.title("PhonePe Transaction Dynamics ")

# ---- Load Data ----

agg_transaction = pd.read_csv("aggregated_transaction.csv")
map_trans_hover = pd.read_csv("map_transaction_hover.csv")
top_transaction= pd.read_csv("top_transaction.csv")
  

# ---- Preprocessing ----
agg_transaction["quarter"] = agg_transaction["month"].apply(
    lambda x: 1 if x <= 3 else 2 if x <= 6 else 3 if x <= 9 else 4
)
agg_transaction["year_quarter"] = agg_transaction["year"].astype(str) + " Q" + agg_transaction["quarter"].astype(str)

agg_transaction["Year-Month"] = pd.to_datetime(agg_transaction[["year", "month"]].assign(day=1))

# ---- -------Overall Transaction Trend Across Quarters ----
st.markdown("###  Overall Transaction Trend Across Quarters")
quarter_trend = agg_transaction.groupby("year_quarter")["amount"].sum().reset_index()
fig1 = px.line(quarter_trend, x="year_quarter", y="amount", markers=True,
               labels={"amount": "Transaction Amount", "year_quarter": "Quarter"})
st.plotly_chart(fig1, use_container_width=True)

# --------------- Total Transaction Amount by State ----
st.markdown("### Total Transaction Amount by State")
state_amount = agg_transaction.groupby("state")["amount"].sum().reset_index().sort_values(by="amount", ascending=False)
fig2 = px.bar(state_amount, x="state", y="amount", color="amount",
              labels={"amount": "Transaction Amount", "state": "State"})
st.plotly_chart(fig2, use_container_width=True)

# --------------- Total Transaction Amount by Payment Category ----
st.markdown("###  Total Transaction Amount by Payment Category")
payment_type = agg_transaction.groupby("transaction_name")["amount"].sum().reset_index().sort_values(by="amount", ascending=False)
fig3 = px.pie(payment_type, names="transaction_name", values="amount")
st.plotly_chart(fig3, use_container_width=True)

# ----------Payment Category Trend Over Time --------------
st.markdown("### Payment Category Trend Over Time")
type_time = agg_transaction.groupby(["Year-Month", "transaction_name"])["amount"].sum().reset_index()
fig4 = px.line(type_time, x="Year-Month", y="amount", color="transaction_name",
               )
st.plotly_chart(fig4, use_container_width=True)


# ----------------- Transaction Type state-wise-----------------
st.markdown("###  Transaction Type State-wise ")

# Group and normalize data
state_mix = agg_transaction.groupby(['state', 'transaction_name'])['amount'].sum().unstack().fillna(0)
state_mix_percent = state_mix.div(state_mix.sum(axis=1), axis=0)

# Sort states by dominant transaction type (max proportion)
state_mix_percent["max_type"] = state_mix_percent.max(axis=1)
state_mix_percent["dominant_type"] = state_mix_percent.idxmax(axis=1)
state_mix_percent = state_mix_percent.sort_values(by="dominant_type")

# Reset index for melting
state_mix_percent = state_mix_percent.drop(columns=["max_type", "dominant_type"]).reset_index()

# Reshape for plotting
state_mix_long = state_mix_percent.melt(id_vars='state', var_name='transaction_name', value_name='proportion')

# Add multiselect
available_states = state_mix_long["state"].unique().tolist()
default_states = available_states[:10]  # show first 10 by default
selected_states = st.multiselect("Select States to View:", options=available_states, default=default_states)

filtered_data = state_mix_long[state_mix_long["state"].isin(selected_states)]

# Plot
fig_mix = px.bar(
    filtered_data,
    x='state',
    y='proportion',
    color='transaction_name',
    labels={'proportion': 'Proportion'},
    height=600
)

fig_mix.update_layout(barmode='stack', xaxis_tickangle=-45)
st.plotly_chart(fig_mix, use_container_width=True)
