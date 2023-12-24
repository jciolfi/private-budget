import datetime
import pandas as pd
from classes import Month
import plotly.express as px


class TransactionExporter:
    def __init__(self):
        pass
    
    def spending_breakdown(self, month, year=None):
        if not year:
            year = datetime.datetime.now().date().year
        
        file_path = f"transactions/{month.value[1]}_{year}.csv"
        data = pd.read_csv(file_path)

        category_sums = data.groupby("Category")["Amount"].sum().reset_index()

        # Create an interactive pie chart
        fig = px.pie(category_sums, values="Amount", names="Category", title=f"Spend for {month} {year}")
        fig.show()
        
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