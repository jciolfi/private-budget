from datetime import datetime
import pandas as pd
from classes import Month
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
from calendar import monthrange


class Reporter:
    def __init__(self):
        pass
    
    # ------------ HELPERS ------------
    # import data and split into income and expenses
    def split_spend_income(self, filepath):
        data = pd.read_csv(filepath)
        data_income = data[data["Category"].str.contains("income|salary|invest", case=False, regex=True)]
        data_spend = data[~data["Category"].str.contains("income|salary|invest", case=False, regex=True)]
        return data, data_income, data_spend
    
    # create a piechart with the given data and title
    def create_spend_piechart(self, data, title):
        fig = px.pie(data, values="Amount", names="Category", title=title)
        return pio.to_html(fig, full_html=False, include_plotlyjs="cdn")
    
    # create linechart of cumulative spend per day for this month
    def create_cumulative_linechart(self, spend_data, title):
        data = spend_data.copy()
        data["Date"] = pd.to_datetime(data["Date"], format="%d %b %Y")
        data.sort_values("Date", inplace=True)
        data["Cumulative Spend"] = data["Amount"].cumsum()
        
        total_spend = data["Cumulative Spend"].iloc[-1]
        year = data["Date"].iloc[0].year
        month = data["Date"].iloc[0].month
        days_in_month = monthrange(year, month)[1]
        
        # insert into front and end to make actual spend look better
        front_padding = pd.DataFrame([{
            "Date": datetime(year, month, 1),
            "Description": "front_padding", 
            "Category": "n/a",
            "Amount": 0, 
            "Cumulative Spend": 0
        }])
        end_padding = pd.DataFrame([{
            "Date": datetime(year, month, days_in_month),
            "Description": "", 
            "Category": "n/a",
            "Amount": 0,
            "Cumulative Spend": total_spend
        }])
        data = pd.concat([front_padding, data, end_padding], ignore_index=True)
        print(data)
        
        fig = go.Figure()
        fig.update_layout(title=title, xaxis_title="Time", yaxis_title="Amount")
        
        fig.add_trace(go.Scatter(x=data["Date"], y=data["Cumulative Spend"], mode="lines", name="Actual Spend"))
        fig.add_trace(go.Scatter(x=[data["Date"].iloc[0].replace(day=1), data["Date"].iloc[0].replace(day=days_in_month)], 
                             y=[0, total_spend], 
                             mode="lines",
                             line=dict(color="red", dash="dash"),
                             name="Average Spend"))
        
        
        
        return pio.to_html(fig, full_html=False, include_plotlyjs="cdn")
    
    
    # create bar charts to compare target vs. actual spend: per category and aggregated
    def category_comparison_barcharts(self, month, year, target, target_income, target_spend, actual, actual_income, actual_spend):
        # bar chart comparing spend per category
        merged_df = target.merge(actual, on="Category", how="outer", suffixes=("_target", "_actual"))
        categories_fig = go.Figure(data=[
            go.Bar(name="target", x=merged_df["Category"], y=merged_df["Amount_target"]),
            go.Bar(name="actual", x=merged_df["Category"], y=merged_df["Amount_actual"])
        ])
        categories_fig.update_layout(barmode="group", title=f"Target vs. Actual Spend for {month.value[1]} {year}", xaxis_title="Category", yaxis_title="Amount")
        categories_html = pio.to_html(categories_fig, full_html=False, include_plotlyjs="cdn")
        
        # bar chart comparing total target vs. actual income/spend
        totals_fig = go.Figure(data=[
            go.Bar(name="target", x=["Income", "Spend"], y=[target_income["Amount"].sum(), target_spend["Amount"].sum()]),
            go.Bar(name="actual", x=["Income", "Spend"], y=[actual_income["Amount"].sum(), actual_spend["Amount"].sum()])
        ])
        totals_fig.update_layout(barmode="group", title=f"Net Difference for {month.value[1]} {year}", xaxis_title="Category", yaxis_title="Amount")
        totals_html = pio.to_html(totals_fig, full_html=False, include_plotlyjs="cdn")
        
        return categories_html, totals_html
    
    
    # create report with data visualizations for target vs. actual spend
    def create_report(self, month, year=None):
        if not year:
            year = datetime.now().date().year
        
        target, target_income, target_spend = self.split_spend_income(f"goals/{month.value[1]}_{year}.csv")
        actual_raw, actual_income, actual_spend_raw = self.split_spend_income(f"actual/{month.value[1]}_{year}.csv")        
        actual_spend = actual_spend_raw.groupby("Category")["Amount"].sum().reset_index()
        actual = actual_raw.groupby("Category")["Amount"].sum().reset_index()
        
        target_spend_piechart_html = self.create_spend_piechart(target_spend, f"Target Spend for {month.value[1]} {year}")
        actual_spend_piechart_html = self.create_spend_piechart(actual_spend, f"Actual Spend for {month.value[1]} {year}")
        actual_spend_linechart_html = self.create_cumulative_linechart(actual_spend_raw, f"Cumulative Spend for {month.value[1]} {year}")
        categories_html, totals_html = self.category_comparison_barcharts(month, year, target, target_income, target_spend, actual, actual_income, actual_spend)
        
        # create report
        report = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{month.value[1]} {year} Report</title>
            <style>
                .chart-container {{
                    margin-bottom: 50px;
                    margin: auto;
                    width: 66%;
                    font-family: verdana, georgia;
                }}
            </style>
        </head>
        <body>
            <div class="chart-container">
                <h2>Cumulative Spend</h2>
                {actual_spend_linechart_html}
            </div>
            <div class="chart-container">
                <h2>Target Spend Breakdown</h2>
                {target_spend_piechart_html}
            </div>
            <div class="chart-container">
                <h2>Actual Spend Breakdown</h2>
                {actual_spend_piechart_html}
            </div>
            <div class="chart-container">
                <h2>Spend Comparison</h2>
                {categories_html}
            </div>
            <div class="chart-container">
                <h2>Net Difference</h2>
                {totals_html}
            </div>
        </body>
        </html>
        """
        
        with open(f"reports/{month.value[1]}_{year}.html", "w") as out_file:
            out_file.write(report)
        
        
if __name__ == "__main__":
    r = Reporter()
    
    r.create_report(Month.DEC, 2023)
    # r.spending_breakdown(Month.JUN, 2023)
    # r.spending_breakdown(Month.JUL, 2023)
    # r.spending_breakdown(Month.AUG, 2023)
    # r.spending_breakdown(Month.OCT, 2023)
    # r.spending_breakdown(Month.NOV, 2023)
    # r.spending_breakdown(Month.DEC, 2023)
    # r.target_spending_breakdown(Month.JAN, 2024)