import sqlite3
import pandas as pd

class MTADelayAnalyzer:
    def __init__(self, db_path: str = "data/processed/mta_delays.db"):
        self.db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def get_top_delayed_lines(self, top_n: int = 5) -> pd.DataFrame:
        """Identifies subway lines with the highest aggregate delays."""
        query = f"""
            SELECT 
                line,
                SUM(delays) AS total_delays,
                ROUND(AVG(delays), 2) AS avg_delays_per_record,
                ROUND(SUM(delays) * 100.0 / (SELECT SUM(delays) FROM subway_delays), 2) AS pct_of_total_delays
            FROM subway_delays
            GROUP BY line
            ORDER BY total_delays DESC
            LIMIT {top_n};
        """
        with self._get_connection() as conn:
            return pd.read_sql(query, conn)

    def get_monthly_trend_and_peaks(self) -> pd.DataFrame:
        """Calculates monthly delay totals with window-based Month-over-Month (MoM) change."""
        query = """
            WITH monthly_totals AS (
                SELECT 
                    year_month,
                    SUM(delays) AS total_delays
                FROM subway_delays
                GROUP BY year_month
            )
            SELECT 
                year_month,
                total_delays,
                LAG(total_delays) OVER (ORDER BY year_month) AS prev_month_delays,
                ROUND(
                    (total_delays - LAG(total_delays) OVER (ORDER BY year_month)) * 100.0 / 
                    LAG(total_delays) OVER (ORDER BY year_month), 
                    2
                ) AS mom_growth_pct
            FROM monthly_totals
            ORDER BY total_delays DESC;
        """
        with self._get_connection() as conn:
            return pd.read_sql(query, conn)

    def get_yearly_summary(self) -> pd.DataFrame:
        """Calculates annual operational metrics."""
        query = """
            SELECT 
                year,
                SUM(delays) AS total_delays,
                COUNT(DISTINCT line) AS active_lines_tracked,
                ROUND(AVG(delays), 2) AS avg_monthly_line_delays
            FROM subway_delays
            GROUP BY year
            ORDER BY year ASC;
        """
        with self._get_connection() as conn:
            return pd.read_sql(query, conn)


if __name__ == "__main__":
    analyzer = MTADelayAnalyzer()

    print("=" * 60)
    print(" 1. TOP 5 DELAYED SUBWAY LINES")
    print("=" * 60)
    top_lines = analyzer.get_top_delayed_lines(top_n=5)
    print(top_lines.to_string(index=False))

    print("\n" + "=" * 60)
    print(" 2. TOP 5 PEAK DELAY MONTHS & MoM SPIKES")
    print("=" * 60)
    monthly_peaks = analyzer.get_monthly_trend_and_peaks().head(5)
    print(monthly_peaks.to_string(index=False))

    print("\n" + "=" * 60)
    print(" 3. YEAR-OVER-YEAR OPERATIONAL SUMMARY")
    print("=" * 60)
    yearly = analyzer.get_yearly_summary()
    print(yearly.to_string(index=False))
    print("=" * 60)