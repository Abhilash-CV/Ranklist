import streamlit as st
import pandas as pd

st.title("Ranklist Generator")

uploaded_file = st.file_uploader("Upload Excel/CSV File", type=["xlsx", "xls", "csv"])

if uploaded_file:
    fname = uploaded_file.name.lower()

    # Load file safely
    if fname.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        try:
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        except ImportError:
            st.error("openpyxl not installed. Convert Excel to CSV and upload again.")
            st.stop()

    df.columns = [c.strip().replace(" ", "_").lower() for c in df.columns]

    required_cols = ["roll_no", "appl_no", "qiuestion_no", "right", "wrong", "dob"]
    if not all(col in df.columns for col in required_cols):
        st.error("Excel must contain columns: " + ", ".join(required_cols))
        st.stop()

    df["dob"] = pd.to_datetime(df["dob"], dayfirst=True, errors="coerce")

    df["score"] = df["right"] * 4 - df["wrong"] * (-1)

    summary = df.groupby(["roll_no", "appl_no", "dob"]).agg(
        total_correct=("right", "sum"),
        total_wrong=("wrong", "sum"),
        total_score=("score", "sum")
    ).reset_index()

    summary = summary.sort_values(
        by=["total_score", "total_correct", "dob"],
        ascending=[False, False, True]
    ).reset_index(drop=True)

    summary["rank"] = summary.index + 1

    st.subheader("Rank List")
    st.dataframe(summary)

    csv = summary.to_csv(index=False)
    st.download_button("Download Ranklist", csv, "ranklist.csv", "text/csv")
