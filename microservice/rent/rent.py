import json
from io import BytesIO

from nameko.rpc import rpc, RpcProxy

class RentService:
    name = "rent_service"

    item_service = RpcProxy("item_service")
    profile_service = RpcProxy("profile_service")

    @rpc
    def rent_item(self, profile_id, item_id):
        result = {}
        if self.profile_service.check_point(profile_id) <= 0:
            result["error"] = True
            result["message"] = "User point is not enough."
            return result
        if self.item_service.check_item(item_id) is False:
            result["error"] = True
            result["message"] = "This item is not enough."
            return result
        
        item = self.item_service.rent_item(item_id)
        self.profile_service.rent_item(profile_id, item_id, item["name"])
        result["error"] = False
        result["message"] = "OK"
        return result
    
    @rpc
    def return_item(self, profile_id, lend_id):
        result = {}
        item_id = self.profile_service.return_item(profile_id, lend_id)
        if item_id is False:
            result["error"] = True
            result["message"] = "This item is already returned."
            return result
        
        self.item_service.return_item(item_id)
        result["error"] = False
        result["message"] = "OK"
        return result

    