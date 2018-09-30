import response
import simplejson as json
import random
from push.lib.push_center import new_push_center
from push.lib.body import new_push_body
from const import APPPush

__all__ = ["PushHandler"]


def check_valid_push_center(platform):
    push_center = new_push_center(platform=platform)
    if not push_center:
        return None
    return push_center


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

            api = request_kwargs.pop("api", "pushTemplateMessage")
            amount = request_kwargs.get("amount", random.randint(1, 100))
            priority = request_kwargs.get("priority", 1)
            pc = check_valid_push_center(platform=platform)
            if not pc:
                return response.ParamsErr("cannot find push center, maybe you should select from {}".format(
                    APPPush.PushCenter.__all__))

            body = new_push_body(platform=platform, app_id=app_id, app_key=app_key, temple_id=temple_id,
                                 amount=amount, target_id=target_id, priority=priority)
            pc.start_push(push_type=push_type, api=api, body=body, **request_kwargs)
            return response.Success("查看实时统计信息: http://106.14.30.88:3000/dashboard/db/shou-qian-ba-tui-song?"
                                            "panelId=1&fullscreen&edit&from=now-5m&to=now&tab=metrics")
        return response.NotFound("not supported")

    @staticmethod
    def kill_push(req):
        if req.method == "POST":
            request_kwargs = json.loads(str(req.body, encoding="utf-8"))
            platform = request_kwargs.pop("platform", None)
            if not platform:
                return response.ParamsErr("lack of params <platform>")
            pc = check_valid_push_center(platform=platform)
            if not pc:
                return response.ParamsErr("cannot find push center, maybe you should select from {}".format(
                    APPPush.PushCenter.__all__))

            msg = pc.stop_all_thread()
            return response.Success(msg)
        return response.NotFound("not supported")

    @staticmethod
    def get_current_stats(req):
        if req.method == "POST":
            request_kwargs = json.loads(str(req.body, encoding="utf-8"))
            platform = request_kwargs.pop("platform", None)
            if not platform:
                return response.ParamsErr("lack of params <platform>")
            pc = check_valid_push_center(platform)
            if not pc:
                return response.ParamsErr("cannot find push center, maybe you should select from {}".format(
                    APPPush.PushCenter.__all__))

            stats = pc.show_stats()
            if stats:
                return response.Success(stats)
            else:
                return response.Success("no data")
        return response.NotFound("not supported")