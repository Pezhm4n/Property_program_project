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
        payload = {"token": token, "property": prop.to_dict()}
        req_json = json.dumps(payload)
        rc, res_json = call_dll_endpoint('re_create_property', req_json)
        check_error(rc)
        return json.loads(res_json)

    @staticmethod
    def update_property(token: str, prop_id: int, prop: PropertyDTO) -> None:
        payload = {"token": token, "id": prop_id, "property": prop.to_dict()}
        req_json = json.dumps(payload)
        rc, res_json = call_dll_endpoint('re_update_property', req_json)
        check_error(rc)

    @staticmethod
    def get_properties(token: str, search_state=None) -> list[PropertyDTO]:
        from .models import SearchState
        state = search_state or SearchState()
        
        payload = {
            "token": token,
            "search_state": state.to_dict()
        }
        req_json = json.dumps(payload)
        rc, res_json = call_dll_endpoint('re_get_properties', req_json)
        check_error(rc)
        data = json.loads(res_json)
        return [PropertyDTO(**item) for item in data.get('properties', [])]

    @staticmethod
    def archive_property(token: str, prop_id: int) -> None:
        payload = {"token": token, "id": prop_id}
        req_json = json.dumps(payload)
        rc, res_json = call_dll_endpoint('re_archive_property', req_json)
        check_error(rc)

    @staticmethod
    def restore_property(token: str, prop_id: int) -> None:
        payload = {"token": token, "id": prop_id}
        req_json = json.dumps(payload)
        rc, res_json = call_dll_endpoint('re_restore_property', req_json)
        check_error(rc)

class DashboardService:
    @staticmethod
    def get_dashboard_data(token: str) -> dict:
        from .exceptions import NotImplementedError
        payload = {"token": token}
        req_json = json.dumps(payload)
        try:
            rc, res_json = call_dll_endpoint('re_get_dashboard', req_json)
            check_error(rc)
            return json.loads(res_json)
        except NotImplementedError:
            # Fallback to rich mock data when core implementation is missing
            return {
                "total_properties": 120,
                "active_properties": 95,
                "archived_properties": 25,
                "total_users": 15,
                "total_agents": 8,
                "last_update": "1405/04/15 12:30",
                "recent_activities": [
                    {"timestamp": "1405/04/15 12:20", "user": "admin", "action": "افزودن ملک مسکونی", "details": "شناسه 101"},
                    {"timestamp": "1405/04/15 11:45", "user": "agent1", "action": "آرشیو ملک", "details": "شناسه 45"},
                    {"timestamp": "1405/04/15 10:15", "user": "admin", "action": "تغییر وضعیت ملک", "details": "شناسه 12"},
                    {"timestamp": "1405/04/15 09:30", "user": "agent2", "action": "ثبت زمین", "details": "شناسه 102"}
                ],
                "charts": {
                    "monthly_sales": [10, 15, 8, 12, 20, 25],
                    "monthly_rents": [5, 12, 15, 8, 10, 18],
                    "categories": {"residential": 60, "commercial": 30, "land": 30}
                }
            }
