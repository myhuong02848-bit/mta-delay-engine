import os
import sqlite3
import pandas as pd
from datetime import datetime

class MTADelayIngestor:
    def __init__(self, raw_data_path: str, db_path: str = "data/processed/mta_delays.db"):
        self.raw_data_path = raw_data_path
        self.db_path = db_path
        
        # Ensure processed directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def load_raw_data(self) -> pd.DataFrame:
        """Loads CSV or Excel data into a pandas DataFrame."""
        if not os.path.exists(self.raw_data_path):
            raise FileNotFoundError(f"Source file not found at: {self.raw_data_path}")
        
        print(f"[{datetime.now().strftime('%X')}] Loading raw dataset...")
        if self.raw_data_path.endswith('.xlsx') or self.raw_data_path.endswith('.xls'):
            df = pd.read_excel(self.raw_data_path)
        else:
            df = pd.read_csv(self.raw_data_path)
            
        print(f"[{datetime.now().strftime('%X')}] Loaded {len(df):,} raw records.")
        return df

    def clean_and_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardizes column names, parses dates, and handles missing data."""
        print(f"[{datetime.now().strftime('%X')}] Raw columns detected: {df.columns.tolist()}")
        print(f"[{datetime.now().strftime('%X')}] Transforming and validating schema...")
        
        # Normalize column headers
        df.columns = [col.strip().lower().replace(' ', '_').replace('-', '_') for col in df.columns]
        
        # 1. Standardize date column
        date_candidates = [col for col in df.columns if any(k in col for k in ['date', 'month', 'year', 'period', 'time'])]
        if date_candidates:
            primary_date_col = date_candidates[0]
            df['record_date'] = pd.to_datetime(df[primary_date_col], errors='coerce')
            df['year'] = df['record_date'].dt.year
            df['month'] = df['record_date'].dt.month
            df['year_month'] = df['record_date'].dt.to_period('M').astype(str)
        else:
            raise KeyError(f"Could not find a date column in: {df.columns.tolist()}")

        # 2. Standardize subway line identifier
        line_candidates = [col for col in df.columns if any(k in col for k in ['line', 'route', 'subway_line', 'train', 'division'])]
        if line_candidates:
            primary_line_col = line_candidates[0]
            df['line'] = df[primary_line_col].astype(str).str.strip().str.upper()
        else:
            raise KeyError(f"Could not find a subway line column in: {df.columns.tolist()}")

        # 3. Standardize delay metric (fallback to any count/numeric column)
        count_candidates = [col for col in df.columns if any(k in col for k in ['delay', 'count', 'num', 'total', 'incidents', 'value', 'trips'])]
        if count_candidates:
            primary_count_col = count_candidates[0]
            df['delays'] = pd.to_numeric(df[primary_count_col], errors='coerce').fillna(0).astype(int)
        else:
            # Fallback: find the first numeric column
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if numeric_cols:
                df['delays'] = df[numeric_cols[0]].fillna(0).astype(int)
            else:
                raise KeyError(f"Could not find a numeric delay metric column in: {df.columns.tolist()}")

        # Drop rows missing essential identifiers
        initial_count = len(df)
        df = df.dropna(subset=['line', 'delays'])
        dropped_count = initial_count - len(df)
        if dropped_count > 0:
            print(f"[{datetime.now().strftime('%X')}] Dropped {dropped_count} rows with missing line/delay data.")

        return df

    def save_to_sqlite(self, df: pd.DataFrame, table_name: str = "subway_delays"):
        """Saves cleaned DataFrame to SQLite with B-Tree indexes for fast querying."""
        print(f"[{datetime.now().strftime('%X')}] Writing data to SQLite at '{self.db_path}'...")
        
        with sqlite3.connect(self.db_path) as conn:
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            
            cursor = conn.cursor()
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_line ON {table_name} (line);")
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_year_month ON {table_name} (year_month);")
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_line_date ON {table_name} (line, year_month);")
            conn.commit()
            
        print(f"[{datetime.now().strftime('%X')}] Ingestion complete! Database table '{table_name}' indexed successfully.")


if __name__ == "__main__":
    # Point this to the exact file name you placed in data/raw/
    RAW_PATH = "data/raw/MTA_Subway_Delay-Causing_Incidents__Beginning_2020_20260828.csv" 
    
    ingestor = MTADelayIngestor(raw_data_path=RAW_PATH)
    raw_df = ingestor.load_raw_data()
    clean_df = ingestor.clean_and_transform(raw_df)
    ingestor.save_to_sqlite(clean_df)