import base64


def basic_auth_header(username, password):
    data = "{username}:{password}".format(username=username, password=password)
    result = base64.b64encode(data)
    return {"Authorization": "Basic %s" % result}
