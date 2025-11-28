import streamlit as st
import pandas as pd

st.title("Ranklist Generator")

uploaded_file = st.file_uploader("Upload Excel/CSV File", type=["xlsx", "xls", "csv"])

if uploaded_file:
    fname = uploaded_file.name.lower()

    # Load safely
    if fname.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file, engine="openpyxl")

    df.columns = [c.strip().replace(" ", "_").lower() for c in df.columns]

    # Ensure correct types
    df["dob"] = pd.to_datetime(df["dob"], dayfirst=True, errors="coerce")
    df["right"] = df["right"].astype(int)
    df["wrong"] = df["wrong"].astype(int)

    # Aggregate per candidate
    summary = df.groupby(["roll_no", "appl_no", "dob"]).agg(
        total_correct=("right", "sum"),
        total_wrong=("wrong", "sum")
    ).reset_index()

    # ⭐ Correct scoring rule: correct - wrong
    summary["total_score"] = summary["total_correct"] - summary["total_wrong"]

    # Ranking rules:
    # 1) Higher score
    # 2) Higher correct responses
    # 3) Older DOB (earlier date)
    summary = summary.sort_values(
        by=["total_score", "total_correct", "dob"],
        ascending=[False, False, True]
    ).reset_index(drop=True)

    summary["rank"] = summary.index + 1

    st.subheader("Rank List")
    st.dataframe(summary)

    # Download option
    csv = summary.to_csv(index=False)
    st.download_button("Download Ranklist", csv, "ranklist.csv", "text/csv")
