import datetime
import pandas as pd
from classes import Month
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go


class Reporter:
    def __init__(self):
        pass
    
    # create a piechart with the given data and title
    def create_spend_piechart(self, data, title):
        fig = px.pie(data, values="Amount", names="Category", title=title)
        return pio.to_html(fig, full_html=False, include_plotlyjs="cdn")
    
    
    # target spend piechart per category
    def target_spending_breakdown(self, month, year):
        file_path = f"goals/{month.value[1]}_{year}.csv"
        data = pd.read_csv(file_path)
        chart_html = self.create_spend_piechart(data[2:], f"Target Spend for {month.value[2]} {year}")
        
        return data, chart_html
        
        
    # actual spend piechart per category
    def actual_spending_breakdown(self, month, year):
        file_path = f"transactions/{month.value[1]}_{year}.csv"
        data = pd.read_csv(file_path)
        category_spend = data.groupby("Category")["Amount"].sum().reset_index()
        chart_html = self.create_spend_piechart(category_spend, f"Actual Spend for {month.value[2]} {year}")
        
        return category_spend, chart_html
    
    
    # create bar charts to compare target vs. actual spend: per category and aggregated
    def spend_comparison_barchart(self, target, actual):
        # bar chart comparing spend per category
        merged_df = target.merge(actual, on="Category", how="outer", suffixes=('_target', '_actual'))
        categories_fig = go.Figure(data=[
            go.Bar(name='target', x=merged_df['Category'], y=merged_df['Amount_target']),
            go.Bar(name='actual', x=merged_df['Category'], y=merged_df['Amount_actual'])
        ])
        categories_fig.update_layout(barmode='group', title='Comparison of Amounts by Category', xaxis_title='Category', yaxis_title='Amount')
        categories_html = pio.to_html(categories_fig, full_html=False, include_plotlyjs="cdn")
        
        # bar chart comparing total target vs. actual income/spend
        target_income = target[target['Category'].str.contains('income|salary', case=False, regex=True)]['Amount'].sum()
        target_spend = target[~target['Category'].str.contains('income|salary', case=False, regex=True)]['Amount'].sum()
        actual_income = actual[actual['Category'].str.contains('income|salary', case=False, regex=True)]['Amount'].sum()
        actual_spend = actual[~actual['Category'].str.contains('income|salary', case=False, regex=True)]['Amount'].sum()
        totals_fig = go.Figure(data=[
            go.Bar(name="target", x=["Income", "Spend"], y=[target_income, target_spend]),
            go.Bar(name="actual", x=["Income", "Spend"], y=[actual_income, actual_spend])
        ])
        totals_html = pio.to_html(totals_fig, full_html=False, include_plotlyjs="cdn")
        
        return categories_html, totals_html
    
    
    # create report with data visualizations for target vs. actual spend
    def create_report(self, month, year=None):
        if not year:
            year = datetime.datetime.now().date().year
            
        target, target_piechart = self.target_spending_breakdown(month, year)
        actual, actual_piechart = self.actual_spending_breakdown(month, year)
        categories_html, totals_html = self.spend_comparison_barchart(target, actual)
        
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
        
        # matplotlib
        # category_sums = data.groupby("Category")["Amount"].sum()
        # plt.figure(figsize=(10, 6))
        # plt.pie(category_sums, labels=category_sums.index, autopct="%1.1f%%", startangle=140)
        # plt.title(f"Amount Spent Per Category in {month.value[2]} 2023")
        # plt.show()
        
        
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