import streamlit as st
import pandas as pd

st.title("Ranklist Generator")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Clean column names
    df.columns = [c.strip().replace(" ", "_").lower() for c in df.columns]

    # Expecting columns: roll_no, appl_no, qiuestion_no, right, wrong, dob
    required_cols = ["roll_no", "appl_no", "qiuestion_no", "right", "wrong", "dob"]

    if not all(col in df.columns for col in required_cols):
        st.error("Excel must contain columns: " + ", ".join(required_cols))
        st.stop()

    # Convert DOB to date
    df["dob"] = pd.to_datetime(df["dob"], dayfirst=True, errors="coerce")

    # Calculate score per question
    df["score"] = df["right"] * 4 + df["wrong"] * (-1)

    # Aggregate for each candidate
    summary = df.groupby(["roll_no", "appl_no", "dob"]).agg(
        total_correct=("right", "sum"),
        total_wrong=("wrong", "sum"),
        total_score=("score", "sum")
    ).reset_index()

    # Ranking Logic
    summary = summary.sort_values(
        by=["total_score", "total_correct", "dob"],
        ascending=[False, False, True]       # higher score, higher correct, older DOB
    ).reset_index(drop=True)

    summary["rank"] = summary.index + 1

    st.subheader("Rank List")
    st.dataframe(summary)

    # Download option
    csv = summary.to_csv(index=False)
    st.download_button("Download Ranklist (CSV)", csv, "ranklist.csv", "text/csv")

