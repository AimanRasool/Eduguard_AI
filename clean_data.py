import pandas as pd

# Load the dataset
file_path = "EVALUATION - SPRING 2026 - SE-6.csv"
df = pd.read_csv(file_path)

# Make column names unique by appending a counter to duplicates
cols = pd.Series(df.columns)
for dup in cols[cols.duplicated()].unique():
    cols[cols == dup] = [
        f"{dup}_{i}" if i != 0 else dup for i in range(sum(cols == dup))
    ]
df.columns = cols

# Ensure the 'Email' column exists
if "Email" not in df.columns:
    df["Email"] = ""

# Save the cleaned dataset
output_path = "EVALUATION_SPRING_2026_SE-6_Cleaned.csv"
df.to_csv(output_path, index=False)
print(f"Cleaned dataset saved successfully as: {output_path}")