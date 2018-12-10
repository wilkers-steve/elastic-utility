# elastic-utility
A docker container for interacting with an Elasticsearch cluster

## Flags
```
parser.add_argument(
    '--query','-q',
    metavar='query',
    type=str,
    required=True,
    default="pod",
    help='Query type: pod name or kubernetes labels')
parser.add_argument(
    '--uri','-u',
    metavar='uri',
    type=str,
    required=True,
    help='Elasticsearch URI (with credentials if basic auth enabled)')
parser.add_argument(
    '--index','-i',
    metavar='index',
    type=str,
    required=False,
    default='_all',
    help='Elasticsearch index to search')
parser.add_argument(
    '--pod','-p',
    metavar='pod',
    type=str,
    required=False,
    help='Name of the pod to retrieve logs for')
parser.add_argument(
    '--labels','-l',
    nargs='+',
    metavar='labels',
    required=False,
    help='List of key:values for labels to query')
parser.add_argument(
    '--namespace','-n',
    metavar='namespace',
    type=str,
    required=False,
    help='The namespace of the pod(s) to retrieve logs for')
```

## Usage
### Python
```
./elastic-query.py --uri http://user:password@elasticsearch-logging.osh-infra:80 --labels kubernetes.labels.application:elasticsearch kubernetes.labels.component:test
```
### Docker
```
docker run docker.io/srwilkers/elastic-query:v0.1.0 --uri http://user:password@elasticsearch-logging.osh-infra:80 --labels kubernetes.labels.application:elasticsearch kubernetes.labels.component:test
```
