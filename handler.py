import json
import predict


def handler(event, context):
    """Handle lambda execution."""
    data = event
    if 'body' in event:
        data = json.loads(event['body'])

    params = _to_list(data)
    resp = predict.predicts(params)
    return response_success(resp)


def _to_list(val):
    """Return the variable converted to list type."""
    if isinstance(val, list):
        return val
    else:
        return [val]


def response_success(data):
    """Return success response."""
    body = {
        "error": None,
        "code": 200,
    }
    data.update(body)
    return {
        "statusCode": 200,
        "body": json.dumps(data)
    }


def response_error400(err):
    """Return error response."""
    data = {
        "error": err,
        "code": 400,
    }
    return {
        "statusCode": 400,
        "body": json.dumps(data)
    }
