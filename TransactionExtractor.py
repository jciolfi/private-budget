import datetime, csv
from os.path import exists
from classes import Transaction, TransactionSource
from bs4 import BeautifulSoup
from collections import defaultdict 

class TransactionExtractor:
    def __init__(self):
        pass
    
    def extract(self, source, filepath, year=None):            
        if not year:
            year = datetime.datetime.now().date().year
            
        transactions = []
        match source:
            case TransactionSource.C1:
                transactions = self.import_c1(filepath, year)
            case TransactionSource.DISC:
                transactions = self.import_disc(filepath)
            case TransactionSource.SOFI:
                transactions = self.import_sofi(filepath)
            case TransactionSource.BOFA:
                transactions = self.import_bofa(filepath)
            case _:
                print(f"Could not find transaction source for {source}")
                return
        
        if not transactions:
            print(f"Warning: could not find any transactions in {filepath}")
            return 
        
        self.export_transactions(transactions)            
            
    def find_item_c1(self, html, tag, classname):
        try:
            if tag == "c1-ease-cell":
                amt_html = html.find(tag, {"class": classname})
                for span in amt_html:
                    return span.text.strip().replace("$", "").replace(",", "")
                
            return html.find(tag, {"class": classname}).text.strip()
        except:
            return None 
    
    def import_c1(self, filepath, year):
        transactions = defaultdict(list)
        with open(filepath, "r") as in_file:
            soup = BeautifulSoup(in_file.read(), "html.parser")
            tables = soup.find_all("div", {"class": "c1-ease-table__body"})
            for table in tables:
                for row in table:
                    if not row or not row.text.split():
                        continue
                    
                    amt = self.find_item_c1(row, "c1-ease-cell", "c1-ease-card-transactions-view-table__amount")
                    if not amt or float(amt) < 0:
                        continue
                    
                    month = self.find_item_c1(row, "span", "c1-ease-txns-date-and-status__month")
                    day = self.find_item_c1(row, "span", "c1-ease-txns-date-and-status__day")
                    desc = self.find_item_c1(row, "div", "c1-ease-txns-description__description")
                    category = self.find_item_c1(row, "span", "c1-ease-card-transactions-view-table__rewards-category")
                    if category and month and day and desc and amt:
                        transactions[f"{month}_{year}"].append(Transaction(f"{day} {month}", desc, category, float(amt)))
        
        return transactions
        
    def import_disc(self, filepath):
        with open(filepath, "r") as in_file:
            pass
    
    def import_sofi(self, filepath):
        with open(filepath, "r") as in_file:
            pass
    
    def import_bofa(self, filepath):
        with open(filepath, "r") as in_file:
            pass
    
    
    def export_transactions(self, transactions):
        for month_year in transactions:
            out_filename = f"transactions/{month_year}.csv"
            add_header = False
            if not exists(out_filename):
                add_header = True
            with open(out_filename, "a") as out_file:
                writer = csv.writer(out_file)
                if add_header:
                    writer.writerow(["Date", "Description", "Category", "Amount"])
                for t in sorted(transactions[month_year], key=lambda t: t.date):
                    writer.writerow([t.date, t.desc, t.category, t.amt])
            
        
        
if __name__ == "__main__":
    t = TransactionExtractor()
    # t.extract(TransactionSource.C1, "statements/nov_23_s1.html", Month.NOV, 2023)
    t.extract(TransactionSource.C1, "statements/bulk_2023.html")