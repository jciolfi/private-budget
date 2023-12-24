import Reporter, Importer
import argparse

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
    
    i.extract(args.bank, args.filepath, args.year)
    
    
    
    
    
    
    
    
    
    