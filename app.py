# =============================================================================
#  BOKKU MART — GROCERY SALES INTELLIGENCE DASHBOARD
#  Version 3.0 — Full rewrite: all bugs fixed, improved layout & hero section
# =============================================================================
#  QUICK START:
#    1.  pip install streamlit pandas plotly openpyxl
#    2.  Put app.py, bokku_mart_grocery_sales_dataset_500.xlsx,
#        and bokku_mart_grocery_sales_dataset.png in the SAME folder
#    3.  streamlit run app.py
#    4.  Open http://localhost:8501
# =============================================================================

import os
import base64
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# 1. PAGE CONFIG  (must be the very first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bokku Mart | Sales Intelligence",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# 2. BRAND PALETTE
# ─────────────────────────────────────────────────────────────────────────────
C_ROYAL  = "rgb(0, 29, 221)"
C_DEEP   = "rgb(0, 22, 180)"
C_PANEL  = "rgb(0, 18, 160)"
C_YELLOW = "rgb(255, 238, 1)"
C_WHITE  = "rgb(255, 255, 255)"
C_GRAY   = "rgb(200, 210, 255)"

CHART_PALETTE = [
    "#FFEE01", "#FFFFFF", "#FFD700", "#6B8FFF",
    "#FFC300", "#A9C4FF", "#FFF176", "#3A5BCC",
    "#E0E0E0", "#FF6B6B",
]
STATUS_COLORS = {"Completed": "#FFEE01", "Pending": "#6B8FFF", "Returned": "#FF6B6B"}

# ─────────────────────────────────────────────────────────────────────────────
# 3. GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
html, body, [data-testid="stAppViewContainer"], .stApp {{
    background-color: {C_ROYAL} !important;
    font-family: 'Segoe UI', Arial, sans-serif;
}}
.block-container {{
    padding: 4rem 1.8rem 1.5rem 1.8rem !important;
    max-width: 100% !important;
}}
section[data-testid="stSidebar"] {{
    background-color: {C_ROYAL} !important;
    border-right: 2px solid {C_YELLOW};
    padding-top: 0 !important;
}}
section[data-testid="stSidebar"] * {{
    color: {C_WHITE} !important;
}}
*, p, h1, h2, h3, h4, h5, h6, label, span, div, li {{
    color: {C_WHITE} !important;
}}
[data-testid="stMetric"] {{
    background-color: {C_DEEP} !important;
    border: 1.5px solid {C_YELLOW} !important;
    border-radius: 10px !important;
    padding: 14px 16px !important;
}}
[data-testid="stMetricLabel"] > div {{
    color: {C_YELLOW} !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}}
[data-testid="stMetricValue"] > div {{
    color: {C_WHITE} !important;
    font-size: 1.4rem !important;
    font-weight: 800 !important;
}}
div[data-baseweb="select"] > div,
div[data-baseweb="popover"] {{
    background-color: {C_DEEP} !important;
    border-color: {C_YELLOW} !important;
    border-radius: 6px !important;
}}
.stSelectbox label, .stMultiSelect label, .stDateInput label {{
    color: {C_YELLOW} !important;
    font-weight: 700 !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}}
