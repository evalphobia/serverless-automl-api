serverless-automl-api
----

[![License: MIT][3]][4] [![Release][5]][6] [![Build Status][7]][8]  [![Code Climate][19]][20] [![BCH compliance][21]][22]

[3]: https://img.shields.io/badge/License-MIT-blue.svg
[4]: LICENSE.md
[5]: https://img.shields.io/github/release/evalphobia/serverless-automl-api.svg
[6]: https://github.com/evalphobia/serverless-automl-api/releases/latest
[7]: https://travis-ci.org/evalphobia/serverless-automl-api.svg?branch=master
[8]: https://travis-ci.org/evalphobia/serverless-automl-api
[9]: https://coveralls.io/repos/evalphobia/serverless-automl-api/badge.svg?branch=master&service=github
[10]: https://coveralls.io/github/evalphobia/serverless-automl-api?branch=master
[11]: https://codecov.io/github/evalphobia/serverless-automl-api/coverage.svg?branch=master
[12]: https://codecov.io/github/evalphobia/serverless-automl-api?branch=master
[15]: https://img.shields.io/github/downloads/evalphobia/serverless-automl-api/total.svg?maxAge=1800
[16]: https://github.com/evalphobia/serverless-automl-api/releases
[17]: https://img.shields.io/github/stars/evalphobia/serverless-automl-api.svg
[18]: https://github.com/evalphobia/serverless-automl-api/stargazers
[19]: https://codeclimate.com/github/evalphobia/serverless-automl-api/badges/gpa.svg
[20]: https://codeclimate.com/github/evalphobia/serverless-automl-api
[21]: https://bettercodehub.com/edge/badge/evalphobia/serverless-automl-api?branch=master
[22]: https://bettercodehub.com/

`serverless-automl-api` is REST API for Google AutoML, powered by AWS Lambda.

# Download

Download serverless-automl-api by command below.

```bash
$ git clone https://github.com/evalphobia/serverless-automl-api
$ cd serverless-automl-api
$ npm install
```

# Config

## serverless.yml

Change environment variables below,

```bash
$ cp serverless.yml.example serverless.yml
$ vim serverless.yml

------------

functions:
  automl_api:
    handler: handler.handler
    memorySize: 128
    timeout: 60
    environment:
      ######### Change here! ########
      GOOGLE_AUTOML_PROJECT: <your GCP project id>
      GOOGLE_AUTOML_MODEL: <AutoML model name>
      GOOGLE_APPLICATION_JSON: '{"type": "service_account", "private_key_id": "<...>", "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n", "client_email": "example@example.iam.gserviceaccount.com", "client_id": "..."}'
    events:
      - http:
          path: predict
          method: post

```

## Environment variables

|Name|Description|
|:--|:--|
| `GOOGLE_AUTOML_PROJECT` | GCP Project ID |
| `GOOGLE_AUTOML_MODEL` | AutoML model name |
| `GOOGLE_APPLICATION_JSON` | JSON string of GCP service account's pem file |


# Deploy

```bash
# To use `sls` command, install first.
# $ npm install -g serverless

$ AWS_ACCESS_KEY_ID=<...> AWS_SECRET_ACCESS_KEY=<...> sls deploy -v
```

# Predict

```bash
# prepare parameters
$ cat params.json

[
  {"key": "file-0", "url": "https://example.com/foo.jpg"},
  {"key": "file-1", "url": "https://example.com/bar.jpg"},
  {"key": "file-2", "b64": "YXNrb2Frc29ha3Nhb2tzb2Frbw=="}
]


# Send request to AWS Lambda with parameters.
$ curl 'https://example.execute-api.ap-northeast-1.amazonaws.com/dev/predict' -XPOST -d @params.json | jq .

{
  "size": 3,
  "results": [
    {
      "key": "file-0",
      "result": {
        "cat": 0.995314359664910,
        "dog": 0.000015523432011,
        "--other--": 0.0000062229569266492035
      },
      "label": "cat",
      "score": 0.995314359664910
    },
    {
      "key": "file-1",
      "result": {
        "cat": 0.000015523432011,
        "dog": 0.995314359664919,
        "--other--": 0.0000062229569266492035
      },
      "label": "dog",
      "score": 0.995314359664919
    },
    {
      "key": "file-2",
      "result": {
        "cat": 0.995314359664917,
        "dog": 0.000015523432011832483,
        "--other--": 0.0000062229569266492035
      },
      "label": "cat",
      "score": 0.995314359664917
    },
  ],
  "error": null,
  "code": 200
}
```

# Check Log

```bash
$ AWS_ACCESS_KEY_ID=<...> AWS_SECRET_ACCESS_KEY=<...> sls logs -f automl_api -t
```
