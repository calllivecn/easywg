import json

class Body2Json:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        try:
            request.META["WG_BODY"] = json.loads(request.body)
        except Exception:
            pass
        
        response = self.get_response(request)

        return response
