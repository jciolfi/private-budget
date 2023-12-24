from classes import Month, Transaction, TransactionSource
from bs4 import BeautifulSoup

class TransactionExtractor:
    def __init__(self):
        pass
    
    def extract(self, source, filepath, month, year):
        # list of Transaction dataclass
        transactions = []
        match source:
            case TransactionSource.C1:
                transactions = self.import_c1(filepath)
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
        
        self.export_transactions(transactions, f"{month.value[0]}_{year}.csv")            
            
    def find_item(self, html, tag, classname):
        if tag == "c1-ease-cell":
            amt_html = html.find(tag, {"class": classname})
            for span in amt_html:
                return span.text.strip()
            
        return html.find(tag, {"class": classname}).text.strip()
    
    def import_c1(self, filepath):
        with open(filepath, "r") as in_file:
            soup = BeautifulSoup(in_file.read(), "html.parser")
            table = soup.find("div", {"class": "c1-ease-table__body"})
            for row in table:
                if not row or not row.text.split():
                    break
                month = self.find_item(row, "span", "c1-ease-txns-date-and-status__month")
                day = self.find_item(row, "span", "c1-ease-txns-date-and-status__day")
                desc = self.find_item(row, "div", "c1-ease-txns-description__description")
                category = self.find_item(row, "span", "c1-ease-card-transactions-view-table__rewards-category")
                amt = self.find_item(row, "c1-ease-cell", "c1-ease-card-transactions-view-table__amount")
                print(month, day, desc, category, amt, "\n")
                # break
        
    def import_disc(self, filepath):
        with open(filepath, "r") as in_file:
            pass
    
    def import_sofi(self, filepath):
        with open(filepath, "r") as in_file:
            pass
    
    def import_bofa(self, filepath):
        with open(filepath, "r") as in_file:
            pass
    
    
    def export_transactions(self, filepath):
        with open(filepath, "w") as out_file:
            pass
        
        
if __name__ == "__main__":
    t = TransactionExtractor()
    t.extract(TransactionSource.C1, "statements/nov_23_s1.html", Month.NOV, 2023)