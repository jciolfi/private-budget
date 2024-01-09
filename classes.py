from enum import Enum
from attr import dataclass

class TransactionSource(Enum):
    C1 = (1, "C1", "Capital One")
    DISC = (2, "Disc", "Discover")
    SOFI = (3, "SoFi", "SoFi")
    BOFA = (4, "BOFA", "Bank of America")
    
    @classmethod
    def from_value(cls, value):
        value = value.lower()
        for member in cls:
            if member.value[0] == str(value) or member.value[1].lower() == value or member.value[2].lower() == value:
                return member
        raise ValueError(f"{value} is not a valid Month")


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
    
    @classmethod
    def from_value(cls, value):
        value = value.lower()
        for member in cls:
            if str(member.value[0]) == value or member.value[1].lower() == value or member.value[2].lower() == value:
                return member
        raise ValueError(f"{value} is not a valid Month")

    
@dataclass
class Transaction:
    date: str
    desc: str
    category: str
    amt: float