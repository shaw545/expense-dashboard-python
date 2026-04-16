import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
from io import BytesIO

st.set_page_config(page_title="Expense Dashboard", page_icon="💰", layout="wide")

st.title("💰 General Expense Dashboard")

# Session state
if "expenses" not in st.session_state:
    st.session_state.expenses = []

st.markdown("Enter expenses in this format: `category description amount`")
st.markdown("Example: `food lunch 30` or `phone bill 15`")

# Input section
col_input1, col_input2 = st.columns([2, 1])

with col_input1:
    user_input = st.text_input("Add Expense")

with col_input2:
    expense_date = st.date_input("Expense Date", value=date.today())

col1, col2 = st.columns([1, 1])

with col1:
    add_clicked = st.button("Add Expense")

with col2:
    clear_clicked = st.button("Clear All")

# Add expense
if add_clicked and user_input:
    text = user_input.strip().lower()
    parts = text.split()

    if len(parts) >= 2:
        try:
            amount = float(parts[-1])
            category = parts[0]
            description = " ".join(parts[1:-1]) if len(parts) > 2 else category

            st.session_state.expenses.append({
                "Date": expense_date.strftime("%Y-%m-%d"),
                "Category": category.title(),
                "Description": description.title(),
                "Amount": amount
            })

            st.success(
                f"Added: {category.title()} | {description.title()} | ${amount:.2f}"
            )
        except ValueError:
            st.error("Invalid format. Use: category description amount")
    else:
        st.error("Please enter at least category and amount.")

# Clear all
if clear_clicked:
    st.session_state.expenses = []
    st.warning("All expenses cleared.")
    st.rerun()

# Display dashboard if expenses exist
if st.session_state.expenses:
    df = pd.DataFrame(st.session_state.expenses)

    # Filters
    st.subheader("Filters")

    filter_col1, filter_col2 = st.columns([1, 1])

    with filter_col1:
        category_options = ["All"] + sorted(df["Category"].unique().tolist())
        selected_category = st.selectbox("Filter by Category", category_options)

    with filter_col2:
        selected_date = st.selectbox(
            "Filter by Date",
            ["All"] + sorted(df["Date"].unique().tolist())
        )

    filtered_df = df.copy()

    if selected_category != "All":
        filtered_df = filtered_df[filtered_df["Category"] == selected_category]

    if selected_date != "All":
        filtered_df = filtered_df[filtered_df["Date"] == selected_date]

    # Metrics
    total_expenses = filtered_df["Amount"].sum()
    total_items = len(filtered_df)
    avg_expense = filtered_df["Amount"].mean() if total_items > 0 else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Expenses", f"${total_expenses:.2f}")
    c2.metric("Number of Entries", total_items)
    c3.metric("Average Expense", f"${avg_expense:.2f}")

    # Expense records with delete
    st.subheader("Expense Records")
    st.write("Click ❌ to delete an expense")

    h1, h2, h3, h4, h5 = st.columns([2, 2, 3, 2, 1])
    h1.markdown("**Date**")
    h2.markdown("**Category**")
    h3.markdown("**Description**")
    h4.markdown("**Amount**")
    h5.markdown("**Remove**")

    for i, row in filtered_df.reset_index().iterrows():
        original_index = row["index"]
        col1, col2, col3, col4, col5 = st.columns([2, 2, 3, 2, 1])

        col1.write(row["Date"])
        col2.write(row["Category"])
        col3.write(row["Description"])
        col4.write(f"${row['Amount']:.2f}")

        if col5.button("❌", key=f"delete_{original_index}"):
            st.session_state.expenses.pop(original_index)
            st.rerun()

    # Category summary
    summary_df = (
        filtered_df.groupby("Category", as_index=False)["Amount"]
        .sum()
        .sort_values("Amount", ascending=False)
    )

    st.subheader("Category Summary")
    st.dataframe(summary_df, use_container_width=True)

    # Charts
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Bar Chart")
        fig_bar, ax_bar = plt.subplots(figsize=(6, 4))
        ax_bar.bar(summary_df["Category"], summary_df["Amount"])
        ax_bar.set_xlabel("Category")
        ax_bar.set_ylabel("Amount ($)")
        ax_bar.set_title("Expenses by Category")
        plt.xticks(rotation=45)
        st.pyplot(fig_bar)

    with chart_col2:
        st.subheader("Pie Chart")
        fig_pie, ax_pie = plt.subplots(figsize=(6, 4))
        ax_pie.pie(
            summary_df["Amount"],
            labels=summary_df["Category"],
            autopct="%1.1f%%",
            startangle=90
        )
        ax_pie.set_title("Expense Share by Category")
        st.pyplot(fig_pie)

    # Trend chart
    st.subheader("📈 Expense Trend Over Time")

    trend_df = filtered_df.copy()
    trend_df["Date"] = pd.to_datetime(trend_df["Date"])
    trend_df = trend_df.groupby("Date", as_index=False)["Amount"].sum()
    trend_df = trend_df.sort_values("Date")

    fig_line, ax_line = plt.subplots(figsize=(8, 4))
    ax_line.plot(trend_df["Date"], trend_df["Amount"], marker="o")
    ax_line.set_xlabel("Date")
    ax_line.set_ylabel("Amount ($)")
    ax_line.set_title("Daily Expense Trend")
    plt.xticks(rotation=45)
    st.pyplot(fig_line)

    # Downloads
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Filtered Expenses as CSV",
        data=csv,
        file_name="filtered_expenses.csv",
        mime="text/csv"
    )

    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        filtered_df.to_excel(writer, index=False, sheet_name="Expenses")
        summary_df.to_excel(writer, index=False, sheet_name="Summary")
        trend_df.to_excel(writer, index=False, sheet_name="Trend")

    st.download_button(
        label="Download Filtered Expenses as Excel",
        data=excel_buffer.getvalue(),
        file_name="filtered_expenses.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("No expenses added yet.")