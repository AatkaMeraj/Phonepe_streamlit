import streamlit as st
import pandas as pd
import plotly.express as px

# ---- Title ----
st.title(" PhonePe User Registration Insights")

# ---- Load Data ----

aggregated_user = pd.read_csv("aggregated_user.csv")
map_user = pd.read_csv("map_user.csv")
top_user = pd.read_csv("top_user.csv")


# ---- Preprocessing ----
aggregated_user["quarter"] = aggregated_user["month"].apply(lambda x: (x - 1) // 3 + 1)
aggregated_user["year_quarter"] = aggregated_user["year"].astype(str) + " Q" + aggregated_user["quarter"].astype(str)
aggregated_user["Year-Month"] = pd.to_datetime(aggregated_user[["year", "month"]].assign(day=1))

map_user["quarter"] = aggregated_user["month"].apply(lambda x: (x - 1) // 3 + 1)
map_user["year_quarter"] = aggregated_user["year"].astype(str) + " Q" + aggregated_user["quarter"].astype(str)
map_user["Year-Month"] = pd.to_datetime(map_user[["year", "month"]].assign(day=1))

# ----Top States, Districts & Pincodes ----
st.markdown("## Top Regions by Registered Users")

region_option = st.radio("View by:", ["State", "District"], horizontal=True)

if region_option == "State":
    top_states = aggregated_user.groupby("state")["registered_users"].sum().sort_values(ascending=False).head(10).reset_index()
    fig = px.bar(top_states, x="state", y="registered_users", color="registered_users", title="Top 10 States by Registered Users")
elif region_option == "District":
    top_districts = map_user.groupby("district")["registered_users"].sum().sort_values(ascending=False).head(10).reset_index()
    fig = px.bar(top_districts, x="district", y="registered_users", color="registered_users", title="Top 10 Districts by Registered Users")


st.plotly_chart(fig, use_container_width=True)

# ----  Time-based Trends ----
st.markdown("## Registration Trend Over Time")

trend_option = st.radio("Trend Type:", ["Yearly", "Quarterly"], horizontal=True)

if trend_option == "Yearly":
    yearly = aggregated_user.groupby("year")["registered_users"].sum().reset_index()
    fig2 = px.line(yearly, x="year", y="registered_users", markers=True, title="Total Registered Users - Yearly")
else:
    quarterly = aggregated_user.groupby("year_quarter")["registered_users"].sum().reset_index()
    fig2 = px.line(quarterly, x="year_quarter", y="registered_users", markers=True, title="Total Registered Users - Quarterly")

st.plotly_chart(fig2, use_container_width=True)

# ---- Time Breakdown per Region ----
st.markdown("## Monthly/Quarterly User Breakdown per Region")

breakdown_option = st.radio("Breakdown by:", ["State", "District"], horizontal=True)
time_option = st.radio("Time View:", ["Monthly", "Quarterly"], horizontal=True)

if breakdown_option == "State":
    top_states = aggregated_user.groupby("state")["registered_users"].sum().nlargest(10).index.tolist()
    filtered = aggregated_user[aggregated_user["state"].isin(top_states)]
    group_cols = ["Year-Month" if time_option == "Monthly" else "year_quarter", "state"]
elif breakdown_option == "District":
    top_districts = map_user.groupby("district")["registered_users"].sum().nlargest(10).index.tolist()
    filtered = map_user[map_user["district"].isin(top_districts)]
    group_cols = ["Year-Month" if time_option == "Monthly" else "year_quarter", "district"]

region_trend = filtered.groupby(group_cols)["registered_users"].sum().reset_index()
fig3 = px.line(region_trend, x=group_cols[0], y="registered_users", color=group_cols[1],
               title=f"Top 10 {breakdown_option}s - {time_option} Registered User Trend")
st.plotly_chart(fig3, use_container_width=True)



# ---- Engagement Ratio (App Opens / Registered User)
st.markdown("## Engagement Ratio (App Opens/Registered User)")

engagement_view = st.radio("View Engagement Ratio by:", ["State", "District"], horizontal=True)

if engagement_view == "State":
    state_engagement = aggregated_user.groupby('state')[['registered_users', 'app_opens']].sum().reset_index()
    state_engagement = state_engagement[state_engagement['registered_users'] > 0]
    state_engagement['engagement_ratio'] = state_engagement['app_opens'] / state_engagement['registered_users']

    # Top 10 states by engagement ratio
    top_states = state_engagement.sort_values('engagement_ratio', ascending=False).head(10)

    fig = px.bar(top_states, x='engagement_ratio', y='state', 
                 color='engagement_ratio',
                 title='Top 10 States by Engagement Ratio (All Time)',
                 labels={'engagement_ratio': 'App Opens per Registered User', 'state': 'State'})
    fig.update_layout(yaxis=dict(categoryorder='total ascending'))
    st.plotly_chart(fig, use_container_width=True)

else:
    # District-level: Group by both state + district for clear labels
    district_engagement = map_user.groupby(['state', 'district'])[['registered_users', 'app_opens']].sum().reset_index()
    district_engagement = district_engagement[district_engagement['registered_users'] > 0]
    district_engagement['engagement_ratio'] = district_engagement['app_opens'] / district_engagement['registered_users']
    district_engagement['label'] = district_engagement['state'] + " - " + district_engagement['district']

    # Top 10 districts by engagement ratio
    top_districts = district_engagement.sort_values('engagement_ratio', ascending=False).head(10)

    fig = px.bar(top_districts, x='engagement_ratio', y='label', 
                 color='engagement_ratio',
                 title='Top 10 Districts by Engagement Ratio (All Time)',
                 labels={'engagement_ratio': 'App Opens per Registered User', 'label': 'District'})
    fig.update_layout(yaxis=dict(categoryorder='total ascending'))
    st.plotly_chart(fig, use_container_width=True)
