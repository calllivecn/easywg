import json

class Body2Json:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        wg_body = {}
        body = {}
        try:
           body = json.loads(request.body)
        except Exception:
            pass

        for k, v in body.items():
            if v is not None:
                wg_body[k] = v

        request.META["WG_BODY"] = wg_body

        response = self.get_response(request)

        return response
