import pandas as pd
import numpy as np

def missing_values_check(df):
    missing = df.isnull().sum()
    percent = (missing / len(df)) * 100
    result = pd.DataFrame({
        'Missing Count': missing,
        'Missing %': percent.round(2)
    })
    result = result[result['Missing Count'] > 0]
    if result.empty:
        print("✅ No missing values found")
    else:
        print("🔴 Missing Values Found:")
        print(result)
    return result

def duplicate_check(df):
    dup_count = df.duplicated().sum()
    if dup_count == 0:
        print("✅ No duplicates found")
    else:
        print(f"🔴 {dup_count} duplicate rows found")
    return dup_count

def outlier_detection(df):
    numeric_cols = df.select_dtypes(
                   include=[np.number]).columns
    outlier_report = {}
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = df[
            (df[col] < Q1 - 1.5 * IQR) |
            (df[col] > Q3 + 1.5 * IQR)
        ]
        if len(outliers) > 0:
            outlier_report[col] = len(outliers)
            print(f"🟡 {col}: {len(outliers)} "
                  f"outliers found")
    if not outlier_report:
        print("✅ No outliers found")
    return outlier_report

def schema_validator(df):
    schema = pd.DataFrame({
        'Column': df.columns,
        'Data Type': df.dtypes.values,
        'Unique Values': [df[col].nunique()
                         for col in df.columns],
        'Sample Value': [df[col].iloc[0]
                        for col in df.columns]
    })
    print("📋 Dataset Schema:")
    print(schema.to_string())
    return schema

def health_score(df):
    score = 100
    missing_pct = (df.isnull().sum().sum() /
                  (df.shape[0] * df.shape[1]) * 100)
    score -= missing_pct * 2
    dup_pct = df.duplicated().sum() / len(df) * 100
    score -= dup_pct * 2
    numeric_cols = df.select_dtypes(
                   include=[np.number]).columns
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = df[
            (df[col] < Q1 - 1.5 * IQR) |
            (df[col] > Q3 + 1.5 * IQR)
        ]
        outlier_pct = len(outliers) / len(df) * 100
        score -= outlier_pct * 0.5
    score = max(0, round(score, 2))
    if score >= 80:
        print(f"🟢 Health Score: {score}/100 — Good")
    elif score >= 60:
        print(f"🟡 Health Score: {score}/100 "
              f"— Needs Attention")
    else:
        print(f"🔴 Health Score: {score}/100 "
              f"— Critical")
    return score

def full_scan(df):
    print("=" * 50)
    print("🛡️  DATASENTINEL — FULL SCAN REPORT")
    print("=" * 50)
    print(f"\n📊 Dataset: {df.shape[0]} rows × "
          f"{df.shape[1]} columns\n")
    print("\n--- 1. MISSING VALUES ---")
    missing = missing_values_check(df)
    print("\n--- 2. DUPLICATES ---")
    dupes = duplicate_check(df)
    print("\n--- 3. OUTLIERS ---")
    outliers = outlier_detection(df)
    print("\n--- 4. SCHEMA ---")
    schema = schema_validator(df)
    print("\n--- 5. HEALTH SCORE ---")
    score = health_score(df)
    print("\n" + "=" * 50)
    print("✅ SCAN COMPLETE")
    print("=" * 50)
    return {
        'missing': missing,
        'duplicates': dupes,
        'outliers': outliers,
        'schema': schema,
        'health_score': score
    }