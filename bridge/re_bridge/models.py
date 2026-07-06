from dataclasses import dataclass, asdict

@dataclass
class LoginRequest:
    username: str
    password: str
    
    def to_dict(self):
        return asdict(self)

@dataclass
class LoginResponse:
    token: str

@dataclass
class PropertyDTO:
    category: str
    listing_type: str
    municipal_district: int
    address: str
    owner_phone: str
    sale_price: int
    rent_deposit: int
    rent_monthly: int
    
    def to_dict(self):
        return asdict(self)
