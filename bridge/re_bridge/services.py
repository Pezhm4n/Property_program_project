import json
from .loader import call_dll_endpoint
from .exceptions import check_error
from .models import LoginRequest, LoginResponse, PropertyDTO

class AuthService:
    @staticmethod
    def login(req: LoginRequest) -> LoginResponse:
        req_json = json.dumps(req.to_dict())
        rc, res_json = call_dll_endpoint('re_login', req_json)
        check_error(rc)
        data = json.loads(res_json)
        return LoginResponse(token=data.get('token', ''))
        
    @staticmethod
    def logout(token: str) -> None:
        req_json = json.dumps({"token": token})
        rc, _ = call_dll_endpoint('re_logout', req_json)
        check_error(rc)

class PropertyService:
    @staticmethod
    def create_property(token: str, prop: PropertyDTO) -> dict:
        payload = {
            "token": token,
            "property": prop.to_dict()
        }
        req_json = json.dumps(payload)
        rc, res_json = call_dll_endpoint('re_create_property', req_json)
        check_error(rc)
        return json.loads(res_json)
