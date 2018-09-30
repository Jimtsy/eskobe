import response
import simplejson as json
import random
from push.push_center import Body, PushCenter
from const import APPPush

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
                return response.ParamsErrorResponse("lack of params")

            if push_type not in APPPush.PushType.__all__:
                return response.ParamsErrorResponse("invalid push_type, select from {}".format(APPPush.PushType.__all__))

            api = request_kwargs.pop("api", "pushTemplateMessage")
            amount = request_kwargs.get("amount", random.randint(1, 100))
            priority = request_kwargs.get("priority", 1)
            body = Body(app_id, app_key, temple_id, amount, target_id, platform, priority)
            push_center = PushCenter(platform=platform)

            push_center.start_push(push_type=push_type, api=api, body=body, **request_kwargs)
            return response.SuccessResponse("查看实时统计信息: http://106.14.30.88:3000/dashboard/db/shou-qian-ba-tui-song?"
                                            "panelId=1&fullscreen&edit&from=now-5m&to=now&tab=metrics")
        return response.NotFoundResponse("not supported")

    @staticmethod
    def kill_push(req):
        if req.method == "POST":
            request_kwargs = json.loads(str(req.body, encoding="utf-8"))
            platform = request_kwargs.pop("platform", None)
            if not platform:
                return response.ParamsErrorResponse("lack of params <platform>")
            push_center = PushCenter(platform=platform)
            msg = push_center.stop_all_thread()
            return response.SuccessResponse(msg)
        return response.NotFoundResponse("not supported")

    @staticmethod
    def get_current_stats(req):
        if req.method == "POST":
            request_kwargs = json.loads(str(req.body, encoding="utf-8"))
            platform = request_kwargs.pop("platform", None)
            if not platform:
                return response.ParamsErrorResponse("lack of params <platform>")
            push_center = PushCenter(platform=platform)
            stats = push_center.show_stats()
            if stats:
                return response.SuccessResponse(stats)
            else:
                return response.SuccessResponse("no data")
        return response.NotFoundResponse("not supported")