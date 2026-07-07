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
    id: int
    is_archived: bool
    category: str
    listing_type: str
    city: str
    municipal_district: int
    address: str
    owner_phone: str
    area_sqm: int
    sale_price: int
    rent_deposit: int
    rent_monthly: int
    date_registered: str
    
    def to_dict(self):
        return asdict(self)

@dataclass
class PaginationDTO:
    page_number: int = 1
    page_size: int = 20

@dataclass
class SortingDTO:
    column: str = "date_registered"
    ascending: bool = False

@dataclass
class SearchState:
    query: str = ""
    filters: dict = None
    sorting: SortingDTO = None
    pagination: PaginationDTO = None
    
    def __post_init__(self):
        if self.filters is None:
            self.filters = {"is_archived": False}
        if self.sorting is None:
            self.sorting = SortingDTO()
        if self.pagination is None:
            self.pagination = PaginationDTO()
            
    def to_dict(self):
        return {
            "query": self.query,
            "filters": self.filters,
            "sorting": asdict(self.sorting),
            "pagination": asdict(self.pagination)
        }

    @classmethod
    def from_dict(cls, data: dict):
        if not data:
            return cls()
        sorting_data = data.get("sorting", {})
        pagination_data = data.get("pagination", {})
        return cls(
            query=data.get("query", ""),
            filters=data.get("filters", {}),
            sorting=SortingDTO(
                column=sorting_data.get("column", "date_registered"),
                ascending=sorting_data.get("ascending", False)
            ),
            pagination=PaginationDTO(
                page_number=pagination_data.get("page_number", 1),
                page_size=pagination_data.get("page_size", 20)
            )
        )
