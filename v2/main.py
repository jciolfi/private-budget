import sys
import pandas as pd

category_colors = {
    "Dining": "#f3433a",
    "Merchandise": "#db534c",
    "Other Travel": "#c4635e",
    "Entertainment": "#ac7370",
    "Gas/Automotive": "#4eb2b8",
    "Grocery": "#1fd2dc",
    "Other": "#7d9394"
}

def round_money(money):
    return round(money, 2)


def generate_sankeymatic_chart(actual_income, actual_spend):
        chart_contents = []
        colors = [":Income #4c956c", ":Spending #7a71f8"]
        
        # total_income = round_money(actual_income["Amount"].sum())
        total_income = 0
        total_spend = actual_spend["Debit"].sum()
        print(type(total_spend), total_spend)
        savings = total_income - total_spend
        
        # append savings or overdraft
        if savings > 0:
            chart_contents.append(f"Income [{total_spend}] Spending")
            chart_contents.append(f"Income [{savings}] Savings")
            colors.append(":Savings #2c6e49")
        else:
            chart_contents.append(f"Bank [{-savings}] Spending")
            chart_contents.append(f"Income [{total_income}] Spending")
            colors.append(":Bank #79021c")
        
        # append spend by category
        for _, row in actual_spend.iterrows():
            category, amount = row["Category"], round_money(row["Debit"])
            chart_contents.append(f"Spending [{amount}] {category}")
            
            if category in category_colors:
                colors.append(f":{category} {category_colors[category]}")
        
        return "<br>\n".join(chart_contents + colors)


def main(filename):
    with open(filename, "r") as fp:
        # TODO: exclude only payments, include refunds?
        df = pd.read_csv(fp)
        df.dropna(subset=["Debit"], inplace=True)
        
        df['Debit'] = pd.to_numeric(df['Debit'])
        df["Transaction Date"] = pd.to_datetime(df["Transaction Date"])
        df.set_index("Transaction Date")
        
        category_spend = df.groupby("Category")["Debit"].sum().reset_index()
        print(type(category_spend), category_spend)
        print(generate_sankeymatic_chart(0, category_spend))
            
        
    
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./run <statement.csv>")
    main(sys.argv[1])