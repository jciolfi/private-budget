from classes import Month, Transaction, TransactionSource

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
            
    
    def import_c1(self, filepath):
        with open(filepath) as in_file:
            pass
        
    def import_disc(self, filepath):
        with open(filepath) as in_file:
            pass
    
    def import_sofi(self, filepath):
        with open(filepath) as in_file:
            pass
    
    def import_bofa(self, filepath):
        with open(filepath) as in_file:
            pass
    
    
    def export_transactions(self, filepath):
        with open(filepath) as out_file:
            pass