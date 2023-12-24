from enum import Enum

from attr import dataclass

class TransactionSource(Enum):
    C1 = (1, "Capital One")
    DISC = (2, "Discover")
    SOFI = (3, "SoFi")
    BOFA = (4, "Bank of America")

class Month(Enum):
    JAN = (1, "January")
    FEB = (2, "February")
    MAR = (3, "March")
    APR = (4, "April")
    MAY = (5, "May")
    JUN = (6, "June")
    JUL = (7, "July")
    AUG = (8, "August")
    SEP = (9, "September")
    OCT = (10, "October")
    NOV = (11, "November")
    DEC = (12, "December")
    
@dataclass
class Transaction:
    date: str
    desc: str
    category: str
    amt: float