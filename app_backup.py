import sqlite3
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="FinTrack | Personal Finance",
    page_icon="💰",
    layout="wide"
)

DB_NAME = "finance.db"

# ---------------- DATABASE ----------------

def get_connection():
    return sqlite3.connect(DB_NAME)

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
        return pd.read_sql_query(
            "SELECT * FROM transactions ORDER BY transaction_date DESC, id DESC",
            conn
        )

def save_transaction(transaction_date, transaction_type,
                     category, amount, description):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO transactions
            (transaction_date, transaction_type, category, amount, description)
            VALUES (?, ?, ?, ?, ?)
        """, (
            str(transaction_date),
            transaction_type,
            category,
            amount,
            description
        ))

def delete_transaction(transaction_id):
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM transactions WHERE id = ?",
            (transaction_id,)
        )

initialize_database()

# ---------------- DESIGN ----------------

st.markdown("""
<style>
/* Main background */
.stApp {
    background: linear-gradient(135deg, #0b1220 0%, #111827 100%);
    color: #f8fafc;
}

/* Main content spacing */
.block-container {
    max-width: 1400px;
    padding-top: 2.2rem;
    padding-bottom: 3rem;
}

/* Headings */
h1 {
    color: #f8fafc !important;
    font-weight: 800 !important;
    letter-spacing: -1px;
}

h2, h3 {
    color: #e2e8f0 !important;
    font-weight: 700 !important;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #172554, #162033);
    border: 1px solid #334155;
    border-radius: 18px;
    padding: 22px 20px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
    transition: transform 0.2s ease;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    border-color: #38bdf8;
}

[data-testid="stMetricLabel"] {
    color: #cbd5e1 !important;
    font-size: 0.95rem !important;
}

[data-testid="stMetricValue"] {
    color: #7dd3fc !important;
    font-weight: 800 !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0b1120;
    border-right: 1px solid #243047;
}

/* Buttons */
div.stButton > button,
div.stFormSubmitButton > button {
    background: linear-gradient(90deg, #0284c7, #2563eb);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.55rem 1rem;
    font-weight: 700;
    transition: 0.2s ease;
}

div.stButton > button:hover,
div.stFormSubmitButton > button:hover {
    border: none;
    color: white;
    filter: brightness(1.12);
}

/* Input fields */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {
    border-radius: 9px;
}

/* Divider */
hr {
    border-color: #293548;
}

/* Data tables */
[data-testid="stDataFrame"] {
    border: 1px solid #334155;
    border-radius: 12px;
    overflow: hidden;
}

/* Alerts */
div[data-testid="stAlert"] {
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------

st.sidebar.title("💰 FinTrack")
st.sidebar.caption("Your personal finance companion")

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "🏠 Dashboard",
        "➕ Add Transaction",
        "📋 Transaction History",
        "📘 About This Project"
    ]
)

st.sidebar.divider()
st.sidebar.caption("Built with Python and Streamlit")

# ---------------- LOAD DATA ----------------

df = load_transactions()

if not df.empty:
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])
    df["amount"] = pd.to_numeric(df["amount"])

income = (
    df.loc[df["transaction_type"] == "Income", "amount"].sum()
    if not df.empty else 0
)

expenses = (
    df.loc[df["transaction_type"] == "Expense", "amount"].sum()
    if not df.empty else 0
)

savings = income - expenses

# ---------------- DASHBOARD ----------------

