import datetime
import pandas as pd
from classes import Month
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go


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
        fig.show()
        return pio.to_html(fig, full_html=False, include_plotlyjs="cdn")
    
    # create linechart of cumulative spend per day for this month
    def create_cumulative_linechart(self, data, title):
        data["Date"] = pd.to_datetime(data["Date"], format="%d %b")
        data.sort_values("Date", inplace=True)
        data["Cumulative Spend"] = data["Amount"].cumsum()
        fig = px.line(data, x="Date", y="Cumulative Spend", title=title)
        fig.show()
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
        categories_fig.show()
        categories_html = pio.to_html(categories_fig, full_html=False, include_plotlyjs="cdn")
        
        # bar chart comparing total target vs. actual income/spend
        totals_fig = go.Figure(data=[
            go.Bar(name="target", x=["Income", "Spend"], y=[target_income["Amount"].sum(), target_spend["Amount"].sum()]),
            go.Bar(name="actual", x=["Income", "Spend"], y=[actual_income["Amount"].sum(), actual_spend["Amount"].sum()])
        ])
        totals_fig.show()
        totals_html = pio.to_html(totals_fig, full_html=False, include_plotlyjs="cdn")
        
        return categories_html, totals_html
    
    
    # create report with data visualizations for target vs. actual spend
    def create_report(self, month, year=None):
        if not year:
            year = datetime.datetime.now().date().year
        
        target, target_income, target_spend = self.split_spend_income(f"goals/{month.value[1]}_{year}.csv")
        actual_raw, actual_income, actual_spend_raw = self.split_spend_income(f"actual/{month.value[1]}_{year}.csv")        
        actual_spend = actual_spend_raw.groupby("Category")["Amount"].sum().reset_index()
        actual = actual_raw.groupby("Category")["Amount"].sum().reset_index()
        
        target_spend_piechart = self.create_spend_piechart(target_spend, f"Target Spend for {month.value[1]} {year}")
        actual_spend_piechart = self.create_spend_piechart(actual_spend, f"Actual Spend for {month.value[1]} {year}")
        actual_spend_linechart = self.create_cumulative_linechart(actual_spend_raw, f"Cumulative Spend for {month.value[2]} {year}")
        
        # target, target_piechart = self.target_spending_breakdown(month, year)
        # actual, actual_piechart, actual_linechart = self.actual_spending_breakdown(month, year)
        categories_html, totals_html = self.category_comparison_barcharts(month, year, target, target_income, target_spend, actual, actual_income, actual_spend)
        
        # create report
        report = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{month} {year} Report</title>
        </head>
        <body>
            <h1>Spend By Category</h1>
            {actual}
        </body>
        </html>
        """
        
        # with open(f"reports/{month.value[1]}_{year}.html", "w") as out_file:
        #     out_file.write(report)
        
        
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