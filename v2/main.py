import sys
import pandas as pd

def main(filename):
    print(filename)
    
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./run <statement.csv>")
    main(sys.argv[1])