import streamlit as st
import pandas as pd
import numpy as np
from report import generate_pdf_report
from scanner import (missing_values_check,
                     duplicate_check,
                     outlier_detection,
                     schema_validator,
                     health_score)
import os

# ── PAGE CONFIG ──
st.set_page_config(
    page_title="DataSentinel",
    page_icon="🛡️",
    layout="wide"
)

# ── CUSTOM CSS ──
st.markdown("""
    <style>
    .main {background-color: #FAFBFD;}
    .title {
        color: #0D1F3C;
        font-size: 42px;
        font-weight: bold;
    }
    .subtitle {
        color: #0A7EA4;
        font-size: 18px;
    }
    .metric-card {
        background: #EBF1FB;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# ── HEADER ──
st.markdown(
    '<p class="title">🛡️ DataSentinel</p>',
    unsafe_allow_html=True
)
st.markdown(
    '<p class="subtitle">Automated Data Quality '
    'Monitoring System</p>',
    unsafe_allow_html=True
)
st.markdown("---")

# ── SIDEBAR ──
st.sidebar.image(
    "https://img.icons8.com/color/96/shield.png",
    width=80
)
st.sidebar.title("DataSentinel")
st.sidebar.markdown("### Upload Your Data")

uploaded_file = st.sidebar.file_uploader(
    "Choose a CSV file",
    type=['csv']
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Or Use Sample Data")

use_sample = st.sidebar.button(
    "📊 Load Sample HR Dataset"
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Built by Purva Sai**\n\n"
    "[GitHub](https://github.com/purva-code24)"
    " | "
    "[LinkedIn](https://www.linkedin.com/in/"
    "purva-sai-095789249/)"
)

# ── LOAD DATA ──
df = None

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success(f"✅ File uploaded successfully!")

elif use_sample:
    import os
    base_path = os.path.dirname(
        os.path.abspath(__file__)
    )
    df = pd.read_csv(
        os.path.join(base_path, 
        'sample_data', 'HRDataset_v14.csv')
    )
    st.success("✅ Sample HR Dataset loaded!")

# ── MAIN DASHBOARD ──
if df is not None:

    # Dataset Overview
    st.markdown("## 📊 Dataset Overview")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Rows", df.shape[0])
    with col2:
        st.metric("Total Columns", df.shape[1])
    with col3:
        st.metric("Missing Values",
                  df.isnull().sum().sum())
    with col4:
        st.metric("Duplicate Rows",
                  df.duplicated().sum())

    st.markdown("---")

    # Health Score
    st.markdown("## 🏥 Health Score")
    score = health_score(df)

    if score >= 80:
        st.success(f"🟢 Health Score: {score}/100 — Good")
    elif score >= 60:
        st.warning(
            f"🟡 Health Score: {score}/100 "
            f"— Needs Attention"
        )
    else:
        st.error(
            f"🔴 Health Score: {score}/100 — Critical"
        )

    st.progress(int(score))
    st.markdown("---")

    # Tabs for results
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔴 Missing Values",
        "🔵 Duplicates",
        "🟡 Outliers",
        "📋 Schema"
    ])

    with tab1:
        st.markdown("### Missing Values Report")
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        if missing.empty:
            st.success("✅ No missing values found!")
        else:
            missing_df = pd.DataFrame({
                'Column': missing.index,
                'Missing Count': missing.values,
                'Missing %': (
                    missing.values / len(df) * 100
                ).round(2)
            })
            st.dataframe(missing_df, 
                        use_container_width=True)

    with tab2:
        st.markdown("### Duplicate Rows Report")
        dup_count = df.duplicated().sum()
        if dup_count == 0:
            st.success("✅ No duplicates found!")
        else:
            st.error(f"🔴 {dup_count} duplicate "
                    f"rows found")
            st.dataframe(
                df[df.duplicated()],
                use_container_width=True
            )

    with tab3:
        st.markdown("### Outliers Report")
        numeric_cols = df.select_dtypes(
            include=[np.number]).columns
        outlier_data = []
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = df[
                (df[col] < Q1 - 1.5 * IQR) |
                (df[col] > Q3 + 1.5 * IQR)
            ]
            if len(outliers) > 0:
                outlier_data.append({
                    'Column': col,
                    'Outliers Found': len(outliers),
                    'Outlier %': round(
                        len(outliers)/len(df)*100, 2
                    )
                })
        if not outlier_data:
            st.success("✅ No outliers found!")
        else:
            st.dataframe(
                pd.DataFrame(outlier_data),
                use_container_width=True
            )

    with tab4:
        st.markdown("### Schema Report")
        schema_df = pd.DataFrame({
            'Column': df.columns,
            'Data Type': df.dtypes.values,
            'Unique Values': [
                df[col].nunique() 
                for col in df.columns
            ],
            'Sample Value': [
                df[col].iloc[0] 
                for col in df.columns
            ]
        })
        st.dataframe(schema_df,
                    use_container_width=True)

    st.markdown("---")

    # Download PDF Button
    # Download PDF Button
    st.markdown("## 📄 Download Report")
    
    with st.spinner("Generating PDF..."):
        pdf_file = generate_pdf_report(
            df,
            filename="DataSentinel_Report.pdf"
        )
    
    with open("DataSentinel_Report.pdf", "rb") as f:
        pdf_data = f.read()
    
    st.download_button(
        label="📥 Download PDF Report",
        data=pdf_data,
        file_name="DataSentinel_Report.pdf",
        mime="application/pdf"
    )
    st.success("✅ Click button above to download!")

    # ── EMAIL ALERT SECTION ──
    st.markdown("---")
    st.markdown("## 📧 Email Alert")
    
    receiver = st.text_input(
        "Enter email to send alert:",
        placeholder="example@gmail.com"
    )
    
    if st.button("🚨 Send Alert Email"):
        if receiver:
            from alerts import send_alert
            score = health_score(df)
            with st.spinner("Sending email..."):
                sent = send_alert(
                    receiver_email=receiver,
                    df=df,
                    health_score=score,
                    sender_email=
                        "purvasai021@gmail.com",
                    app_password=
                        "ezdr pduv qgue nqvo"
                )
            if sent:
                st.success(
                    "✅ Alert email sent "
                    "successfully!"
                )
            else:
                st.info(
                    "✅ Data quality is good — "
                    "no alert needed!"
                )
        else:
            st.warning(
                "⚠️ Please enter an email address"
            )

else:
    # Welcome screen
    st.markdown("## 👋 Welcome to DataSentinel!")
    st.markdown("""
    ### What does DataSentinel do?
    - 🔴 Detects **missing values** in your dataset
    - 🔵 Finds **duplicate rows** automatically  
    - 🟡 Identifies **outliers** in numeric columns
    - 📋 Validates your **data schema**
    - 🏥 Gives an overall **Health Score out of 100**
    - 📄 Generates a **downloadable PDF report**
    
    ### How to use?
    1. Upload your CSV file from the sidebar
    2. Or click **Load Sample HR Dataset**
    3. View your complete data quality report
    4. Download the PDF report
    """)

    st.info(
        "👈 Upload a CSV file or load sample "
        "data from the sidebar to get started!"
    )