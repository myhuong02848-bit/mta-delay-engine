import os
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

class MTADelayVisualizer:
    def __init__(self, db_path: str = "data/processed/mta_delays.db", output_dir: str = "reports"):
        self.db_path = db_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def plot_top_lines(self, top_n: int = 10):
        """Generates a horizontal bar chart of the most delayed subway lines."""
        query = f"""
            SELECT line, SUM(delays) AS total_delays
            FROM subway_delays
            GROUP BY line
            ORDER BY total_delays DESC
            LIMIT {top_n};
        """
        with self._get_connection() as conn:
            df = pd.read_sql(query, conn)

        fig = px.bar(
            df,
            x="total_delays",
            y="line",
            orientation="h",
            title=f"Top {top_n} NYC Subway Lines by Total Delays (2020–2024)",
            labels={"total_delays": "Total Delay Incidents", "line": "Subway Line"},
            color="total_delays",
            color_continuous_scale="Reds"
        )
        fig.update_layout(yaxis=dict(autorange="reversed"), template="plotly_white")
        
        output_file = os.path.join(self.output_dir, "top_delayed_lines.html")
        fig.write_html(output_file)
        print(f"Saved: {output_file}")

    def plot_monthly_timeline(self):
        """Generates an interactive time-series timeline of system-wide delays."""
        query = """
            SELECT year_month, SUM(delays) AS total_delays
            FROM subway_delays
            GROUP BY year_month
            ORDER BY year_month ASC;
        """
        with self._get_connection() as conn:
            df = pd.read_sql(query, conn)

        fig = px.line(
            df,
            x="year_month",
            y="total_delays",
            title="NYC Subway System-Wide Delays Timeline (Monthly)",
            labels={"year_month": "Month", "total_delays": "Delay Incidents"},
            markers=True
        )
        fig.update_layout(template="plotly_white", xaxis_tickangle=-45)

        output_file = os.path.join(self.output_dir, "monthly_delay_timeline.html")
        fig.write_html(output_file)
        print(f"Saved: {output_file}")


if __name__ == "__main__":
    visualizer = MTADelayVisualizer()
    visualizer.plot_top_lines()
    visualizer.plot_monthly_timeline()