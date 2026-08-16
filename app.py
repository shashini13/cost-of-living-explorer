import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="Cost of Living Explorer", page_icon="🌍", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("cost_of_living_clean.csv")

@st.cache_data(ttl=3600)
def get_exchange_rates():
    try:
        response = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5)
        data = response.json()
        if data['result'] == 'success':
            return data['rates'], data['time_last_update_utc']
    except Exception:
        pass
    return None, None

df = load_data()
rates, last_updated = get_exchange_rates()

st.title("🌍 Cost of Living Explorer")
st.write(
    "Compare the cost of living across 95 countries. Data sourced from the World Bank "
    "International Comparison Program (ICP) 2021, via WhereNext (CC BY 4.0)."
)
st.markdown("---")

st.sidebar.header("Explore Options")

currency_options = ["USD"] + sorted(rates.keys()) if rates else ["USD"]
selected_currency = st.sidebar.selectbox(
    "Display currency", currency_options,
    index=currency_options.index("LKR") if "LKR" in currency_options else 0
)

if rates and selected_currency != "USD":
    conversion_rate = rates[selected_currency]
    st.sidebar.caption(f"1 USD = {conversion_rate:,.2f} {selected_currency}")
    st.sidebar.caption(f"Rates updated: {last_updated}")
else:
    conversion_rate = 1

def convert(usd_amount):
    return usd_amount * conversion_rate

def format_currency(usd_amount):
    converted = convert(usd_amount)
    return f"${converted:,.0f}" if selected_currency == "USD" else f"{converted:,.0f} {selected_currency}"

view_mode = st.sidebar.radio(
    "Choose a view",
    ["Single Country", "Compare Countries", "Rankings", "World Map", "Budget Finder"]
)

