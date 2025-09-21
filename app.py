# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

#  Page configurations
st.set_page_config(
    page_title="Lebanon Tourism Infrastructure Explorer",
    page_icon="🧭",
    layout="wide",
)

#  CSS 
st.markdown(
    """
<style>
[data-testid="stAppViewContainer"] { background-color: #f7f7f9; }
h1 { text-align:center; color:#2c3e50; font-weight:700; margin-bottom:.5rem; }
h2, h3 { color:#34495e; margin-top:1.2rem; }
.kpi-card {
  background:#fff; padding:1rem; border-radius:12px;
  box-shadow:0 2px 6px rgba(0,0,0,0.1); text-align:center;
  border-left:6px solid #2c3e50; margin-bottom:1rem;
  height:130px; display:flex; flex-direction:column; justify-content:center;
}
.kpi-value { font-size:1.6rem; font-weight:700; color:#2c3e50; }
.kpi-label { font-size:.9rem; color:#7f8c8d; }

/* style checkboxes like pills */
div[data-testid="stCheckbox"] > label {
  background:#ecf0f1; border:1px solid #bdc3c7; border-radius:20px;
  padding:6px 14px; color:#2c3e50; transition:all .2s ease;
}
div[data-testid="stCheckbox"] > label:hover { background:#dfe6e9; border-color:#95a5a6; }
</style>
""",
    unsafe_allow_html=True,
)

#  Load Dataset 
df = pd.read_csv("lebanon_tourism.csv")
df.columns = df.columns.str.strip()

num_cols = [
    "Total number of hotels",
    "Total number of cafes",
    "Total number of guest houses",
    "Total number of restaurants",
]
for c in num_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

df["Area"] = df["refArea"].astype(str).str.extract(r"([^/]+)$")[0].str.replace("_", " ", regex=False)
df["Level"] = df["Area"].str.contains("Governorate", case=False).map(
    {True: "Governorate", False: "District"}
)
df["Total"] = df[num_cols].sum(axis=1)

#  Header 
st.markdown(
    """
    <h1 style="text-align:center;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/5/59/Flag_of_Lebanon.svg"
             width="40" style="vertical-align:middle; margin-right:10px;">
        Lebanon Tourism Infrastructure Explorer
    </h1>
    """,
    unsafe_allow_html=True,
)

st.subheader(" Dataset Summary")
st.markdown(
    f"""
This dataset contains **{df.shape[0]:,} rows** and **{df.shape[1]:,} columns**.  
It includes the number of **hotels, cafes, guest houses, and restaurants** across Lebanon’s **governorates and districts**.  
Each row represents an area with a breakdown of facility counts and a computed total.
"""
)

st.divider()

#  cards kpi
gov = (
    df[df["Level"] == "Governorate"]
    .groupby("Area", as_index=False)
    .agg(Total=("Total", "sum"))
    .sort_values("Total", ascending=False)
)
dist = (
    df[df["Level"] == "District"]
    .groupby("Area", as_index=False)
    .agg(Total=("Total", "sum"))
    .sort_values("Total", ascending=False)
)

avg_gov = int(df[df["Level"] == "Governorate"].groupby("Area")["Total"].sum().mean())
avg_dist = int(df[df["Level"] == "District"].groupby("Area")["Total"].sum().mean())

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        f"""
<div class="kpi-card">
  <div class="kpi-value">{int(df['Total'].sum()):,}</div>
  <div class="kpi-label"> Total Facilities</div>
</div>
""",
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        f"""
<div class="kpi-card">
  <div style="display:flex; justify-content:space-around; gap:1rem;">
    <div>
      <div class="kpi-label"> Top Governorate</div>
      <div class="kpi-value">{gov.iloc[0]['Area']}</div>
    </div>
    <div>
      <div class="kpi-label"> Top District</div>
      <div class="kpi-value">{dist.iloc[0]['Area']}</div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        f"""
<div class="kpi-card">
  <div class="kpi-value">{avg_gov:,}</div>
  <div class="kpi-label"> Avg facilities per Governorate</div>
</div>
""",
        unsafe_allow_html=True,
    )

with c4:
    st.markdown(
        f"""
<div class="kpi-card">
  <div class="kpi-value">{avg_dist:,}</div>
  <div class="kpi-label"> Avg facilities per District</div>
