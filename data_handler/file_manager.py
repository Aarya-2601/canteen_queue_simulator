import os
import pandas as pd

def save_csv(df, file_path):
    dirname = os.path.dirname(file_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    df.to_csv(file_path, index=False)
    return file_path

def load_csv(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    return pd.read_csv(file_path)