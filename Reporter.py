from datetime import datetime
import pandas as pd
from classes import Month
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
from calendar import monthrange
from os.path import exists

class Reporter:
    def __init__(self):
        pass
    
    # ------------ HELPERS ------------
    # import data and split into income and expenses
    def split_spend_income(self, filepaths):
        for filepath in filepaths:
            if not exists(filepath):
                continue
            
            data = pd.read_csv(filepath)
            data_income = data[data["Category"].str.contains("income|salary|invest", case=False, regex=True)]
            data_spend = data[~data["Category"].str.contains("income|salary|invest", case=False, regex=True)]
            return data, data_income, data_spend
            
        print(f"Could not find any filepaths: {', '.join(filepaths)}")
        exit(1)
    
    def round_money(self, money):
        return round(money, 2)
    
    
    # ------------ BLURBS ------------
    def generate_cumulative_blurb(self, total_spend, days_in_month):
        return f"You spent ${self.round_money(total_spend)} this month, for a daily average spend of ${self.round_money(total_spend / days_in_month)}."
    
    def generate_spend_blurb(self, data, num_top=3):
        top_categories = data.sort_values(by='Amount', ascending=False).head(num_top)
        res = []
        for _, cat in top_categories.iterrows():
            res.append(f'{cat["Category"]} (${self.round_money(cat["Amount"])})')
        
        return f"Your top categories were: {', '.join(res[:-1])}, and {res[-1]}."
    
    def generate_per_category_blurb(self, merged_df):
        return f""
    
    def generate_totals_blurb(self, tot_target_income, tot_target_spend, tot_actual_income, tot_actual_spend):
        return f""
    
    # ------------ FIGURES ------------
    # create a piechart with the given data and title
    def create_spend_piechart(self, data, title):
        fig = px.pie(data, values="Amount", names="Category", title=title)
        return pio.to_html(fig, full_html=False, include_plotlyjs="cdn"), self.generate_spend_blurb(data)
    
    
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
            "Description": "end_padding", 
            "Category": "n/a",
            "Amount": 0,
            "Cumulative Spend": total_spend
        }])
        data = pd.concat([front_padding, data, end_padding], ignore_index=True)
        
        fig = go.Figure()
        fig.update_layout(title=title, xaxis_title="Time", yaxis_title="Amount")
        
        fig.add_trace(go.Scatter(x=data["Date"], y=data["Cumulative Spend"], mode="lines", name="Actual Spend"))
        fig.add_trace(go.Scatter(x=[data["Date"].iloc[0].replace(day=1), data["Date"].iloc[0].replace(day=days_in_month)], 
                             y=[0, total_spend],
                             mode="lines",
                             line=dict(color="red", dash="dash"),
                             name="Average Spend"))
        
        
        return pio.to_html(fig, full_html=False, include_plotlyjs="cdn"), self.generate_cumulative_blurb(total_spend, days_in_month)
    
    
    def create_per_category_barchart(self, month, year, target, actual):
        merged_df = target.merge(actual, on="Category", how="outer", suffixes=("_target", "_actual"))
        categories_fig = go.Figure(data=[
            go.Bar(name="target", x=merged_df["Category"], y=merged_df["Amount_target"]),
            go.Bar(name="actual", x=merged_df["Category"], y=merged_df["Amount_actual"])
        ])
        categories_fig.update_layout(barmode="group", title=f"Target vs. Actual Spend for {month.value[1]} {year}", xaxis_title="Category", yaxis_title="Amount")
        chart_html = pio.to_html(categories_fig, full_html=False, include_plotlyjs="cdn")
        return chart_html, self.generate_per_category_blurb(merged_df)
        
    def create_totals_barchart(self, month, year, target_income, target_spend, actual_income, actual_spend):
        tot_target_income, tot_target_spend = target_income["Amount"].sum(), target_spend["Amount"].sum()
        tot_actual_income, tot_actual_spend = actual_income["Amount"].sum(), actual_spend["Amount"].sum()
        totals_fig = go.Figure(data=[
            go.Bar(name="target", x=["Income", "Spend"], y=[tot_target_income, tot_target_spend]),
            go.Bar(name="actual", x=["Income", "Spend"], y=[tot_actual_income, tot_actual_spend])
        ])
        totals_fig.update_layout(barmode="group", title=f"Net Difference for {month.value[1]} {year}", xaxis_title="Category", yaxis_title="Amount")
        chart_html = pio.to_html(totals_fig, full_html=False, include_plotlyjs="cdn")
        return chart_html, self.generate_totals_blurb(tot_target_income, tot_target_spend, tot_actual_income, tot_actual_spend)
    
    
    # ------------ MAIN ------------
    
    # create report with data visualizations for target vs. actual spend
    def create_report(self, month, year=None):
        if not year:
            year = datetime.now().date().year
        
        target, target_income, target_spend = self.split_spend_income([f"goals/{month.value[1]}_{year}.csv", "goals/default_goals.csv"])
        actual_raw, actual_income, actual_spend_raw = self.split_spend_income([f"actual/{month.value[1]}_{year}.csv"])
        actual_spend = actual_spend_raw.groupby("Category")["Amount"].sum().reset_index()
        actual = actual_raw.groupby("Category")["Amount"].sum().reset_index()
        
        target_spend_piechart_html, target_spend_piechart_blurb = self.create_spend_piechart(target_spend, f"Target Spend for {month.value[1]} {year}")
        actual_spend_piechart_html, actual_spend_piechart_blurb = self.create_spend_piechart(actual_spend, f"Actual Spend for {month.value[1]} {year}")
        actual_spend_linechart_html, actual_spend_linechart_blurb = self.create_cumulative_linechart(actual_spend_raw, f"Cumulative Spend for {month.value[1]} {year}")
        per_category_html, per_category_blurb = self.create_per_category_barchart(month, year, target, actual)
        totals_html, totals_blurb = self.create_totals_barchart(month, year, target_income, target_spend, actual_income, actual_spend)
        
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
                <p>{actual_spend_linechart_blurb}</p>
            </div>
            <div class="chart-container">
                <h2>Target Spend Breakdown</h2>
                {target_spend_piechart_html}
                <p>{target_spend_piechart_blurb}</p>
            </div>
            <div class="chart-container">
                <h2>Actual Spend Breakdown</h2>
                {actual_spend_piechart_html}
                <p>{actual_spend_piechart_blurb}</p>
            </div>
            <div class="chart-container">
                <h2>Spend Comparison</h2>
                {per_category_html}
                <p>{per_category_blurb}</p>
            </div>
            <div class="chart-container">
                <h2>Net Difference</h2>
                {totals_html}
                <p>{totals_blurb}</p>
            </div>
        </body>
        </html>
        """
        
        with open(f"reports/{month.value[1]}_{year}.html", "w") as out_file:
            out_file.write(report)
        
        
if __name__ == "__main__":
    r = Reporter()
    
    r.create_report(Month.NOV, 2023)