# --- SINGLE COUNTRY VIEW ---
if view_mode == "Single Country":
    country = st.selectbox("Select a country", sorted(df['country'].unique()))
    row = df[df['country'] == country].iloc[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Monthly Cost", format_currency(row['monthly_estimate_usd']))
    col2.metric("Cost Rank", f"#{int(row['rank'])} of 95")
    col3.metric("Region", row['region'])

    st.subheader(f"Affordability breakdown for {country}")
    st.caption("Higher score = more affordable, relative to other countries (0-100 scale)")

    breakdown = pd.DataFrame({
        "Category": ["Groceries", "Rent", "Utilities", "Transport"],
        "Affordability Score": [row['grocery_index'], row['rent_index'],
                                  row['utilities_index'], row['transport_index']]
    })
    fig = px.bar(breakdown, x="Category", y="Affordability Score", color="Category",
                 range_y=[0, 100], title=f"{country} — Affordability by Category")
    st.plotly_chart(fig, use_container_width=True)

# --- COMPARE COUNTRIES VIEW ---
elif view_mode == "Compare Countries":
    countries = st.multiselect(
        "Select countries to compare (2-5 recommended)",
        sorted(df['country'].unique()),
        default=["Sri Lanka", "United Kingdom", "Australia"]
    )
    if countries:
        comparison = df[df['country'].isin(countries)].copy()
        comparison['display_cost'] = comparison['monthly_estimate_usd'].apply(convert)

        fig1 = px.bar(comparison, x="country", y="display_cost", color="country",
                      title=f"Monthly Cost of Living Comparison ({selected_currency})",
                      labels={"display_cost": f"Monthly Cost ({selected_currency})", "country": "Country"})
        st.plotly_chart(fig1, use_container_width=True)

        melted = comparison.melt(
            id_vars=["country"],
            value_vars=["grocery_index", "rent_index", "utilities_index", "transport_index"],
            var_name="Category", value_name="Affordability Score"
        )
        melted["Category"] = melted["Category"].str.replace("_index", "").str.title()

        fig2 = px.bar(melted, x="Category", y="Affordability Score", color="country",
                      barmode="group", range_y=[0, 100], title="Affordability Breakdown by Category")
        st.plotly_chart(fig2, use_container_width=True)

        display_table = comparison[['country', 'region', 'display_cost', 'grocery_index',
                                      'rent_index', 'utilities_index', 'transport_index']].copy()
        display_table = display_table.rename(columns={'display_cost': f'Monthly Cost ({selected_currency})'})
        st.dataframe(display_table, use_container_width=True, hide_index=True)
    else:
        st.info("Select at least one country above to see the comparison.")

# --- RANKINGS VIEW ---
elif view_mode == "Rankings":
    region_options = ["All"] + sorted(df['region'].unique().tolist())
    region_filter = st.selectbox("Filter by region", region_options)
    top_n = st.slider("Number of countries to show", 5, 30, 10)
    sort_order = st.radio("Sort order", ["Cheapest first", "Most expensive first"])

    data = df.copy()
    if region_filter != "All":
        data = data[data['region'] == region_filter]

    ascending = sort_order == "Cheapest first"
    data = data.sort_values('monthly_estimate_usd', ascending=ascending).head(top_n)
    data['display_cost'] = data['monthly_estimate_usd'].apply(convert)

    fig = px.bar(data, x="display_cost", y="country", orientation="h",
                 title=f"{'Cheapest' if ascending else 'Most Expensive'} {top_n} Countries"
                       f"{' in ' + region_filter if region_filter != 'All' else ''} ({selected_currency})",
                 labels={"display_cost": f"Monthly Cost ({selected_currency})", "country": "Country"})
    fig.update_layout(yaxis={'categoryorder': 'total ascending' if ascending else 'total descending'})
    st.plotly_chart(fig, use_container_width=True)

# --- WORLD MAP VIEW ---
elif view_mode == "World Map":
    st.subheader("Cost of Living Around the World")

    with st.expander("ℹ️ What am I looking at?"):
        st.write(
            "This globe shows the **estimated monthly cost of living for one person** "
            "(rent, groceries, utilities, and transport combined) in each country. "
            "**Darker red = more expensive**, **lighter yellow = more affordable**. "
            "Click and drag the globe to rotate it, scroll to zoom, and hover over any "
            "country to see its exact estimated monthly cost."
        )

    map_df = df.copy()
    map_df['display_cost'] = map_df['monthly_estimate_usd'].apply(convert)

    fig = px.choropleth(
        map_df,
        locations="country",
        locationmode="country names",
        color="monthly_estimate_usd",
        hover_name="country",
        hover_data={"display_cost": ":,.0f", "monthly_estimate_usd": False},
        color_continuous_scale="YlOrRd",
        title="Estimated Monthly Cost of Living",
        labels={"monthly_estimate_usd": "Cost (USD)", "display_cost": f"Cost ({selected_currency})"}
    )
    fig.update_geos(projection_type="orthographic", showcountries=True)
    fig.update_layout(height=600, margin={"r": 0, "t": 40, "l": 0, "b": 0})
    st.plotly_chart(fig, use_container_width=True)

# --- BUDGET FINDER VIEW ---
else:
    st.subheader("Find Countries Within Your Budget")

    default_budget = int(convert(1500))
    budget = st.number_input(
        f"Your monthly budget ({selected_currency})",
        min_value=0, value=default_budget, step=int(convert(50)) or 1
    )

    budget_in_usd = budget / conversion_rate
    affordable = df[df['monthly_estimate_usd'] <= budget_in_usd].copy()
    affordable['display_cost'] = affordable['monthly_estimate_usd'].apply(convert)
    affordable = affordable.sort_values('monthly_estimate_usd')

    st.write(f"**{len(affordable)} of 95 countries** fit within a budget of "
             f"{budget:,.0f} {selected_currency}/month.")

    if len(affordable) > 0:
        fig = px.bar(affordable, x="display_cost", y="country", orientation="h",
                     color="region", title="Countries Within Your Budget",
                     labels={"display_cost": f"Monthly Cost ({selected_currency})", "country": "Country"},
                     height=max(400, len(affordable) * 20))
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No countries fit within this budget. Try increasing it.")

st.markdown("---")
st.caption(
    "Data: WhereNext Cost of Living Index 2026, derived from World Bank ICP 2021 Price Level "
    "Indices. Licensed CC BY 4.0. Exchange rates via the ExchangeRate-API open access endpoint "
    "(exchangerate-api.com). Figures are country-level averages calibrated to a single-person "
    "household and may not reflect city-specific or individual circumstances."
)
