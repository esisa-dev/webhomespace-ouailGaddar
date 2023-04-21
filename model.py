from dataclasses import dataclass
import datetime
@dataclass
class User:
    name:str
    passwd:str
@dataclass
class Directory:
    name:str
    date:datetime
    size:float
    path:str
    def __str__(self):
        return f"{self.name}  - {self.size} ( {self.path} )"
    def __repr__(self):
        return f"{self.name} - {self.date} - {self.size} - {self.path}"
@dataclass
class File :
    name:str
    date:datetime
    size:float
    path:str
    def __str__(self):
       return f"{self.name}  - {self.size} ( {self.path} )"