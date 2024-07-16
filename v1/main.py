import argparse
from Reporter import Reporter
from Importer import Importer
from classes import TransactionSource

def get_args():
    parser = argparse.ArgumentParser(description="Budgeting Tool")
    parser.add_argument('-b', '--bank', required=True, help='Source bank for transactions')
    parser.add_argument('-f', '--filepath', required=True, help='Filepath for transactions')
    parser.add_argument('-i', '--capital-gains', type=float, help='Capital gains amount')
    parser.add_argument('-s', '--salary', type=float, help='Salary amount')
    parser.add_argument('-o', '--other-income', type=float, help='Other income amount')
    parser.add_argument('-y', '--year', type=int, help='Year for transaction')
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    i = Importer()
    r = Reporter()
    
    try:
        source = TransactionSource.from_value(args.bank)
    except:
        print(f"Unknown source: '{args.bank}'")
        exit(1)
    
    times = i.run(source, args.filepath, args.year, args.salary, args.capital_gains, args.other_income)
    for month, year in times:
        r.run(month, year)
        print(f"Writing report for {month.value[2]}, {year}...")
        
    if len(times) > 0:
        print("Done!")
    
    
    
    
    
    
    
    
    
    
    