if page == "🏠 Dashboard":

    st.markdown("""
    <div style="
        padding: 30px;
        border-radius: 22px;
        background: linear-gradient(115deg, #062f2b, #101a2c 65%, #172554);
        border: 1px solid #087f70;
        margin-bottom: 25px;
    ">
        <div style="color:#34f5c5; font-size:14px; letter-spacing:3px;">
            FINTRACK / PERSONAL FINANCE
        </div>
        <h1 style="margin:12px 0 5px 0;">
            Your Money. Your Future. 🚀
        </h1>
        <p style="color:#cbd5e1; font-size:17px; margin-bottom:0;">
            Take control of your finances with real-time financial insights.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Financial calculations
    income = (
        df.loc[df["transaction_type"] == "Income", "amount"].sum()
        if not df.empty else 0
    )

    expenses = (
        df.loc[df["transaction_type"] == "Expense", "amount"].sum()
        if not df.empty else 0
    )

    savings = income - expenses
    savings_rate = (savings / income * 100) if income > 0 else 0

    # Summary cards
    st.markdown("### ◈ Financial Overview")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown("**💵 TOTAL INCOME**")
        st.markdown(
            f"<h2 style='color:#34f5c5;'>₹{income:,.2f}</h2>"
            "<p style='color:#94a3b8;'>Money received</p>",
            unsafe_allow_html=True
        )

    with c2:
        st.markdown("**💸 TOTAL EXPENSES**")
        st.markdown(
            f"<h2 style='color:#fb7185;'>₹{expenses:,.2f}</h2>"
            "<p style='color:#94a3b8;'>Money spent</p>",
            unsafe_allow_html=True
        )

    with c3:
        st.markdown("**💎 NET SAVINGS**")
        savings_color = "#a78bfa" if savings >= 0 else "#fb7185"
        st.markdown(
            f"<h2 style='color:{savings_color};'>₹{savings:,.2f}</h2>"
            "<p style='color:#94a3b8;'>Income minus expenses</p>",
            unsafe_allow_html=True
        )

    with c4:
        st.markdown("**📈 SAVINGS RATE**")
        st.markdown(
            f"<h2 style='color:#38bdf8;'>{savings_rate:.1f}%</h2>"
            "<p style='color:#94a3b8;'>Of total income</p>",
            unsafe_allow_html=True
        )

    st.divider()

    # Charts
    left, right = st.columns([1, 1.5])

    with left:
        st.markdown("### ◉ Spending Breakdown")

        expense_df = (
            df[df["transaction_type"] == "Expense"]
            if not df.empty else pd.DataFrame()
        )

        if not expense_df.empty:
            category_totals = (
                expense_df.groupby("category", as_index=False)["amount"]
                .sum()
            )

            fig = px.pie(
                category_totals,
                names="category",
                values="amount",
                hole=0.68,
                color_discrete_sequence=[
                    "#34f5c5",
                    "#8b5cf6",
                    "#38bdf8",
                    "#fb7185",
                    "#fbbf24",
                    "#a3e635"
                ]
            )

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=20, b=10, l=10, r=10),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                )
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("Add an expense to unlock your spending analysis.")

    with right:
        st.markdown("### ↗ Income vs Expenses")

        comparison = pd.DataFrame({
            "Type": ["Income", "Expenses"],
            "Amount": [income, expenses]
        })

        fig = px.bar(
            comparison,
            x="Type",
            y="Amount",
            color="Type",
            text="Amount",
            color_discrete_map={
                "Income": "#34f5c5",
                "Expenses": "#fb7185"
            }
        )

        fig.update_traces(
            texttemplate="₹%{y:,.0f}",
            textposition="outside",
            marker_line_width=0
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            margin=dict(t=25, b=10, l=5, r=15),
            yaxis_title="Amount (₹)",
            xaxis_title="",
            yaxis=dict(
                gridcolor="rgba(148,163,184,0.12)",
                zeroline=False
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Financial insights
    st.markdown("### ✦ Your Financial Intelligence")

    insight_col, action_col = st.columns([1.5, 1])

    with insight_col:
        if income == 0 and expenses == 0:
            insight_message = (
                "Your financial journey starts here. "
                "Add your first income or expense to unlock insights."
            )
            insight_icon = "🚀"

        elif savings < 0:
            insight_message = (
                f"Your expenses exceed your income by ₹{abs(savings):,.2f}. "
                "Review your spending and look for ways to reduce expenses."
            )
            insight_icon = "⚠️"

        elif income > 0 and savings_rate >= 30:
            insight_message = (
                f"Great progress! You're retaining {savings_rate:.1f}% "
                "of your recorded income. Keep building healthy money habits."
            )
            insight_icon = "💎"

        elif income > 0:
            insight_message = (
                f"Your current savings rate is {savings_rate:.1f}%. "
                "Review your expenses to find opportunities to save more."
            )
            insight_icon = "💡"

        else:
            insight_message = (
                "You've recorded expenses. Add your income to calculate "
                "your savings rate."
            )
            insight_icon = "📊"

        st.markdown(
            f"""
            <div style="
                background:linear-gradient(120deg,#102d31,#111827);
                border:1px solid #176e67;
                border-radius:18px;
                padding:22px;
                min-height:145px;
            ">
                <div style="font-size:28px;">{insight_icon}</div>
                <h4 style="color:#34f5c5;">FinTrack Insight</h4>
                <p style="color:#e2e8f0;">{insight_message}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with action_col:
        st.markdown(
            """
            <div style="
                background:linear-gradient(135deg,#172554,#312e81);
                border:1px solid #4f46e5;
                border-radius:18px;
                padding:22px;
                min-height:145px;
            ">
                <h3 style="color:#c4b5fd;">✦ The FinTrack Goal</h3>
                <p style="color:#e2e8f0;">
                    Track consistently.<br>
                    Spend intentionally.<br>
                    Build your financial future.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Recent transactions
    st.divider()
    st.markdown("### ◷ Recent Transactions")

    if df.empty:
        st.info("Your latest transactions will appear here.")

    else:
        recent = df.head(5).copy()

        recent["transaction_date"] = pd.to_datetime(
            recent["transaction_date"]
        ).dt.strftime("%d %b %Y")

        recent["amount"] = recent.apply(
            lambda row: (
                f"+ ₹{row['amount']:,.2f}"
                if row["transaction_type"] == "Income"
                else f"- ₹{row['amount']:,.2f}"
            ),
            axis=1
        )

        st.dataframe(
            recent[[
                "transaction_date",
                "transaction_type",
                "category",
                "amount",
                "description"
            ]],
            use_container_width=True,
            hide_index=True
        )

    st.caption(
        "FINTRACK • Plan better. Spend smarter. Build your future."
    )
# ---------------- ADD TRANSACTION ----------------

elif page == "➕ Add Transaction":

    st.title("➕ Add a Transaction")
    st.write("Record your income and expenses.")

    transaction_type = st.selectbox(
        "Transaction Type",
        ["Income", "Expense"]
    )

    categories = {
        "Income": [
            "Salary",
            "Business",
            "Freelancing",
            "Investment",
            "Other Income"
        ],
        "Expense": [
            "Food",
            "Travel",
            "Shopping",
            "Education",
            "Bills",
            "Healthcare",
            "Entertainment",
            "Other Expense"
        ]
    }

    category = st.selectbox(
        "Category",
        categories[transaction_type]
    )

    with st.form("transaction_form"):

        transaction_date = st.date_input(
            "Transaction Date",
            value=date.today()
        )

        amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            value=0.0,
            step=100.0
        )

        description = st.text_input(
            "Description",
            placeholder="Example: Monthly salary"
        )

        submitted = st.form_submit_button(
            "💾 Save Transaction",
            use_container_width=True
        )

        if submitted:
            if amount <= 0:
                st.error("Please enter an amount greater than zero.")
            else:
                save_transaction(
                    transaction_date,
                    transaction_type,
                    category,
                    amount,
                    description.strip()
                )

                st.success("Transaction saved successfully! 🎉")
                st.rerun()

# ---------------- TRANSACTION HISTORY ----------------

elif page == "📋 Transaction History":

    st.title("📋 Transaction History")
    st.write("Review, filter, and download your financial records.")

    if df.empty:
        st.info("No transactions found. Add your first transaction!")

    else:
        # Convert dates into a consistent format
        history_df = df.copy()
        history_df["transaction_date"] = pd.to_datetime(
            history_df["transaction_date"]
        )

        # Month and year filters
        st.subheader("📅 Monthly Report")

        col1, col2 = st.columns(2)

        with col1:
            selected_month = st.selectbox(
                "Select Month",
                list(range(1, 13)),
                index=date.today().month - 1,
                format_func=lambda m: date(2000, m, 1).strftime("%B")
            )

        with col2:
            available_years = sorted(
                history_df["transaction_date"].dt.year.unique().tolist(),
                reverse=True
            )

            selected_year = st.selectbox(
                "Select Year",
                available_years,
                index=(
                    available_years.index(date.today().year)
                    if date.today().year in available_years else 0
                )
            )

        # Filter transactions by selected month and year
        monthly_df = history_df[
            (history_df["transaction_date"].dt.month == selected_month)
            & (history_df["transaction_date"].dt.year == selected_year)
        ].copy()

        monthly_income = monthly_df.loc[
            monthly_df["transaction_type"] == "Income", "amount"
        ].sum()

        monthly_expenses = monthly_df.loc[
            monthly_df["transaction_type"] == "Expense", "amount"
        ].sum()

        monthly_savings = monthly_income - monthly_expenses

        # Monthly financial summary
        st.subheader("💰 Monthly Financial Summary")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Monthly Income",
            f"₹{monthly_income:,.2f}"
        )

        col2.metric(
            "Monthly Expenses",
            f"₹{monthly_expenses:,.2f}"
        )

        col3.metric(
            "Monthly Savings",
            f"₹{monthly_savings:,.2f}"
        )

        st.divider()

        # Transaction type filter
        filter_type = st.selectbox(
            "Filter by Transaction Type",
            ["All", "Income", "Expense"]
        )

        filtered_df = monthly_df.copy()

        if filter_type != "All":
            filtered_df = filtered_df[
                filtered_df["transaction_type"] == filter_type
            ]

        st.subheader("🧾 Transactions")

        if filtered_df.empty:
            st.info("No transactions match your selected filters.")

        else:
            display_df = filtered_df.copy()

            display_df["transaction_date"] = (
                display_df["transaction_date"].dt.strftime("%Y-%m-%d")
            )

            st.dataframe(
                display_df[
                    [
                        "id",
                        "transaction_date",
                        "transaction_type",
                        "category",
                        "amount",
                        "description"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

            # Download filtered transactions
            csv_data = display_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="📥 Download Monthly Report (CSV)",
                data=csv_data,
                file_name=(
                    f"FinTrack_{selected_year}_"
                    f"{selected_month:02d}.csv"
                ),
                mime="text/csv",
                use_container_width=True
            )

            # Delete transaction
            st.divider()
            st.subheader("🗑️ Delete a Transaction")

            selected_id = st.selectbox(
                "Select Transaction ID",
                filtered_df["id"].tolist()
            )

            confirm_delete = st.checkbox(
                "I confirm that I want to delete this transaction."
            )

            if st.button("Delete Transaction"):
                if confirm_delete:
                    delete_transaction(selected_id)
                    st.success("Transaction deleted successfully!")
                    st.rerun()
                else:
                    st.warning("Please confirm before deleting.")

# ---------------- ABOUT THIS PROJECT ----------------

elif page == "📘 About This Project":

    st.title("📘 About FinTrack")

    st.write("""
    **FinTrack** is a Personal Finance Manager developed as a college project.

    It helps users record income and expenses, monitor savings,
    view transaction history, and understand spending patterns.
    """)

    st.subheader("🛠️ Technologies Used")

    st.markdown("""
    - **Python:** Main programming language.
    - **Streamlit:** Builds the interactive web interface.
    - **SQLite:** Stores financial transactions.
    - **Pandas:** Processes and analyses transaction data.
    - **Plotly:** Creates interactive financial charts.
    """)

    st.subheader("🧮 Financial Calculations")

    st.code("""
Total Income = Sum of all income transactions

Total Expenses = Sum of all expense transactions

Net Savings = Total Income - Total Expenses

Savings Rate = (Net Savings / Total Income) * 100
    """, language="text")

    st.subheader("🔄 How the App Works")

    st.markdown("""
    1. The user enters a transaction.
    2. Python validates the amount.
    3. SQLite stores the transaction.
    4. Pandas loads and processes the data.
    5. Python calculates income, expenses, and savings.
    6. Plotly displays financial charts on the dashboard.
    """)

    st.info("This application is an educational project. It does not connect to bank accounts.")