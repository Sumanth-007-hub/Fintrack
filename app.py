from pathlib import Path
import sqlite3
from datetime import date

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =========================================================
# FINTRACK — Personal Finance Manager
# Python + Streamlit + SQLite + Pandas + Plotly
# =========================================================

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "finance.db"

st.set_page_config(
    page_title="FinTrack | Personal Finance",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- DESIGN SYSTEM ----------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #080d16;
    --panel: #101927;
    --panel2: #111d2c;
    --line: rgba(148, 163, 184, .16);
    --text: #edf4fb;
    --muted: #94a3b8;
    --mint: #45f0bd;
    --cyan: #52d9f5;
    --purple: #a78bfa;
    --pink: #fb7185;
}
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
.stApp {
    background:
      radial-gradient(ellipse at 80% 0%, rgba(21, 94, 117, .18), transparent 34%),
      radial-gradient(ellipse at 10% 40%, rgba(16, 185, 129, .06), transparent 30%),
      var(--bg);
    color: var(--text);
}
[data-testid="stHeader"] {
    background: rgba(8, 13, 22, .78);
}
.block-container {
    max-width: 1500px;
    padding-top: 1.65rem;
    padding-bottom: 3rem;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1320 0%, #090f1b 100%);
    border-right: 1px solid rgba(148,163,184,.14);
}
section[data-testid="stSidebar"] > div {
    padding-top: 1.5rem;
}
h1, h2, h3, h4 {
    font-family: 'Manrope', sans-serif !important;
    letter-spacing: -.035em;
    color: #f3f7fc !important;
}
h1 { font-weight: 800 !important; }
p, label, span { color: inherit; }
small, .muted { color: var(--muted); }
hr {
    border-color: var(--line);
    margin: 1.35rem 0;
}
[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(19,33,49,.97), rgba(12,22,35,.97));
    border: 1px solid rgba(148,163,184,.16);
    border-radius: 18px;
    padding: 19px 20px;
    box-shadow: 0 10px 35px rgba(0,0,0,.13);
    min-height: 128px;
}
[data-testid="stMetricLabel"] {
    color: #a8b8cc !important;
    font-size: .9rem !important;
    font-weight: 600 !important;
}
[data-testid="stMetricValue"] {
    color: #f5f9ff !important;
    font-family: 'Manrope', sans-serif !important;
    font-size: clamp(1.3rem, 2vw, 2rem) !important;
    font-weight: 800 !important;
}
[data-testid="stMetricDelta"] { font-weight: 700; }
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {
    background-color: #111c2b;
    border-color: #2a3b50;
    border-radius: 10px;
}
div.stButton > button, div.stFormSubmitButton > button {
    border-radius: 10px;
    border: 1px solid rgba(69,240,189,.35);
    background: linear-gradient(100deg, #0b8e74, #087e8b);
    color: white;
    font-weight: 700;
    min-height: 2.7rem;
    transition: all .18s ease;
}
div.stButton > button:hover, div.stFormSubmitButton > button:hover {
    border-color: #45f0bd;
    box-shadow: 0 0 22px rgba(69,240,189,.15);
    color: white;
}
[data-testid="stDataFrame"] {
    border: 1px solid rgba(148,163,184,.18);
    border-radius: 13px;
    overflow: hidden;
}
[data-testid="stAlert"] { border-radius: 12px; }
div[data-testid="stTabs"] button { font-weight: 700; }
.ft-brand {
    padding: 10px 8px 18px;
}
.ft-brand-mark {
    display: inline-flex;
    width: 42px; height: 42px;
    align-items: center; justify-content: center;
    border-radius: 13px;
    color: #051510;
    font-size: 22px;
    font-weight: 900;
    background: linear-gradient(145deg, #6effd0, #16bda1);
    box-shadow: 0 0 24px rgba(69,240,189,.19);
}
.ft-brand-name {
    font-family: 'Manrope', sans-serif;
    font-size: 26px; font-weight: 800;
    letter-spacing: -1px;
    margin-left: 10px;
    vertical-align: middle;
}
.ft-brand-sub {
    color: #8da1b7; font-size: 12px;
    letter-spacing: 1.4px; margin-top: 7px;
}
.ft-hero {
    position: relative;
    overflow: hidden;
    padding: 27px 30px;
    border-radius: 22px;
    border: 1px solid rgba(69,240,189,.30);
    background:
      radial-gradient(ellipse at 88% 40%, rgba(16,185,129,.23), transparent 33%),
      linear-gradient(115deg, rgba(7,49,45,.96), rgba(14,26,45,.98) 62%, rgba(27,26,64,.95));
    margin-bottom: 23px;
}
.ft-eyebrow {
    font-size: 11px; letter-spacing: 2.5px; font-weight: 800;
    color: #58f3ca; text-transform: uppercase;
}
.ft-hero h1 {
    font-size: clamp(28px, 3.2vw, 42px);
    line-height: 1.12; margin: 12px 0 8px;
}
.ft-hero p { color: #c4d2e0; font-size: 15px; margin: 0; }
.ft-hero-orb {
    position: absolute; right: 34px; top: 15px;
    width: 135px; height: 135px; border-radius: 50%;
    border: 1px solid rgba(69,240,189,.22);
    box-shadow: inset 0 0 35px rgba(69,240,189,.06), 0 0 40px rgba(69,240,189,.05);
}
.ft-hero-orb:before, .ft-hero-orb:after {
    content: ""; position: absolute; inset: 17px;
    border: 1px solid rgba(82,217,245,.24); border-radius: 50%;
    transform: rotateX(65deg) rotateZ(25deg);
}
.ft-hero-orb:after { inset: 35px -5px; transform: rotateX(65deg) rotateZ(-25deg); }
.ft-section-label {
    color: #93a7bd; text-transform: uppercase;
    letter-spacing: 2px; font-size: 11px; font-weight: 800;
    margin: 7px 0 13px;
}
.ft-panel {
    background: linear-gradient(145deg, rgba(17,29,44,.94), rgba(10,19,31,.96));
    border: 1px solid rgba(148,163,184,.16);
    border-radius: 18px;
    padding: 19px 20px;
    box-shadow: 0 12px 35px rgba(0,0,0,.12);
}
.ft-panel-title {
    font-family: 'Manrope', sans-serif; font-weight: 800;
    font-size: 16px; color: #eef5fc;
}
.ft-panel-sub { color: #91a4ba; font-size: 12px; margin-top: 3px; }
.ft-insight {
    background: radial-gradient(ellipse at 100% 50%, rgba(16,185,129,.15), transparent 45%),
                linear-gradient(120deg, #102b2c, #101c2a);
    border: 1px solid rgba(69,240,189,.28);
    border-radius: 18px; padding: 20px;
}
.ft-insight-label { color: #facc15; font-weight: 800; font-size: 14px; }
.ft-insight-text { color: #d6e1ed; line-height: 1.6; margin-top: 9px; }
.ft-tag {
    display: inline-block; padding: 4px 9px; border-radius: 30px;
    font-size: 11px; font-weight: 800;
}
.ft-footer {
    color: #63768d; font-size: 11px; letter-spacing: 1.2px;
    text-align: center; padding-top: 18px;
}
@media (max-width: 800px) {
    .ft-hero { padding: 22px; }
    .ft-hero-orb { opacity: .35; right: -15px; }
}
</style>
""", unsafe_allow_html=True)

# -------------------- DATABASE ---------------------------

def get_connection():
    return sqlite3.connect(DB_PATH)

def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_date TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT
            )
        """)

def load_transactions():
    with get_connection() as conn:
        data = pd.read_sql_query(
            """SELECT id, transaction_date, transaction_type, category,
                      amount, description
               FROM transactions
               ORDER BY transaction_date DESC, id DESC""",
            conn
        )
    if not data.empty:
        data["transaction_date"] = pd.to_datetime(
            data["transaction_date"], errors="coerce"
        )
        data["amount"] = pd.to_numeric(data["amount"], errors="coerce").fillna(0)
        data["description"] = data["description"].fillna("")
    return data

def save_transaction(transaction_date, transaction_type, category, amount, description):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO transactions
               (transaction_date, transaction_type, category, amount, description)
               VALUES (?, ?, ?, ?, ?)""",
            (str(transaction_date), transaction_type, category, float(amount), description.strip())
        )

def delete_transaction(transaction_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM transactions WHERE id = ?", (int(transaction_id),))

initialize_database()
df = load_transactions()

# -------------------- HELPERS ----------------------------

def money(value):
    return f"₹{float(value):,.2f}"

def plot_layout(fig, height=320):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#cbd5e1", size=12),
        margin=dict(t=18, b=12, l=10, r=10),
        height=height,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#cbd5e1")
        ),
        hoverlabel=dict(
            bgcolor="#101927",
            bordercolor="#45f0bd",
            font_color="#f8fafc"
        ),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="rgba(148,163,184,.12)")
    fig.update_yaxes(gridcolor="rgba(148,163,184,.10)", zeroline=False)
    return fig

income_total = float(df.loc[df["transaction_type"] == "Income", "amount"].sum()) if not df.empty else 0.0
expense_total = float(df.loc[df["transaction_type"] == "Expense", "amount"].sum()) if not df.empty else 0.0
net_savings = income_total - expense_total
savings_rate = (net_savings / income_total * 100) if income_total > 0 else 0.0

# -------------------- SIDEBAR -----------------------------

with st.sidebar:
    st.markdown("""
    <div class="ft-brand">
      <span class="ft-brand-mark">↗</span><span class="ft-brand-name">FinTrack</span>
      <div class="ft-brand-sub">PLAN · TRACK · GROW</div>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Your personal finance workspace")
    st.markdown("<div class='ft-section-label'>Workspace</div>", unsafe_allow_html=True)
    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Add Transaction",
            "Transaction History",
            "Analytics",
            "Insights",
            "About This Project",
        ],
        label_visibility="collapsed",
        format_func=lambda p: {
            "Dashboard": "◈  Dashboard",
            "Add Transaction": "＋  Add Transaction",
            "Transaction History": "▤  Transaction History",
            "Analytics": "⌁  Analytics",
            "Insights": "✧  Insights",
            "About This Project": "ⓘ  About This Project",
        }[p],
    )
    st.markdown("---")
    st.markdown("""
    <div class="ft-panel" style="padding:15px;">
      <div style="font-size:11px;letter-spacing:1.5px;color:#45f0bd;font-weight:800;">SMART FINANCE</div>
      <div style="font-size:17px;font-weight:800;margin-top:7px;">Build better habits.</div>
      <div style="color:#94a3b8;font-size:12px;margin-top:4px;">Small steps. Stronger future.</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div class='ft-footer'>BUILT WITH PYTHON · STREAMLIT</div>", unsafe_allow_html=True)

# -------------------- DASHBOARD --------------------------

if page == "Dashboard":
    st.markdown(f"""
    <div class="ft-hero">
      <div class="ft-eyebrow">FinTrack / Personal Finance</div>
      <h1>Your money. Your future.</h1>
      <p>Welcome to your financial command centre. Track clearly, plan confidently.</p>
      <div class="ft-hero-orb"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='ft-section-label'>Your financial overview</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("↗  TOTAL INCOME", money(income_total))
    c2.metric("↘  TOTAL EXPENSES", money(expense_total))
    c3.metric("◇  NET SAVINGS", money(net_savings))
    c4.metric("◎  SAVINGS RATE", f"{savings_rate:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([0.95, 1.45], gap="large")

    with left:
        st.markdown("<div class='ft-panel-title'>Spending breakdown</div><div class='ft-panel-sub'>How your expenses are distributed</div>", unsafe_allow_html=True)
        expense_df = df[df["transaction_type"] == "Expense"].copy() if not df.empty else pd.DataFrame()
        if not expense_df.empty:
            category_totals = expense_df.groupby("category", as_index=False)["amount"].sum()
            fig = px.pie(
                category_totals, names="category", values="amount", hole=0.70,
                color_discrete_sequence=["#45f0bd", "#8b7cff", "#52d9f5", "#fb7185", "#fbbf24", "#a3e635", "#f97316"]
            )
            fig.update_traces(
                textinfo="percent",
                textfont=dict(color="#07111d", size=11),
                marker=dict(line=dict(color="#101927", width=3)),
                hovertemplate="<b>%{label}</b><br>Amount: ₹%{value:,.2f}<br>%{percent}<extra></extra>"
            )
            fig = plot_layout(fig, 300)
            fig.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.12, x=0.0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("<div style='padding:45px 10px;text-align:center;color:#94a3b8;'>Your category chart will appear when you add expenses.</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='ft-panel-title'>Income vs expenses</div><div class='ft-panel-sub'>Compare money received with money spent</div>", unsafe_allow_html=True)
        comp = pd.DataFrame({"Type": ["Income", "Expenses"], "Amount": [income_total, expense_total]})
        fig = px.bar(
            comp, x="Type", y="Amount", color="Type", text="Amount",
            color_discrete_map={"Income": "#45f0bd", "Expenses": "#fb7185"}
        )
        fig.update_traces(
            texttemplate="₹%{y:,.0f}", textposition="outside",
            marker_line_width=0, cliponaxis=False,
            hovertemplate="%{x}<br>₹%{y:,.2f}<extra></extra>"
        )
        fig = plot_layout(fig, 300)
        fig.update_layout(showlegend=False, yaxis_title="", xaxis_title="", uniformtext_minsize=10, uniformtext_mode="hide")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    recent_col, insight_col = st.columns([1.45, 0.95], gap="large")

    with recent_col:
        st.markdown("<div class='ft-panel-title'>Recent transactions</div><div class='ft-panel-sub'>Your latest financial activity</div>", unsafe_allow_html=True)
        if df.empty:
            st.info("No transactions yet. Add your first transaction to bring your dashboard to life.")
        else:
            recent = df.head(6).copy()
            recent["transaction_date"] = recent["transaction_date"].dt.strftime("%d %b %Y")
            recent["amount"] = recent.apply(
                lambda r: ("+ " if r["transaction_type"] == "Income" else "− ") + money(r["amount"]),
                axis=1
            )
            recent["transaction_type"] = recent["transaction_type"].map(
                {"Income": "🟢 Income", "Expense": "🔴 Expense"}
            ).fillna(recent["transaction_type"])
            st.dataframe(
                recent[["transaction_date", "transaction_type", "category", "amount", "description"]],
                use_container_width=True, hide_index=True
            )

    with insight_col:
        if income_total <= 0 and expense_total <= 0:
            insight_title = "Your journey starts here"
            insight_text = "Add your first transaction to unlock meaningful financial insights."
            icon = "✦"
        elif net_savings < 0:
            insight_title = "Review your spending"
            insight_text = f"Your recorded expenses exceed income by {money(abs(net_savings))}. Review categories and identify areas to adjust."
            icon = "!"
        elif savings_rate >= 30:
            insight_title = "You're building momentum"
            insight_text = f"Your current savings rate is {savings_rate:.1f}%. Keep tracking consistently to understand your habits."
            icon = "✦"
        else:
            insight_title = "Find room to save"
            insight_text = f"Your current savings rate is {savings_rate:.1f}%. Review your spending breakdown to spot possible savings."
            icon = "◎"
        st.markdown(f"""
        <div class="ft-insight">
          <div style="font-size:25px;color:#facc15;">{icon}</div>
          <div class="ft-insight-label">FINTRACK INSIGHT</div>
          <div style="font-size:18px;font-weight:800;margin-top:7px;">{insight_title}</div>
          <div class="ft-insight-text">{insight_text}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="ft-panel">
          <div class="ft-section-label">The big picture</div>
          <div style="font-size:30px;font-weight:800;color:#45f0bd;">{len(df):,}</div>
          <div style="color:#94a3b8;font-size:13px;">transactions recorded</div>
          <hr>
          <div style="font-size:13px;color:#cbd5e1;">Plan better. Spend intentionally. Build your future.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='ft-footer'>FINTRACK · PLAN BETTER. SPEND SMARTER. BUILD YOUR FUTURE.</div>", unsafe_allow_html=True)

# -------------------- ADD TRANSACTION --------------------

elif page == "Add Transaction":
    st.title("＋ Add transaction")
    st.caption("Record money coming in or going out. Your dashboard updates automatically.")

    transaction_type = st.segmented_control(
        "Transaction type",
        options=["Income", "Expense"],
        default="Expense",
        key="new_transaction_type",
    )
    categories = {
        "Income": ["Salary", "Business", "Freelancing", "Investment", "Gift", "Other Income"],
        "Expense": ["Food", "Travel", "Shopping", "Education", "Bills", "Healthcare", "Entertainment", "Rent", "Other Expense"],
    }
    category = st.selectbox("Category", categories[transaction_type], key=f"category_{transaction_type}")

    with st.form("transaction_form", clear_on_submit=True):
        date_value = st.date_input("Transaction date", value=date.today())
        amount = st.number_input("Amount (₹)", min_value=0.0, value=0.0, step=100.0, format="%.2f")
        description = st.text_input("Description", placeholder="e.g. Monthly salary or groceries")
        submitted = st.form_submit_button("Save transaction", use_container_width=True)

    if submitted:
        if amount <= 0:
            st.error("Enter an amount greater than zero.")
        else:
            save_transaction(date_value, transaction_type, category, amount, description)
            st.success("Transaction saved. Your dashboard is updated!")
            st.rerun()

# -------------------- TRANSACTION HISTORY ----------------

elif page == "Transaction History":
    st.title("Transaction history")
    st.caption("Search, filter, review, and export your records.")

    if df.empty:
        st.info("No transactions yet. Add a transaction to get started.")
    else:
        f1, f2, f3 = st.columns([1, 1, 1.3])
        with f1:
            type_filter = st.selectbox("Transaction type", ["All", "Income", "Expense"])
        with f2:
            category_options = ["All"] + sorted(df["category"].dropna().unique().tolist())
            category_filter = st.selectbox("Category", category_options)
        with f3:
            search_text = st.text_input("Search description", placeholder="Search transactions...")

        filtered = df.copy()
        if type_filter != "All":
            filtered = filtered[filtered["transaction_type"] == type_filter]
        if category_filter != "All":
            filtered = filtered[filtered["category"] == category_filter]
        if search_text.strip():
            query = search_text.strip().lower()
            filtered = filtered[
                filtered["description"].str.lower().str.contains(query, na=False)
                | filtered["category"].str.lower().str.contains(query, na=False)
            ]

        st.caption(f"{len(filtered)} transaction(s) found")
        display = filtered.copy()
        display["transaction_date"] = display["transaction_date"].dt.strftime("%Y-%m-%d")
        st.dataframe(display, use_container_width=True, hide_index=True)

        st.download_button(
            "Download filtered transactions (CSV)",
            data=display.to_csv(index=False).encode("utf-8"),
            file_name="fintrack_transactions.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.markdown("---")
        with st.expander("Delete a transaction"):
            chosen_id = st.selectbox("Select transaction ID", filtered["id"].tolist(), key="delete_id")
            confirm = st.checkbox("I understand this permanently deletes the selected transaction.")
            if st.button("Delete selected transaction"):
                if confirm:
                    delete_transaction(chosen_id)
                    st.success("Transaction deleted.")
                    st.rerun()
                else:
                    st.warning("Please confirm before deleting.")

# -------------------- ANALYTICS ---------------------------

elif page == "Analytics":
    st.title("Financial analytics")
    st.caption("Explore how your income and expenses change over time.")

    if df.empty:
        st.info("Add transactions to unlock analytics.")
    else:
        dates = df["transaction_date"].dropna()
        years = sorted(dates.dt.year.unique().tolist(), reverse=True)
        selected_year = st.selectbox("Analysis year", years, index=0)
        year_df = df[df["transaction_date"].dt.year == selected_year].copy()
        year_df["month_number"] = year_df["transaction_date"].dt.month
        monthly = year_df.pivot_table(
            index="month_number", columns="transaction_type", values="amount",
            aggfunc="sum", fill_value=0
        ).reindex(range(1, 13), fill_value=0)
        monthly.index = [date(2000, m, 1).strftime("%b") for m in monthly.index]
        monthly = monthly.rename_axis("Month").reset_index()
        for col in ["Income", "Expense"]:
            if col not in monthly:
                monthly[col] = 0

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly["Month"], y=monthly["Income"], name="Income",
            mode="lines+markers", line=dict(color="#45f0bd", width=3),
            fill="tozeroy", fillcolor="rgba(69,240,189,.08)"
        ))
        fig.add_trace(go.Scatter(
            x=monthly["Month"], y=monthly["Expense"], name="Expenses",
            mode="lines+markers", line=dict(color="#fb7185", width=3),
            fill="tozeroy", fillcolor="rgba(251,113,133,.06)"
        ))
        fig = plot_layout(fig, 380)
        fig.update_layout(xaxis_title="", yaxis_title="Amount (₹)")
        st.plotly_chart(fig, use_container_width=True)

        a, b = st.columns(2, gap="large")
        with a:
            st.markdown("#### Monthly totals")
            st.dataframe(monthly, use_container_width=True, hide_index=True)
        with b:
            st.markdown("#### Expense categories")
            expenses_df = year_df[year_df["transaction_type"] == "Expense"]
            if not expenses_df.empty:
                cats = expenses_df.groupby("category", as_index=False)["amount"].sum().sort_values("amount", ascending=False)
                fig2 = px.bar(cats, x="amount", y="category", orientation="h", color="amount",
                              color_continuous_scale=["#14532d", "#45f0bd"])
                fig2 = plot_layout(fig2, 320)
                fig2.update_layout(coloraxis_showscale=False, xaxis_title="Amount (₹)", yaxis_title="")
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No expenses recorded for this year.")

# -------------------- INSIGHTS ----------------------------

elif page == "Insights":
    st.title("Financial insights")
    st.caption("A simple view of what your recorded data tells you.")

    a, b, c = st.columns(3)
    a.metric("Income recorded", money(income_total))
    b.metric("Expenses recorded", money(expense_total))
    c.metric("Net position", money(net_savings))

    if df.empty:
        st.info("Record some transactions first to generate insights.")
    else:
        expense_rows = df[df["transaction_type"] == "Expense"]
        if not expense_rows.empty:
            category_totals = expense_rows.groupby("category")["amount"].sum().sort_values(ascending=False)
            biggest_category = category_totals.index[0]
            biggest_amount = float(category_totals.iloc[0])
            st.markdown(f"""
            <div class="ft-insight">
              <div class="ft-insight-label">TOP SPENDING CATEGORY</div>
              <div style="font-size:24px;font-weight:800;margin-top:7px;">{biggest_category}</div>
              <div class="ft-insight-text">You have recorded {money(biggest_amount)} in this category.</div>
            </div>
            """, unsafe_allow_html=True)
        if income_total > 0:
            st.progress(min(max(savings_rate / 100, 0.0), 1.0), text=f"Savings rate: {savings_rate:.1f}%")
            if savings_rate < 0:
                st.warning("Your recorded expenses are higher than your recorded income.")
            elif savings_rate < 20:
                st.info("Your recorded savings rate is below 20%. Review spending categories to identify possible changes.")
            else:
                st.success("Your recorded savings rate is 20% or higher. Keep tracking consistently.")
        else:
            st.info("Add an income transaction to calculate a savings rate.")

# -------------------- ABOUT THIS PROJECT ------------------

elif page == "About This Project":
    st.title("About FinTrack")
    st.caption("A college project demonstrating Python-based data management and analytics.")

    st.markdown("""
    <div class="ft-hero">
      <div class="ft-eyebrow">Project overview</div>
      <h1>Personal finance, made visible.</h1>
      <p>FinTrack records transactions, calculates financial summaries, and turns data into visual insights.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Technology stack")
    t1, t2, t3, t4 = st.columns(4)
    t1.metric("Language", "Python")
    t2.metric("Interface", "Streamlit")
    t3.metric("Database", "SQLite")
    t4.metric("Analytics", "Pandas + Plotly")

    st.markdown("### How the application works")
    st.markdown("""
    1. **Input:** A user chooses a transaction type, category, date, amount, and description.
    2. **Validation:** Python checks that the amount is greater than zero.
    3. **Storage:** SQLite inserts the transaction into the database.
    4. **Processing:** Pandas loads and filters the stored records.
    5. **Calculation:** Python calculates income, expenses, net savings, and savings rate.
    6. **Visualisation:** Plotly creates interactive charts from the transaction data.
    """)

    st.markdown("### Key formulas")
    st.code(
        "Total Income = Sum of all Income transactions\n"
        "Total Expenses = Sum of all Expense transactions\n"
        "Net Savings = Total Income - Total Expenses\n"
        "Savings Rate = (Net Savings / Total Income) × 100",
        language="text",
    )

    st.markdown("### Example database structure")
    st.code(
        "transactions(\n"
        "  id INTEGER PRIMARY KEY,\n"
        "  transaction_date TEXT,\n"
        "  transaction_type TEXT,\n"
        "  category TEXT,\n"
        "  amount REAL,\n"
        "  description TEXT\n"
        ")",
        language="sql",
    )
    st.info("Educational note: FinTrack is a personal tracking tool. It does not connect to banks or provide regulated financial advice.")

st.markdown("<div class='ft-footer'>FINTRACK · A PYTHON FINANCE & ANALYTICS PROJECT</div>", unsafe_allow_html=True)
