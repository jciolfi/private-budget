from enum import Enum
from attr import dataclass

class TransactionSource(Enum):
    C1 = (1, "Capital One")
    DISC = (2, "Discover")
    SOFI = (3, "SoFi")
    BOFA = (4, "Bank of America")

class Month(Enum):
    JAN = (1, "Jan", "January")
    FEB = (2, "Feb", "February")
    MAR = (3, "Mar", "March")
    APR = (4, "Apr", "April")
    MAY = (5, "May", "May")
    JUN = (6, "Jun", "June")
    JUL = (7, "Jul", "July")
    AUG = (8, "Aug", "August")
    SEP = (9, "Sep", "September")
    OCT = (10, "Oct", "October")
    NOV = (11, "Nov", "November")
    DEC = (12, "Dec", "December")
    
@dataclass
class Transaction:
    date: str
    desc: str
    category: str
    amt: float