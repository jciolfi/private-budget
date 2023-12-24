import datetime
import pandas as pd
from classes import Month
import plotly.express as px
import plotly.io as pio


class TransactionExporter:
    def __init__(self):
        pass
    
    def spending_breakdown(self, month, year):        
        # open file
        file_path = f"transactions/{month.value[1]}_{year}.csv"
        data = pd.read_csv(file_path)

        # create pie chart of spend by category
        category_spend = data.groupby("Category")["Amount"].sum().reset_index()
        fig = px.pie(category_spend, values="Amount", names="Category", title=f"Spend for {month} {year}")
        chart_html = pio.to_html(fig, full_html=False, include_plotlyjs='cdn')
        
        return category_spend, chart_html
    
    def create_report(self, month, year=None):
        if not year:
            year = datetime.datetime.now().date().year
            
        category_spend, category_chart = self.spending_breakdown(month, year)
        
        # create report
        report = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{month} {year} Report</title>
        </head>
        <body>
            <h1>Spend By Category</h1>
            {category_chart}
        </body>
        </html>
        """
        with open(f"reports/{month.value[1]_{year}}.html", "w") as out_file:
            out_file.write(report)
        
        
        
        
        
        # matplotlib
        # category_sums = data.groupby("Category")["Amount"].sum()
        # plt.figure(figsize=(10, 6))
        # plt.pie(category_sums, labels=category_sums.index, autopct="%1.1f%%", startangle=140)
        # plt.title(f"Amount Spent Per Category in {month.value[2]} 2023")
        # plt.show()
        
        
if __name__ == "__main__":
    t = TransactionExporter()
    t.spending_breakdown(Month.OCT)
    # t.spending_breakdown(Month.NOV)
    # t.spending_breakdown(Month.DEC)