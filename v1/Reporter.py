import re, json
import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
from datetime import datetime
from classes import Month
from calendar import monthrange
from os.path import exists

class Reporter:
    def __init__(self):
        self.category_mappings = {}
        self.category_colors = {}
        
        settings = "settings.json"
        if exists(settings):
            with open(settings, "r") as file:
                mappings = json.load(file)
                self.category_mappings = mappings["Mappings"]
                self.category_colors = mappings["Colors"]
    
    # ------------ HELPERS ------------
    # import data and split into income and expenses
    def split_spend_income(self, filepaths):
        for filepath in filepaths:
            if not exists(filepath):
                continue
            
            filetype = filepath[filepath.rfind(".") + 1:]
            if filetype == "csv":    
                df = pd.read_csv(filepath)
            elif filetype == "json":
                with open(filepath, "r") as file:
                    data = json.load(file)["Budget"]
                df = pd.DataFrame({"Category": data.keys(), "Amount": data.values()})
            else:
                continue
            
            df["Category"] = df["Category"].replace(self.category_mappings)
            df_income = df[df["Category"].str.contains("income|salary|invest", case=False, regex=True)]
            df_spend = df[~df["Category"].str.contains("income|salary|invest", case=False, regex=True)]
            return df, df_income, df_spend
            
        print(f"Could not find any existing files: {', '.join(filepaths)}")
        exit(1)
    
    def round_money(self, money):
        return round(money, 2)
    
    
    # ------------ BLURBS ------------
    def generate_cumulative_blurb(self, total_spend, days_in_month):
        return f"You spent ${self.round_money(total_spend)} this month, for an average daily spend of ${self.round_money(total_spend / days_in_month)}."
    
    def generate_spend_blurb(self, data, num_top=3):
        top_categories = data.sort_values(by='Amount', ascending=False).head(num_top)
        res = []
        for _, row in top_categories.iterrows():
            res.append(f'{row["Category"]} (${self.round_money(row["Amount"])})')
        
        return f"Your top spend categories were: {', '.join(res[:-1])}, and {res[-1]}."
    
    def generate_per_category_blurb(self, merged_df):
        over, under = [], []
        income_pattern = r"(income|salary|invest)"
        for _, row in merged_df.iterrows():
            diff = self.round_money(row["Amount_target"] - row["Amount_actual"])
            category = row["Category"]
            if re.search(income_pattern, category, re.IGNORECASE):
                diff *= -1
            
            category_item = (abs(diff), category)
            if diff >= 0:
                over.append(category_item)
            else:
                under.append(category_item)
        
        over_items = list(map(lambda x: f"{x[1]} (${x[0]})", sorted(over, reverse=True)))
        under_items = list(map(lambda x: f"{x[1]} (-${x[0]})", sorted(under, reverse=True)))
        
        over_str = under_str = ""
        if len(over) > 0:
            over_str = f"You were on target in the following categories: {', '.join(over_items[:-1])}, and {over_items[-1]}."

        if len(under) > 0:
            under_str = f"You were off target in the following categories: {', '.join(under_items[:-1])}, and {under_items[-1]}."
            
        return over_str, under_str
    
    def generate_totals_blurb(self, tot_target_income, tot_target_spend, tot_actual_income, tot_actual_spend):
        spend_diff = tot_target_spend - tot_actual_spend
        under_over_spend = "underspent" if spend_diff >= 0 else "overspent"
        
        income_diff = tot_actual_income - tot_target_income
        under_over_income = "more" if income_diff >= 0 else "less"
        
        net_diff = tot_actual_income - tot_actual_spend
        gain_loss = "gain" if net_diff >= 0 else "loss"
        
        return f"You had a net {gain_loss} of ${abs(self.round_money(net_diff))}.\
            You {under_over_spend} by ${abs(self.round_money(spend_diff))},\
            and you made ${abs(self.round_money(income_diff))} {under_over_income} than expected."
    
    # ------------ FIGURES ------------
    # create a piechart with the given data and title
    def create_spend_piechart(self, data, title):
        fig = px.pie(data, values="Amount", names="Category", title=title, color="Category", color_discrete_map=self.category_colors)
        return pio.to_html(fig, full_html=False, include_plotlyjs="cdn"), self.generate_spend_blurb(data)
    
    
    # create linechart of cumulative spend per day for this month
    def create_cumulative_linechart(self, spend_data, title):
        data = spend_data.copy()
        data["Date"] = pd.to_datetime(data["Date"], format="%d %m %Y")
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
        
        fig.add_trace(go.Scatter(x=[data["Date"].iloc[0].replace(day=1), data["Date"].iloc[0].replace(day=days_in_month)], 
                             y=[0, total_spend],
                             mode="lines",
                             line={"dash": "dash", "color": "#37c2ca"},
                             name="Average Spend"))
        fig.add_trace(go.Scatter(x=data["Date"], y=data["Cumulative Spend"], mode="lines", name="Actual Spend", line={"color": "#db534c"}))
        
        return pio.to_html(fig, full_html=False, include_plotlyjs="cdn"), self.generate_cumulative_blurb(total_spend, days_in_month)
    
    
    def create_per_category_barchart(self, month, year, target, actual):
        merged_df = target.merge(actual, on="Category", how="outer", suffixes=("_target", "_actual"))
        merged_df.fillna(0, inplace=True)
        
        categories_fig = go.Figure(data=[
            go.Bar(name="target", x=merged_df["Category"], y=merged_df["Amount_target"], marker={"color": "#37c2ca"}),
            go.Bar(name="actual", x=merged_df["Category"], y=merged_df["Amount_actual"], marker={"color": "#db534c"})
        ])
        categories_fig.update_layout(barmode="group", title=f"Target vs. Actual Spend for {month.value[1]} {year}", xaxis_title="Category", yaxis_title="Amount")
        chart_html = pio.to_html(categories_fig, full_html=False, include_plotlyjs="cdn")
        return chart_html, self.generate_per_category_blurb(merged_df)
    
    
    def create_totals_barchart(self, month, year, target_income, target_spend, actual_income, actual_spend):
        tot_target_income, tot_target_spend = target_income["Amount"].sum(), target_spend["Amount"].sum()
        tot_actual_income, tot_actual_spend = actual_income["Amount"].sum(), actual_spend["Amount"].sum()
        totals_fig = go.Figure(data=[
            go.Bar(name="target", x=["Income", "Spend"], y=[tot_target_income, tot_target_spend], marker={"color": "#37c2ca"}),
            go.Bar(name="actual", x=["Income", "Spend"], y=[tot_actual_income, tot_actual_spend], marker={"color": "#db534c"})
        ])
        totals_fig.update_layout(barmode="group", title=f"Net Difference for {month.value[1]} {year}", xaxis_title="Category", yaxis_title="Amount")
        chart_html = pio.to_html(totals_fig, full_html=False, include_plotlyjs="cdn")
        return chart_html, self.generate_totals_blurb(tot_target_income, tot_target_spend, tot_actual_income, tot_actual_spend)
    
    
    def generate_sankeymatic_chart(self, actual_income, actual_spend):
        chart_contents = []
        colors = [":Income #4c956c", ":Spending #7a71f8"]
        
        total_income = self.round_money(actual_income["Amount"].sum())
        total_spend = self.round_money(actual_spend["Amount"].sum())
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
            category, amount = row["Category"], self.round_money(row["Amount"])
            chart_contents.append(f"Spending [{amount}] {category}")
            
            if category in self.category_colors:
                colors.append(f":{category} {self.category_colors[category]}")
        
        return "<br>\n".join(chart_contents + colors)
        
    
    # ------------ MAIN ------------
    def run(self, month, year=None):
        if not year:
            year = datetime.now().date().year
        self.create_report(month, year)
    
    # create report with data visualizations for target vs. actual spend
    def create_report(self, month, year):
        target, target_income, target_spend = self.split_spend_income([f"goals/{month.value[0]}_{year}.csv", "settings.json"])
        actual_raw, actual_income, actual_spend_raw = self.split_spend_income([f"actual/{month.value[0]}_{year}.csv"])
        actual_spend = actual_spend_raw.groupby("Category")["Amount"].sum().reset_index()
        actual = actual_raw.groupby("Category")["Amount"].sum().reset_index()
        
        target_spend_piechart_html, target_spend_piechart_blurb = self.create_spend_piechart(target_spend, f"Target Spend for {month.value[1]} {year}")
        actual_spend_piechart_html, actual_spend_piechart_blurb = self.create_spend_piechart(actual_spend, f"Actual Spend for {month.value[1]} {year}")
        actual_spend_linechart_html, actual_spend_linechart_blurb = self.create_cumulative_linechart(actual_spend_raw, f"Cumulative Spend for {month.value[1]} {year}")
        per_category_html, (over_cateory_blurb, under_category_blurb) = self.create_per_category_barchart(month, year, target, actual)
        totals_html, totals_blurb = self.create_totals_barchart(month, year, target_income, target_spend, actual_income, actual_spend)
        sankeymatic_chart = self.generate_sankeymatic_chart(actual_income, actual_spend)
        
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
                .center-iframe {{
                    display: flex;
                    justify-content: center; /* Horizontally center */
                    align-items: center; /* Vertically center */
                    height: 100vh; /* Set the height to fill the entire viewport */
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
                <p>{over_cateory_blurb}</p>
                <p>{under_category_blurb}</p>
            </div>
            <div class="chart-container">
                <h2>Net Difference</h2>
                {totals_html}
                <p>{totals_blurb}</p>
            </div>
            <div class="chart-container">
                <h2>Sankeymatic (Flow) Chart</h2>
                <p>Paste the following below in <a href="https://sankeymatic.com/build/">SankeyMATIC</a> to view your expenses as a flow chart!</p>
                <p>{sankeymatic_chart}</p>
                <div class="center-iframe">
                    <iframe src="https://sankeymatic.com/build/" width="100%" height="100%">
                        <p>Your browser does not support iframes.</p>
                    </iframe>
                </div>    
            </div>
            
        </body>
        </html>
        """
        
        with open(f"reports/{month.value[0]}_{year}.html", "w") as out_file:
            out_file.write(report)
        
        
if __name__ == "__main__":
    r = Reporter()
    
    # r.create_report(Month.MAY, 2023)
    # r.create_report(Month.JUN, 2023)
    # r.create_report(Month.JUL, 2023)
    # r.create_report(Month.AUG, 2023)
    # r.create_report(Month.SEP, 2023)
    r.create_report(Month.NOV, 2023)
    # r.create_report(Month.DEC, 2023)