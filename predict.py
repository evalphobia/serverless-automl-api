import os
import json
import requests
import struct
from google.cloud import automl_v1beta1
from google.oauth2 import service_account
from oauth2client.client import GoogleCredentials
from resize import resize

if 'GOOGLE_APPLICATION_JSON' in os.environ:
    key_dict = json.loads(os.environ['GOOGLE_APPLICATION_JSON'])
    credentials = service_account.Credentials.from_service_account_info(key_dict)
else:
    credentials = GoogleCredentials.get_application_default()

ml_client = automl_v1beta1.PredictionServiceClient(credentials=credentials)


def predicts(params):
    """Run prediction by given image URL."""
    results = []
    predict_targets = []
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
        predict_targets.append({'key': key, 'payload': {'image': {'image_bytes': data}}})
    if len(predict_targets) == 0:
        raise Exception('cannot parse parameters: {}'.format(params))

    for i, target in enumerate(predict_targets):
        result = call_prediction_api(target['payload'])
        results.append({'key': target['key'], 'response': result.payload})

    return parse_results(results)


def _get_file_data(path):
    with open(path, 'rb') as ff:
        data = ff.read()
    return resize(data)


def _download_data(url, timeout=30):
    """Download data from given URL."""
    resp = requests.get(url, allow_redirects=False, timeout=timeout)
    if resp.status_code != 200:
        raise Exception('Error on http: [{}], HTTP status: [{}]'.format(url, resp.status_code))
    print('[_download_data] url:[%s] size:[%d]' % (url, len(resp.content)))
    return resize(resp.content)


def call_prediction_api(payload):
    name = 'projects/{}/locations/{}/models/{}'.format(_get_automl_project(), _get_automl_location(), _get_automl_model())
    th = '%08x' % struct.unpack('<L', struct.pack('>f', 0.0))[0]
    params = {'score_threshold': th}
    return ml_client.predict(name, payload, params)


def parse_results(results):
    data = {}
    data['size'] = len(results)

    result_list = []
    for r in results:
        d = {}
        d['key'] = r['key']
        # get key-value pair for lable and score
        scores = {}
        for i, c in enumerate(r['response']):
            scores[c.display_name] = c.classification.score
        d['result'] = scores
        # get max score
        max_score_label = max(scores, key=scores.get)
        d['label'] = max_score_label
        d['score'] = scores[max_score_label]
        # add data
        result_list.append(d)

    data['results'] = result_list
    print('[parse_results]: %s' % json.dumps(data))
    return data


def _get_automl_project():
    if 'GOOGLE_AUTOML_PROJECT' in os.environ:
        return os.environ['GOOGLE_AUTOML_PROJECT']
    return ''


def _get_automl_model():
    if 'GOOGLE_AUTOML_MODEL' in os.environ:
        return os.environ['GOOGLE_AUTOML_MODEL']
    return ''


def _get_automl_location():
    if 'GOOGLE_AUTOML_LOCATION' in os.environ:
        return os.environ['GOOGLE_AUTOML_LOCATION']
    return 'us-central1'


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