div[data-testid="stDateInput"] input {{
    background-color: {C_DEEP} !important;
    color: {C_WHITE} !important;
    border-color: {C_YELLOW} !important;
}}
span[data-baseweb="tag"] {{
    background-color: {C_YELLOW} !important;
    color: rgb(0,18,160) !important;
}}
span[data-baseweb="tag"] span {{
    color: rgb(0,18,160) !important;
}}
details {{
    background-color: {C_DEEP} !important;
    border: 1.5px solid {C_YELLOW} !important;
    border-radius: 10px !important;
    padding: 4px 8px !important;
}}
details summary {{
    color: {C_YELLOW} !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    cursor: pointer;
}}
hr {{
    border: none !important;
    border-top: 1.5px solid {C_YELLOW} !important;
    margin: 8px 0 12px 0 !important;
    opacity: 0.4;
}}
.js-plotly-plot {{
    border-radius: 10px !important;
    border: 1px solid rgba(255,238,1,0.2) !important;
}}
::-webkit-scrollbar {{ width: 5px; }}
::-webkit-scrollbar-track {{ background: {C_ROYAL}; }}
::-webkit-scrollbar-thumb {{ background: {C_YELLOW}; border-radius: 3px; }}
.stButton > button {{
    background-color: {C_YELLOW} !important;
    color: {C_PANEL} !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 6px !important;
}}
.sb-label {{
    color: {C_YELLOW} !important;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin: 14px 0 3px 0;
    opacity: 0.9;
}}
.sec-hdr {{
    color: {C_YELLOW} !important;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    border-bottom: 1px solid rgba(255,238,1,0.3);
    padding-bottom: 4px;
    margin: 0 0 10px 0;
}}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 4. LOGO LOADER  — cached + absolute path + auto MIME detection
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_logo():
    """
    Loads the logo image ONCE and caches it permanently for the session.
    Uses __file__ so the absolute path never depends on cwd.
    Reads magic bytes to detect JPEG vs PNG regardless of file extension.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        "bokku_mart_grocery_sales_dataset.png",
        "bokku_mart_grocery_sales_dataset.jpg",
        "bokku_mart_grocery_sales_dataset.jpeg",
        "logo.png", "logo.jpg",
    ]
    for name in candidates:
        for fpath in [os.path.join(script_dir, name), name]:
            if os.path.exists(fpath):
                raw = open(fpath, "rb").read()
                b64 = base64.b64encode(raw).decode()
                mime = (
                    "image/jpeg" if raw[:3] == b"\xff\xd8\xff" else
                    "image/png"  if raw[:4] == b"\x89PNG" else
                    "image/jpeg"
                )
                return b64, mime
    return None, None


# ─────────────────────────────────────────────────────────────────────────────
# 5. DATA LOADING & PREPROCESSING  — cached
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    xl_name    = "bokku_mart_grocery_sales_dataset_500.xlsx"
    xl_path    = os.path.join(script_dir, xl_name)
    if not os.path.exists(xl_path):
        xl_path = xl_name

    df = pd.read_excel(xl_path, engine="openpyxl")

    # Strip whitespace from all string columns
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].astype(str).str.strip()

    # Safe date parse
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")

    # Derived metrics
    df["Profit_NGN"] = (
        df["Total_Revenue_NGN"] - df["Purchase_Cost_NGN"] * df["Quantity_Sold"]
    )
    df["Gross_Margin_Pct"] = df.apply(
        lambda r: (r["Profit_NGN"] / r["Total_Revenue_NGN"] * 100)
        if pd.notna(r["Total_Revenue_NGN"]) and r["Total_Revenue_NGN"] != 0 else None,
        axis=1,
    )

    def _tier(m):
        if pd.isna(m):  return "Unknown"
        if m > 30:      return "High"
        if m >= 10:     return "Medium"
        return "Low"
    df["Profitability_Tier"] = df["Gross_Margin_Pct"].apply(_tier)

    df["Unit_Margin_NGN"] = df["Retail_Price_NGN"] - df["Purchase_Cost_NGN"]
    df["Revenue_Per_Unit"] = df.apply(
        lambda r: r["Total_Revenue_NGN"] / r["Quantity_Sold"]
        if pd.notna(r["Quantity_Sold"]) and r["Quantity_Sold"] != 0 else None,
        axis=1,
    )
    df["Is_Returned"]  = df["Order_Status"].str.lower() == "returned"
    df["Date_Ordinal"] = df["Order_Date"].apply(
        lambda d: d.toordinal() if pd.notna(d) else None
    )
    #  Month_Year computed here as a proper column — never used as groupby key
    df["Month_Year"] = df["Order_Date"].dt.to_period("M").astype(str)

    return df


# ─────────────────────────────────────────────────────────────────────────────
# 6. PLOTLY BRAND LAYOUT HELPER
# ─────────────────────────────────────────────────────────────────────────────
def blayout(title="", height=370, legend_h=False):
    return dict(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(color=C_WHITE, size=13, family="Segoe UI, Arial"),
            x=0.01, xanchor="left",
        ),
        plot_bgcolor="rgb(0, 22, 180)",
        paper_bgcolor="rgb(0, 22, 180)",
        font=dict(color=C_WHITE, family="Segoe UI, Arial", size=11),
        height=height,
        margin=dict(l=36, r=16, t=46, b=36),
        hoverlabel=dict(bgcolor="rgb(0,18,160)", font_color=C_WHITE, bordercolor=C_YELLOW),
        xaxis=dict(
            color=C_WHITE,
            tickfont=dict(color=C_WHITE, size=10),
            linecolor="rgba(255,238,1,0.3)",
            gridcolor="rgba(255,255,255,0.06)",
        ),
        yaxis=dict(
            color=C_WHITE,
            tickfont=dict(color=C_WHITE, size=10),
            linecolor="rgba(255,238,1,0.3)",
            gridcolor="rgba(255,255,255,0.06)",
        ),
        legend=dict(
            bgcolor="rgba(0,22,180,0.9)",
            bordercolor="rgba(255,238,1,0.4)",
            borderwidth=1,
            font=dict(color=C_WHITE, size=10),
            orientation="h" if legend_h else "v",
            y=-0.22 if legend_h else 1,
        ),
    )


# ─────────────────────────────────────────────────────────────────────────────
# 7. LOAD ASSETS
# ─────────────────────────────────────────────────────────────────────────────
df_raw         = load_data()
logo_b64, logo_mime = load_logo()


# ─────────────────────────────────────────────────────────────────────────────
# 8. SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:

    # ── Logo block ────────────────────────────────────────────────────────────
    if logo_b64:
        st.markdown(
            f"""
            <div style="text-align:center; padding:18px 0 10px 0;">
              <img src="data:{logo_mime};base64,{logo_b64}"
                   width="162"
                   style="border-radius:14px;
                          border:3px solid {C_YELLOW};
                          box-shadow:0 0 22px rgba(255,238,1,0.4);" />
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div style="text-align:center; padding:18px 0 10px 0;">
              <span style="color:{C_YELLOW}; font-size:2rem;
                           font-family:'Arial Black'; font-weight:900;">bokku!</span>
              <br/>
              <span style="color:{C_WHITE}; font-size:0.85rem;
                           font-weight:700; letter-spacing:0.25em;">MART</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div style="text-align:center; margin-bottom:4px;">
          <span style="color:{C_YELLOW}; font-size:0.62rem;
                       font-weight:700; letter-spacing:0.15em;">
            SALES INTELLIGENCE FILTERS
          </span>
        </div>
        <hr/>
        """,
        unsafe_allow_html=True,
    )

    def _uniq(col):
        return sorted(df_raw[col].dropna().unique().tolist())

    # Date range
    _min = df_raw["Order_Date"].min()
    _max = df_raw["Order_Date"].max()
    if pd.isna(_min): _min = datetime(2025, 1, 1)
    if pd.isna(_max): _max = datetime(2026, 1, 31)

    st.markdown('<p class="sb-label"> Date Range</p>', unsafe_allow_html=True)
    date_range = st.date_input(
        "Date", value=(_min.date(), _max.date()),
        min_value=_min.date(), max_value=_max.date(),
        label_visibility="collapsed",
    )

    st.markdown('<p class="sb-label"> Order Status</p>',    unsafe_allow_html=True)
    sel_status   = st.multiselect("Status",   _uniq("Order_Status"),    default=_uniq("Order_Status"),    label_visibility="collapsed")

    st.markdown('<p class="sb-label"> Payment Method</p>',  unsafe_allow_html=True)
    sel_payment  = st.multiselect("Payment",  _uniq("Payment_Method"),  default=_uniq("Payment_Method"),  label_visibility="collapsed")

    st.markdown('<p class="sb-label"> Delivery Method</p>', unsafe_allow_html=True)
    sel_delivery = st.multiselect("Delivery", _uniq("Delivery_Method"), default=_uniq("Delivery_Method"), label_visibility="collapsed")

    st.markdown('<p class="sb-label"> Category</p>',        unsafe_allow_html=True)
    sel_category = st.multiselect("Category", _uniq("Category"),        default=_uniq("Category"),        label_visibility="collapsed")

    st.markdown('<p class="sb-label"> Store City</p>',       unsafe_allow_html=True)
    sel_city     = st.multiselect("City",     _uniq("Store_City"),      default=_uniq("Store_City"),      label_visibility="collapsed")

    st.markdown('<p class="sb-label"> Supplier</p>',         unsafe_allow_html=True)
    sel_supplier = st.multiselect("Supplier", _uniq("Supplier"),        default=_uniq("Supplier"),        label_visibility="collapsed")

    st.markdown('<p class="sb-label"> Store ID</p>',         unsafe_allow_html=True)
    sel_store    = st.multiselect("Store",    _uniq("Store_ID"),        default=_uniq("Store_ID"),        label_visibility="collapsed")

    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown(
        f'<p style="color:{C_GRAY}; font-size:0.6rem; text-align:center;">'
        f'Bokku Mart · Intelligence Hub · v3.0</p>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 9. APPLY FILTERS
# ─────────────────────────────────────────────────────────────────────────────
df = df_raw.copy()

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    df = df[df["Order_Date"].between(
        pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1]), inclusive="both"
    )]

if sel_status:   df = df[df["Order_Status"].isin(sel_status)]
if sel_payment:  df = df[df["Payment_Method"].isin(sel_payment)]
if sel_delivery: df = df[df["Delivery_Method"].isin(sel_delivery)]
if sel_category: df = df[df["Category"].isin(sel_category)]
if sel_city:     df = df[df["Store_City"].isin(sel_city)]
if sel_supplier: df = df[df["Supplier"].isin(sel_supplier)]
if sel_store:    df = df[df["Store_ID"].isin(sel_store)]

n_filt  = len(df)
n_total = len(df_raw)


# ─────────────────────────────────────────────────────────────────────────────
# 10. HERO BANNER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div style="background:linear-gradient(135deg, rgb(0,22,180) 0%, rgb(0,14,140) 100%);
                border:2px solid {C_YELLOW};
                border-radius:14px;
                padding:20px 28px 16px 28px;
                margin-bottom:18px;
                display:flex;
                align-items:center;
                justify-content:space-between;">
      <div>
        <div style="display:flex; align-items:baseline; gap:10px;">
          <span style="color:{C_YELLOW}; font-size:2.2rem;
                       font-family:'Arial Black',Arial; font-weight:900;
                       letter-spacing:-0.01em; line-height:1;">bokku!</span>
          <span style="color:{C_WHITE}; font-size:1.15rem;
                       font-weight:700; letter-spacing:0.2em; line-height:1;">MART</span>
        </div>
        <p style="color:{C_GRAY}; font-size:0.75rem; margin:5px 0 0 2px;
                  letter-spacing:0.1em; font-weight:500;">
          GROCERY SALES INTELLIGENCE DASHBOARD
        </p>
      </div>
      <div style="text-align:right;">
        <p style="color:{C_YELLOW}; font-size:0.62rem; font-weight:700;
                  letter-spacing:0.1em; margin:0 0 2px 0;">RECORDS IN VIEW</p>
        <p style="color:{C_WHITE}; font-size:1.8rem; font-weight:800;
                  margin:0; line-height:1;">{n_filt:,}
          <span style="color:{C_GRAY}; font-size:0.85rem; font-weight:400;">
            &nbsp;/ {n_total:,}
          </span>
        </p>
        <p style="color:{C_GRAY}; font-size:0.6rem; margin:2px 0 0 0;">
          transactions matched
        </p>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────────────
# 11. KPI CALCULATIONS
# ─────────────────────────────────────────────────────────────────────────────
total_rev       = df["Total_Revenue_NGN"].sum()
total_profit    = df["Profit_NGN"].sum()
avg_margin      = df["Gross_Margin_Pct"].mean()
units_sold      = int(df["Quantity_Sold"].sum())
returned_cnt    = int((df["Order_Status"] == "Returned").sum())
pending_cnt     = int((df["Order_Status"] == "Pending").sum())
completed_cnt   = int((df["Order_Status"] == "Completed").sum())
return_rate     = returned_cnt / n_filt * 100 if n_filt > 0 else 0.0

top_category    = df.groupby("Category")["Total_Revenue_NGN"].sum().idxmax()    if not df.empty else "N/A"
top_product_raw = df.groupby("Product_Name")["Total_Revenue_NGN"].sum().idxmax() if not df.empty else "N/A"
top_product     = (top_product_raw[:26] + "…") if len(top_product_raw) > 26 else top_product_raw
top_city        = df.groupby("Store_City")["Total_Revenue_NGN"].sum().idxmax()  if not df.empty else "N/A"


# ─────────────────────────────────────────────────────────────────────────────
# 12. KPI CARDS  — 3 rows × 4 columns
# ─────────────────────────────────────────────────────────────────────────────
def sec(label):
    st.markdown(f'<p class="sec-hdr">{label}</p>', unsafe_allow_html=True)


sec(" Key Performance Indicators")

c1, c2, c3, c4 = st.columns(4)
c1.metric(" Total Transactions",  f"{n_filt:,}")
c2.metric(" Total Revenue",       f"₦{total_rev:,.0f}")
c3.metric(" Total Profit",        f"₦{total_profit:,.0f}")
c4.metric(" Avg Gross Margin",    f"{avg_margin:.1f}%" if pd.notna(avg_margin) else "N/A")

st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)

c5, c6, c7, c8 = st.columns(4)
c5.metric(" Units Sold",          f"{units_sold:,}")
c6.metric(" Returned Orders",     f"{returned_cnt:,}  ({return_rate:.1f}%)")
c7.metric(" Pending Orders",      f"{pending_cnt:,}")
c8.metric(" Completed Orders",    f"{completed_cnt:,}")

st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)

c9, c10, c11, _ = st.columns(4)
c9.metric(" Top Category",        top_category)
c10.metric(" Top Product",        top_product)
c11.metric(" Top Revenue City",   top_city)

st.markdown("<hr/>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 13. ROW A — Order Status | Revenue vs Profit | Sales Over Time
# ─────────────────────────────────────────────────────────────────────────────
sec(" Sales Performance Analytics")

ca1, ca2, ca3 = st.columns([1, 1.4, 1.6])

# Chart 1: Order Status Distribution
with ca1:
    s_df = df.groupby("Order_Status", as_index=False)["Transaction_ID"].count()
    s_df.columns = ["Status", "Count"]
    s_df["Color"] = s_df["Status"].map(STATUS_COLORS).fillna("#FFFFFF")

    fig = go.Figure(go.Bar(
        x=s_df["Status"], y=s_df["Count"],
        marker=dict(color=s_df["Color"].tolist(),
                    line=dict(color="rgba(255,238,1,0.4)", width=1)),
        text=s_df["Count"], textposition="outside",
        textfont=dict(color=C_WHITE, size=11),
        hovertemplate="<b>%{x}</b><br>Count: %{y:,}<extra></extra>",
    ))
    fig.update_layout(**{**blayout("Order Status Distribution"), "showlegend": False})
    st.plotly_chart(fig, use_container_width=True)

# Chart 2: Revenue vs Profit by Store City
with ca2:
    city_df = (
        df.groupby("Store_City", as_index=False)
          .agg(Revenue=("Total_Revenue_NGN","sum"), Profit=("Profit_NGN","sum"))
          .sort_values("Revenue", ascending=False)
    )
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Revenue", x=city_df["Store_City"], y=city_df["Revenue"],
        marker_color="#FFEE01",
        text=city_df["Revenue"].apply(lambda v: f"₦{v/1e6:.1f}M"),
        textposition="outside", textfont=dict(color=C_WHITE, size=8),
        hovertemplate="<b>%{x}</b><br>Revenue: ₦%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Profit", x=city_df["Store_City"], y=city_df["Profit"],
        marker_color="#6B8FFF",
        text=city_df["Profit"].apply(lambda v: f"₦{v/1e6:.1f}M"),
        textposition="outside", textfont=dict(color=C_WHITE, size=8),
        hovertemplate="<b>%{x}</b><br>Profit: ₦%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(**blayout("Revenue vs Profit by City", legend_h=True), barmode="group")
    st.plotly_chart(fig, use_container_width=True)

# Chart 3: Sales Over Time
#  BUG FIX: re-derive Month_Year from the filtered slice then groupby that column
with ca3:
    t_df = df.dropna(subset=["Order_Date"]).copy()
    if not t_df.empty:
        t_df["Month_Year"] = t_df["Order_Date"].dt.to_period("M").astype(str)
        t_df = (
            t_df.groupby("Month_Year", as_index=False)["Total_Revenue_NGN"].sum()
                .sort_values("Month_Year")
        )
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=t_df["Month_Year"], y=t_df["Total_Revenue_NGN"],
            mode="lines+markers",
            line=dict(color="#FFEE01", width=2.5),
            marker=dict(color="#FFEE01", size=7, line=dict(color=C_WHITE, width=1.5)),
            fill="tozeroy", fillcolor="rgba(255,238,1,0.07)",
            hovertemplate="<b>%{x}</b><br>Revenue: ₦%{y:,.0f}<extra></extra>",
        ))
        fig.update_layout(**blayout("Monthly Sales Revenue"))
        fig.update_layout(showlegend=False, xaxis_tickangle=-35)
    else:
        fig = go.Figure()
        fig.update_layout(**blayout("Monthly Sales Revenue — No Data"))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("<div style='margin-top:4px;'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 14. ROW B — Payment Donut | Top 10 Products | Category Revenue
# ─────────────────────────────────────────────────────────────────────────────
sec(" Product & Payment Intelligence")

cb1, cb2, cb3 = st.columns([1, 1.4, 1.6])

# Chart 4: Payment Method Donut
with cb1:
    pay_df = df.groupby("Payment_Method", as_index=False)["Transaction_ID"].count()
    pay_df.columns = ["Method", "Count"]
    fig = go.Figure(go.Pie(
        labels=pay_df["Method"], values=pay_df["Count"],
        hole=0.55,
        marker=dict(colors=CHART_PALETTE[:len(pay_df)],
                    line=dict(color="rgb(0,22,180)", width=2.5)),
        textfont=dict(color=C_WHITE, size=11),
        hovertemplate="<b>%{label}</b><br>Txns: %{value:,}<br>Share: %{percent}<extra></extra>",
    ))
    fig.update_layout(**blayout("Payment Method Breakdown", legend_h=True))
    st.plotly_chart(fig, use_container_width=True)

# Chart 5: Top 10 Products by Revenue
with cb2:
    prod_df = (
        df.groupby("Product_Name", as_index=False)["Total_Revenue_NGN"].sum()
          .sort_values("Total_Revenue_NGN", ascending=True)
          .tail(10)
    )
    fig = go.Figure(go.Bar(
        x=prod_df["Total_Revenue_NGN"], y=prod_df["Product_Name"],
        orientation="h",
        marker=dict(
            color=prod_df["Total_Revenue_NGN"].tolist(),
            colorscale=[[0,"#3A5BCC"],[0.5,"#FFD700"],[1,"#FFEE01"]],
            showscale=False,
            line=dict(color="rgba(255,238,1,0.3)", width=0.5),
        ),
        text=prod_df["Total_Revenue_NGN"].apply(lambda v: f"₦{v/1e3:.0f}k"),
        textposition="outside", textfont=dict(color=C_WHITE, size=9),
        hovertemplate="<b>%{y}</b><br>Revenue: ₦%{x:,.0f}<extra></extra>",
    ))
    fig.update_layout(**{**blayout("Top 10 Products by Revenue"), "showlegend": False})
    st.plotly_chart(fig, use_container_width=True)

# Chart 6: Sales by Category
with cb3:
    cat_df = (
        df.groupby("Category", as_index=False)["Total_Revenue_NGN"].sum()
          .sort_values("Total_Revenue_NGN", ascending=False)
    )
    fig = go.Figure(go.Bar(
        x=cat_df["Category"], y=cat_df["Total_Revenue_NGN"],
        marker=dict(color=CHART_PALETTE[:len(cat_df)],
                    line=dict(color="rgba(255,238,1,0.4)", width=1)),
        text=cat_df["Total_Revenue_NGN"].apply(lambda v: f"₦{v/1e6:.2f}M"),
        textposition="outside", textfont=dict(color=C_WHITE, size=10),
        hovertemplate="<b>%{x}</b><br>Revenue: ₦%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(**{**blayout("Revenue by Product Category"), "showlegend": False})
    st.plotly_chart(fig, use_container_width=True)

st.markdown("<div style='margin-top:4px;'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 15. ROW C — Supplier Treemap | Delivery Volume | Stacked Status × Delivery
# ─────────────────────────────────────────────────────────────────────────────
sec(" Supplier, Delivery & Fulfilment Analytics")

cc1, cc2, cc3 = st.columns(3)

# Chart 7: Profit by Supplier (Treemap)
with cc1:
    sup_df = (
        df.groupby("Supplier", as_index=False)["Profit_NGN"].sum()
          .sort_values("Profit_NGN", ascending=False)
    )
    fig = go.Figure(go.Treemap(
        labels=sup_df["Supplier"],
        parents=[""] * len(sup_df),
        values=sup_df["Profit_NGN"].clip(lower=1),
        marker=dict(
            colors=sup_df["Profit_NGN"].tolist(),
            colorscale=[[0,"rgb(0,22,180)"],[0.5,"#3A5BCC"],[1,"#FFEE01"]],
            showscale=False,
            pad=dict(t=4, l=4, r=4, b=4),
        ),
        textfont=dict(color=C_WHITE, size=12),
        hovertemplate="<b>%{label}</b><br>Profit: ₦%{value:,.0f}<extra></extra>",
    ))
    fig.update_layout(**{**blayout("Profit by Supplier", height=375), "showlegend": False})
    st.plotly_chart(fig, use_container_width=True)

# Chart 8: Delivery Method Volume
with cc2:
    del_df = df.groupby("Delivery_Method", as_index=False)["Quantity_Sold"].sum()
    fig = go.Figure(go.Bar(
        x=del_df["Delivery_Method"], y=del_df["Quantity_Sold"],
        marker=dict(color=["#FFEE01","#6B8FFF"],
                    line=dict(color=C_WHITE, width=1)),
        text=del_df["Quantity_Sold"],
        textposition="outside", textfont=dict(color=C_WHITE, size=12),
        hovertemplate="<b>%{x}</b><br>Units: %{y:,}<extra></extra>",
    ))
    fig.update_layout(**{**blayout("Delivery Method — Units Sold", height=375), "showlegend": False})
    st.plotly_chart(fig, use_container_width=True)

# Chart 9: Order Status × Delivery Method (Stacked Bar)
with cc3:
    stk_df = (
        df.groupby(["Delivery_Method","Order_Status"], as_index=False)
          ["Transaction_ID"].count()
    )
    stk_df.columns = ["Delivery_Method","Order_Status","Count"]
    fig = go.Figure()
    for status in ["Completed","Pending","Returned"]:
        sub = stk_df[stk_df["Order_Status"] == status]
        if sub.empty: continue
        clr = STATUS_COLORS.get(status, "#FFFFFF")
        fig.add_trace(go.Bar(
            name=status,
            x=sub["Delivery_Method"], y=sub["Count"],
            marker_color=clr,
            text=sub["Count"], textposition="inside",
            textfont=dict(color="rgb(0,18,160)" if clr=="#FFEE01" else C_WHITE, size=11),
            hovertemplate=f"<b>%{{x}}</b><br>{status}: %{{y:,}}<extra></extra>",
        ))
    fig.update_layout(**blayout("Order Status by Delivery Method", height=375,
                                legend_h=True), barmode="stack")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("<div style='margin-top:4px;'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 16. ROW D — 3D Intelligence Scatter (full width)
# ─────────────────────────────────────────────────────────────────────────────
sec("🔬 Advanced 3D Sales Intelligence Scatter")

sc_df = df.dropna(subset=["Date_Ordinal","Quantity_Sold","Total_Revenue_NGN"]).copy()

if not sc_df.empty:
    fig3d = go.Figure()
    for status, color in STATUS_COLORS.items():
        sub = sc_df[sc_df["Order_Status"] == status]
        if sub.empty: continue
        fig3d.add_trace(go.Scatter3d(
            x=sub["Date_Ordinal"], y=sub["Quantity_Sold"], z=sub["Total_Revenue_NGN"],
            mode="markers", name=status,
            marker=dict(size=4, color=color, opacity=0.85,
                        line=dict(color="rgba(0,18,160,0.4)", width=0.3)),
            customdata=sub[["Transaction_ID","Product_Name","Category",
                            "Store_City","Gross_Margin_Pct"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Product : %{customdata[1]}<br>"
                "Category: %{customdata[2]}<br>"
                "City    : %{customdata[3]}<br>"
                "Margin  : %{customdata[4]:.1f}%<br>"
                "Qty Sold: %{y:,}<br>"
                "Revenue : ₦%{z:,.0f}<extra></extra>"
            ),
        ))
    fig3d.update_layout(
        height=520,
        paper_bgcolor="rgb(0,22,180)",
        margin=dict(l=0, r=0, t=30, b=0),
        scene=dict(
            bgcolor="rgb(0,18,160)",
            xaxis=dict(title="Date (Ordinal)", color=C_WHITE,
                       backgroundcolor="rgb(0,18,160)",
                       gridcolor="rgba(255,255,255,0.08)",
                       tickfont=dict(color=C_WHITE, size=9)),
            yaxis=dict(title="Qty Sold", color=C_WHITE,
                       backgroundcolor="rgb(0,18,160)",
                       gridcolor="rgba(255,255,255,0.08)",
                       tickfont=dict(color=C_WHITE, size=9)),
            zaxis=dict(title="Revenue (₦)", color=C_WHITE,
                       backgroundcolor="rgb(0,18,160)",
                       gridcolor="rgba(255,255,255,0.08)",
                       tickfont=dict(color=C_WHITE, size=9)),
        ),
        legend=dict(
            bgcolor="rgba(0,22,180,0.9)", bordercolor="rgba(255,238,1,0.4)",
            borderwidth=1, font=dict(color=C_WHITE, size=11), x=0.01, y=0.99,
        ),
        hoverlabel=dict(bgcolor="rgb(0,18,160)", font_color=C_WHITE, bordercolor=C_YELLOW),
    )
    st.plotly_chart(fig3d, use_container_width=True)
else:
    st.info("No data available for 3D scatter with current filters.")

st.markdown("<hr/>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 17. EXECUTIVE INSIGHT PANEL
# ─────────────────────────────────────────────────────────────────────────────
with st.expander("  EXECUTIVE INSIGHT PANEL — Click to Expand Strategic Summary"):
    st.markdown(
        f"""
        <div style="background:rgb(0,18,160); padding:22px 26px;
                    border-radius:10px; line-height:1.8;">
          <h3 style="color:{C_YELLOW}; font-family:Arial Black; margin:0 0 6px 0;">
            Bokku Mart — Strategic Sales Intelligence Summary
          </h3>
          <hr style="border-color:rgba(255,238,1,0.35); margin:0 0 16px 0;"/>

          <h4 style="color:{C_YELLOW}; margin:0 0 4px 0;"> Seasonal Demand Patterns</h4>
          <p style="color:{C_WHITE}; margin:0 0 14px 0;">
            January 2025 was the strongest month (₦927K revenue), with a mid-year
            trough (Sep: ₦652K) and a December recovery (₦798K). Procurement teams should
            pre-position Grains and Beverages 6 weeks before December and January peak windows
            to prevent stockouts and protect margin during high-demand periods.
          </p>

          <h4 style="color:{C_YELLOW}; margin:0 0 4px 0;"> Margin Variance by Category & City</h4>
          <p style="color:{C_WHITE}; margin:0 0 14px 0;">
            Dairy leads total revenue, while Grains experience commodity margin compression.
            Lagos and Abuja deliver highest absolute revenues but face tighter margins from
            competitive pricing. Allocate shelf space toward Beverages and Snacks in
            high-rent store locations to maximise blended margin per square metre.
          </p>

          <h4 style="color:{C_YELLOW}; margin:0 0 4px 0;"> Payment Behaviour in Nigerian Retail</h4>
          <p style="color:{C_WHITE}; margin:0 0 14px 0;">
            The four-way payment split (Cash, Mobile Wallet, POS, Bank Transfer) signals
            growing digital adoption. Finance teams should negotiate lower merchant fees with
            dominant mobile providers and guarantee POS terminal uptime across all cities,
            especially for Home Delivery where payment failures trigger order cancellations.
          </p>

          <h4 style="color:{C_YELLOW}; margin:0 0 4px 0;"> Return Patterns — Supplier & Fulfilment Signals</h4>
          <p style="color:{C_WHITE}; margin:0 0 14px 0;">
            Returned orders are direct revenue leakage. Cross-reference the Supplier Treemap
            with the Stacked Delivery chart to identify supplier or channel patterns.
            Any supplier with a return rate above 15% should be escalated for quality
            renegotiation. Home Delivery return clusters warrant a logistics damage audit.
          </p>

          <h4 style="color:{C_YELLOW}; margin:0 0 4px 0;"> Daily Operational Action Plan</h4>
          <p style="color:{C_WHITE}; margin:0 0 0 0;">
            ① Check KPIs each morning for prior-day revenue vs target. ② Review Top 10
            Products for fast-moving SKUs needing reorder. ③ Monitor Pending Orders daily
            to avoid SLA breaches. ④ Use the 3D Scatter to flag low-revenue / high-quantity
            anomalies (possible pricing errors or staff discount abuse). ⑤ Run weekly
            supplier reviews anchored to the Profit by Supplier treemap.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 18. FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div style="text-align:center; padding:14px 0 6px 0;
                border-top:1px solid rgba(255,238,1,0.25); margin-top:6px;">
      <p style="color:{C_YELLOW}; font-size:0.7rem; font-weight:700;
                letter-spacing:0.1em; margin:0;">
        BOKKU MART · GROCERY SALES INTELLIGENCE DASHBOARD · v3.0
      </p>
      <p style="color:{C_GRAY}; font-size:0.63rem; margin:3px 0 0 0;">
        Streamlit · Plotly · Pandas &nbsp;|&nbsp; ₦ Nigerian Naira &nbsp;|&nbsp;
        500 transactions · 8 cities · 5 suppliers · 20 products
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)
