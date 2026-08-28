import pytest
import pandas as pd
import sqlite3
import os
from src.ingest import MTADelayIngestor

@pytest.fixture
def sample_raw_dataframe():
    """Provides a mock DataFrame containing common edge cases, mixed types, and dirty column names."""
    return pd.DataFrame({
        " Subway Line ": ["N", "Q", " r ", None, "6"],
        "Month / Year": ["2022-07-01", "2022-08-01", "2023-01-15", "2023-02-01", "invalid_date"],
        " Delays Count ": ["1,200", 450, None, 300, 150]
    })

@pytest.fixture
def ingestor(tmp_path):
    """Instantiates MTADelayIngestor using a temporary SQLite database path."""
    test_db = str(tmp_path / "test_mta.db")
    return MTADelayIngestor(raw_data_path="dummy_path.csv", db_path=test_db)

def test_clean_and_transform_schema(ingestor, sample_raw_dataframe):
    """Tests if columns are properly standardized and invalid records are handled."""
    cleaned_df = ingestor.clean_and_transform(sample_raw_dataframe.copy())

    # Verify standard columns exist
    assert "line" in cleaned_df.columns
    assert "delays" in cleaned_df.columns
    assert "year_month" in cleaned_df.columns

    # Verify string sanitization (uppercase, stripped)
    assert "R" in cleaned_df["line"].values
    assert "N" in cleaned_df["line"].values

    # Verify null lines were dropped
    assert cleaned_df["line"].isna().sum() == 0

def test_delay_metric_numeric_conversion(ingestor, sample_raw_dataframe):
    """Ensures delay counts are converted to integer types and nulls are handled."""
    cleaned_df = ingestor.clean_and_transform(sample_raw_dataframe.copy())

    assert pd.api.types.is_integer_dtype(cleaned_df["delays"])
    assert (cleaned_df["delays"] >= 0).all()

def test_sqlite_persistence_and_indexing(ingestor, sample_raw_dataframe):
    """Verifies that data writes to SQLite and required B-Tree indexes are created."""
    cleaned_df = ingestor.clean_and_transform(sample_raw_dataframe.copy())
    ingestor.save_to_sqlite(cleaned_df, table_name="test_delays")

    # Connect to the test DB and verify table & index existence
    with sqlite3.connect(ingestor.db_path) as conn:
        cursor = conn.cursor()
        
        # Verify row count
        cursor.execute("SELECT COUNT(*) FROM test_delays;")
        count = cursor.fetchone()[0]
        assert count == len(cleaned_df)

        # Verify indexes exist
        cursor.execute("PRAGMA index_list(test_delays);")
        indexes = [row[1] for row in cursor.fetchall()]
        assert "idx_line" in indexes
        assert "idx_year_month" in indexes