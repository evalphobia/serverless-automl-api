import base64
import os
import json
import requests
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
from resize import resize

if 'GOOGLE_APPLICATION_JSON' in os.environ:
    from oauth2client.service_account import ServiceAccountCredentials
    key_dict = json.loads(os.environ['GOOGLE_APPLICATION_JSON'])
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(key_dict)
else:
    credentials = GoogleCredentials.get_application_default()

ml_service = discovery.build('ml', 'v1', credentials=credentials)


def predicts(params):
    """Run prediction by given image URL."""
    predict_params = []
    for i, param in enumerate(params):
        key = str(i)
        if 'key' in param:
            key = param['key']

        if 'b64' in param:
            data = param['b64']
        elif 'url' in param:
            data = _download_data(param['url'])
        elif 'file' in param:
            data = _get_file_data(param['file'])
        else:
            continue
        predict_params.append({'key': key, 'image_bytes': {'b64': data}})
    if len(predict_params) == 0:
        raise Exception('cannot parse parameters: {}'.format(params))

    results = call_prediction_api(predict_params)
    return parse_results(results)


def _get_file_data(path):
    with open(path, 'rb') as ff:
        data = ff.read()
    return base64.b64encode(resize(data)).decode('utf-8')


def _download_data(url, timeout=10):
    """Download data from given URL."""
    resp = requests.get(url, allow_redirects=False, timeout=timeout)
    if resp.status_code != 200:
        raise Exception('Error on http: [{}], HTTP status: [{}]'.format(url, resp.status_code))
    return base64.b64encode(resize(resp.content)).decode('utf-8')


def call_prediction_api(instances):
    name = 'projects/{}/models/{}'.format(_get_automl_project(), _get_automl_model())
    version = _get_automl_version()
    if version:
        name += '/versions/{}'.format(version)
    request_dict = {'instances': instances}
    request = ml_service.projects().predict(name=name, body=request_dict)
    return request.execute()  # waits till request is returned


def parse_results(results):
    results = results['predictions']
    data = {}
    # data['raw_output'] = results
    data['size'] = len(results)

    result_list = []
    for r in results:
        d = {}
        d['key'] = r['key']
        # get key-value pair for lable and score
        scores = {}
        for i, label in enumerate(r['labels']):
            scores[label] = r['scores'][i]
        d['result'] = scores
        # get max score
        max_score = max(r['scores'])
        max_idx = r['scores'].index(max_score)
        d['label'] = r['labels'][max_idx]
        d['score'] = max_score
        # add data
        result_list.append(d)

    data['results'] = result_list
    return data


def _get_automl_project():
    if 'GOOGLE_AUTOML_PROJECT' in os.environ:
        return os.environ['GOOGLE_AUTOML_PROJECT']
    return ''


def _get_automl_model():
    if 'GOOGLE_AUTOML_MODEL' in os.environ:
        return os.environ['GOOGLE_AUTOML_MODEL']
    return ''


def _get_automl_version():
    if 'GOOGLE_AUTOML_VERSION' in os.environ:
        return os.environ['GOOGLE_AUTOML_VERSION']
    return ''


def _get_automl_files():
    if 'GOOGLE_AUTOML_FILE' in os.environ:
        return os.environ['GOOGLE_AUTOML_FILE'].split(',')
    return []


def _get_automl_urls():
    if 'GOOGLE_AUTOML_URL' in os.environ:
        return os.environ['GOOGLE_AUTOML_URL'].split(',')
    return []


if __name__ == '__main__':
    params = []
    for v in _get_automl_urls():
        params.append({'url': v})
    for v in _get_automl_files():
        params.append({'file': v})

    if len(params) == 0:
        raise Exception('Set "GOOGLE_AUTOML_FILE" or "GOOGLE_AUTOML_URL" environment variables for image processing')
    res = predicts(params)
    print(res)
