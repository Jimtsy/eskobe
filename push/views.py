import response
import simplejson as json
import random
from const import APPPush
from push.push_center import push_center

__all__ = ["PushHandler"]


class PushHandler:
    @staticmethod
    def push_message(req):
        if req.method == "POST":
            request_kwargs = json.loads(str(req.body, encoding="utf-8"))
            app_id = request_kwargs.pop("app_id", None)
            app_key = request_kwargs.pop("app_key", None)
            temple_id = request_kwargs.pop("temple_id", None)
            platform = request_kwargs.pop("platform", None)
            target_id = request_kwargs.pop("target_id", None)
            push_type = request_kwargs.pop("push_type", None)
            if not all([app_id, app_key, temple_id, platform, target_id]):
                return response.ParamsErr("lack of params")

            if push_type not in APPPush.PushType.__all__:
                return response.ParamsErr("invalid push_type, select from {}".format(APPPush.PushType.__all__))

            amount = request_kwargs.get("amount", random.randint(1, 100))
            priority = request_kwargs.get("priority", 1)
            body = push_center.new_push_body(platform=platform, app_id=app_id, app_key=app_key, temple_id=temple_id,
                                             amount=amount, target_id=target_id, priority=priority)
            msg = push_center.push(platform, body)
            return response.Success(msg)
        return response.NotFound("not supported")

    @staticmethod
    def kill_push(req):
        if req.method == "POST":
            request_kwargs = json.loads(str(req.body, encoding="utf-8"))
            platform = request_kwargs.pop("platform", None)
            target_id = request_kwargs.pop("target_id", None)
            if not all([platform, target_id]):
                return response.ParamsErr("lack of params")
            msg = push_center.kill_push(platform, target_id)
            return response.Success(msg)
        return response.NotFound("not supported")

    @staticmethod
    def get_current_stats(req):
        if req.method == "POST":
            request_kwargs = json.loads(str(req.body, encoding="utf-8"))
            platform = request_kwargs.pop("platform", None)
            target_id = request_kwargs.pop("target_id", None)
            if not all([platform, target_id]):
                return response.ParamsErr("lack of params")

            msg = push_center.show_stats(platform, target_id)
            return response.Success(msg)
        return response.NotFound("not supported")

    @staticmethod
    def show_hooks(req):
        if req.method == "POST":
            request_kwargs = json.loads(str(req.body, encoding="utf-8"))
            platform = request_kwargs.pop("platform", None)
            if not platform:
                return response.ParamsErr("lack of params")
            msg = push_center.show_hooks(platform)
            return response.Success(msg)
        return response.NotFound("not supported")