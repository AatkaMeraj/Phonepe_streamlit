import streamlit as st
import pandas as pd
import plotly.express as px


# --- Load Data ---
aggregated_insurance = pd.read_csv("aggregated_insurance.csv")
aggregated_transaction = pd.read_csv("aggregated_transaction.csv")
map_insurance_hover = pd.read_csv("map_insurance_hover.csv")
map_transaction_hover = pd.read_csv("map_transaction_hover.csv")
top_insurance = pd.read_csv("top_insurance.csv")

# --- Preprocess ---
for df in [aggregated_insurance, aggregated_transaction, map_insurance_hover, top_insurance]:
    df["Year-Month"] = pd.to_datetime(df[["year", "month"]].assign(day=1))

aggregated_transaction_state = aggregated_transaction.groupby(['state', 'year', 'month'])[['amount']].sum().reset_index()
aggregated_insurance_state = aggregated_insurance.groupby(['state', 'year', 'month'])[['amount']].sum().reset_index()

# --- Tabs ---
tab1, tab2, tab3, tab4 = st.tabs([
    "Top Insurance States",
    "Insurance Growth Over Time",
    "State vs District View",
    "Insurance Intensity Analysis"
])

# ---Insurance Penetration ---
with tab1:
    st.subheader(" Top States by Insurance Penetration")

    # Merge for penetration ratio
    penetration_df = pd.merge(
        aggregated_transaction_state,
        aggregated_insurance_state,
        on=["state", "year", "month"],
        suffixes=('_txn', '_ins')
    )

    # Calculate penetration (total insurance / total transaction)
    pen_ratio = penetration_df.groupby('state')[['amount_txn', 'amount_ins']].sum().reset_index()
    pen_ratio['penetration'] = (pen_ratio['amount_ins'] / pen_ratio['amount_txn']) * 100
    top_states = pen_ratio.sort_values("penetration", ascending=False).head(10)

    fig1 = px.bar(top_states, x="state", y="penetration", color="penetration",
                  labels={"penetration": "Penetration (%)"})
    st.plotly_chart(fig1, use_container_width=True)

# --- Insurance Growth Over Time ---
with tab2:
    st.subheader("Insurance Transaction Growth Over Time")

    growth_trend = aggregated_insurance.groupby("Year-Month")["amount"].sum().reset_index()

    fig2 = px.line(growth_trend, x="Year-Month", y="amount",
                   title="Insurance Transactions Over Time (India-wide)",
                   labels={"amount": "Insurance Amount (₹)"})
    st.plotly_chart(fig2, use_container_width=True)

# ---  Top 10 States & Districts ---
with tab3:
    view_option = st.radio("View Top 10 By:", ["State", "District"], horizontal=True)

    if view_option == "State":
        state_top = aggregated_insurance.groupby("state")["amount"].sum().nlargest(10).reset_index()
        fig3 = px.bar(state_top, x="state", y="amount", color="amount",
                      title="Top 10 States by Insurance Amount")
        st.plotly_chart(fig3, use_container_width=True)

    else:
        district_top = map_insurance_hover.groupby("district")["amount"].sum().nlargest(10).reset_index()
        fig4 = px.bar(district_top, x="district", y="amount", color="amount",
                      title="Top 10 Districts by Insurance Amount")
        st.plotly_chart(fig4, use_container_width=True)

# ---  Insurance Intensity Analysis ---
with tab4:
    st.subheader("Insurance Intensity Analysis")

    intensity_view = st.radio("View by:", ["State", "District"], horizontal=True)

    if intensity_view == "State":
        total_txn_amt = aggregated_transaction.groupby('state')["amount"].sum().reset_index()
        total_ins_amt = aggregated_insurance.groupby('state')["amount"].sum().reset_index()

        merged_txn = pd.merge(total_txn_amt, total_ins_amt, on="state", how="left", suffixes=("_txn", "_ins"))
        merged_txn["insurance_intensity"] = (merged_txn["amount_ins"] / merged_txn["amount_txn"]) * 100
        merged_txn = merged_txn.dropna().sort_values("insurance_intensity", ascending=False).head(10)

        fig5 = px.bar(merged_txn, x="state", y="insurance_intensity", color="insurance_intensity",
                      title="Top States by Insurance Intensity (%)",
                      labels={"insurance_intensity": "Insurance Share of All Transactions"})
        st.plotly_chart(fig5, use_container_width=True)

    else:
            # Get insurance amount per district
        district_ins = map_insurance_hover.groupby("district")["amount"].sum().reset_index(name="amount_ins")
        district_txn = map_transaction_hover.groupby("district")["amount"].sum().reset_index(name="amount_txn")

# Merge and calculate intensity
        district_merged = pd.merge(district_txn, district_ins, on="district", how="inner")
        district_merged["insurance_intensity"] = (district_merged["amount_ins"] / district_merged["amount_txn"]) * 100
        district_merged = district_merged.dropna().sort_values("insurance_intensity", ascending=False).head(10)

# Plot
        fig6 = px.bar(district_merged, x="district", y="insurance_intensity", color="insurance_intensity",
              title="Top Districts by Insurance Intensity (%)",
              labels={"insurance_intensity": "Insurance Share of Transactions"})
        st.plotly_chart(fig6, use_container_width=True)

      