</div>
""",
        unsafe_allow_html=True,
    )

st.divider()

#  Visualization 1 
st.subheader("Visualization 1 — Total Tourism Infrastructure by Area")

level_choice = st.radio(
    "Administrative level",
    ["All", "Governorates", "Districts"],
    index=0,
    key="chart1_level"
)

if level_choice == "Governorates":
    df_level = df[df["Level"] == "Governorate"].groupby("Area", as_index=False)["Total"].sum()
elif level_choice == "Districts":
    df_level = df[df["Level"] == "District"].groupby("Area", as_index=False)["Total"].sum()
else:
    df_level = df.groupby("Area", as_index=False)["Total"].sum()

df_level = df_level.sort_values("Total", ascending=False)

fig1 = px.bar(
    df_level,
    x="Area",
    y="Total",
    color="Total",
    color_continuous_scale="Viridis",
    title=f"Total Tourism Infrastructure ({level_choice})",
)
fig1.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig1, use_container_width=True)

# ---- Insights for Chart 1 ----
st.markdown("### 🔍 Insights from Chart 1")

col_left, col_right = st.columns(2)

with col_left:
    highest_district = dist.iloc[0]
    lowest_district = dist.iloc[-1]
    gap_districts = int(highest_district["Total"] - lowest_district["Total"])
    st.write(f"- **Highest District:** {highest_district['Area']} — **{int(highest_district['Total']):,}** facilities")
    st.write(f"- **Lowest District:** {lowest_district['Area']} — **{int(lowest_district['Total']):,}** facilities")
    st.write(f"- **Gap (Districts):** {gap_districts:,} facilities")

with col_right:
    highest_gov = gov.iloc[0]
    lowest_gov = gov.iloc[-1]
    gap_governorates = int(highest_gov["Total"] - lowest_gov["Total"])
    st.write(f"- **Highest Governorate:** {highest_gov['Area']} — **{int(highest_gov['Total']):,}** facilities")
    st.write(f"- **Lowest Governorate:** {lowest_gov['Area']} — **{int(lowest_gov['Total']):,}** facilities")
    st.write(f"- **Gap (Governorates):** {gap_governorates:,} facilities")

st.write(
    "- There is a significant regional disparity between governorates and districts, "
    "where tourism infrastructure in some areas is heavily concentrated, while in others it remains very limited, "
    "highlighting the imbalance in tourism development across Lebanon."
)

st.divider()

#  Visualization 2 
st.subheader("Visualization 2 — Tourism Facilities Breakdown by Type")

colA, colB, colC = st.columns([1, 2, 1])

with colA:
    level_choice2 = st.radio(
        "Administrative level",
        ["All", "Governorates", "Districts"],
        index=0,
        key="chart2_level"
    )

with colB:
    pretty = {
        "Total number of hotels": "Hotels",
        "Total number of cafes": "Cafes",
        "Total number of guest houses": "Guest houses",
        "Total number of restaurants": "Restaurants",
    }
    all_pretty = [pretty[c] for c in num_cols]

    st.markdown("**Facility types**")
    chosen_pretty = []
    cols = st.columns(len(all_pretty))
    for i, opt in enumerate(all_pretty):
        if cols[i].checkbox(opt, value=True, key=f"ft_{opt}"):
            chosen_pretty.append(opt)

    selected_cols = [k for k, v in pretty.items() if v in chosen_pretty]

with colC:
    chart_mode = st.radio(
        "Chart mode",
        ["Stacked", "Grouped"],
        index=0,
        key="chart2_mode"
    )

if selected_cols:
    if level_choice2 == "Governorates":
        df2 = df[df["Level"] == "Governorate"]
    elif level_choice2 == "Districts":
        df2 = df[df["Level"] == "District"]
    else:
        df2 = df

    agg = df2.groupby("Area", as_index=False)[selected_cols].sum()
    long_df = agg.melt(
        id_vars="Area",
        value_vars=selected_cols,
        var_name="Facility_Type",
        value_name="Count",
    )
    long_df["Facility_Type"] = long_df["Facility_Type"].map(pretty)

    order = long_df.groupby("Area")["Count"].sum().sort_values(ascending=False).index

    custom_colors = {
        "Hotels": "#1f77b4",
        "Cafes": "#2ca02c",
        "Guest houses": "#ff7f0e",
        "Restaurants": "#d62728",
    }

    fig2 = px.bar(
        long_df,
        x="Area",
        y="Count",
        color="Facility_Type",
        title=f"Tourism Facilities Breakdown by Type ({level_choice2})",
        category_orders={"Area": list(order)},
        barmode="stack" if chart_mode == "Stacked" else "group",
        color_discrete_map=custom_colors,
    )
    fig2.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig2, use_container_width=True)

    # ---- Dynamic Insights for Chart 2 (3 insights only) ----
    st.markdown("### 🔎 Insights from Chart 2")

    totals_by_type = long_df.groupby("Facility_Type")["Count"].sum().sort_values(ascending=False)

    if not totals_by_type.empty:
        top_type = totals_by_type.index[0]
        top_share = 100 * totals_by_type.iloc[0] / totals_by_type.sum()

        if len(totals_by_type) > 1:
            second_type = totals_by_type.index[1]
            second_share = 100 * totals_by_type.iloc[1] / totals_by_type.sum()
        else:
            second_type, second_share = None, None

        st.write(f"- **{top_type}** are the most common, making up **{top_share:.1f}%** of selected facilities.")
        if second_type:
            st.write(f"- **{second_type}** are the second most common, accounting for **{second_share:.1f}%**.")
        st.write(f"- **{top_type} alone** account for nearly **{top_share:.1f}%** of all selected facilities.")
    else:
        st.info("No facilities to analyze with the current filters.")
else:
    st.warning("⚠️ Select at least one facility type to display Chart 2.")

