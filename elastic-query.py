#!/usr/bin/python

import argparse
from datetime import datetime
import getopt
import sys

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search


def main():
    """Query a specific elasticsearch index or all indexes for logs, filtering
    by either by pod name and namespace or by kubernetes label values for the
    pod's application, component and namespace."""

    desc = ('Query elasticsearch indexes for logs, using a pods name and'
            ' namespace, or by label values for the pods application, '
            ' component, and namespace.'
            ' ex. \"elastic-query.py'
            ' --query pod'
            ' --uri http://admin:changeme@elasticsearch-logging.osh-infra:80'
            ' --pod elasticsearch-test'
            ' --namespace osh-infra\"'
            ' OR'
            ' \"elastic-query.py'
            ' --query labels'
            ' --uri http://admin:changeme@elasticsearch-logging.osh-infra:80'
            ' --app elasticsearch'
            ' --component test'
            ' --namespace osh-infra\"')
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument(
        '--query',
        metavar='query',
        type=str,
        required=True,
        default="pod",
        help='Query type: pod name or kubernetes labels')
    parser.add_argument(
        '--uri',
        metavar='uri',
        type=str,
        required=True,
        help='Elasticsearch URI (with credentials if basic auth enabled)')
    parser.add_argument(
        '--index',
        metavar='index',
        type=str,
        required=False,
        default='_all',
        help='Elasticsearch index to search')
    parser.add_argument(
        '--pod',
        metavar='pod',
        type=str,
        required=False,
        help='Name of the pod to retrieve logs for')
    parser.add_argument(
        '--app',
        metavar='app',
        type=str,
        required=False,
        help='The Kubernetes label "application" on the pod(s)')
    parser.add_argument(
        '--component',
        metavar='component',
        type=str,
        required=False,
        help='The kubernetes label "component" on the pod(s)')
    parser.add_argument(
        '--namespace',
        metavar='namespace',
        type=str,
        required=False,
        help='The namespace of the pod(s) to retrieve logs for')

    args, unknown = parser.parse_known_args()

    es = Elasticsearch([args.uri])

    if args.query == "pod":
        search = pod_query(es, args.pod, args.namespace, args.index)
    elif args.query == "labels":
        search = label_query(es, args.app, args.component,
                             args.namespace, args.index)
    else:
        print("I'm sorry Dave, I'm afraid I can't do that")
        exit(1)
    print("Scan yielded %s results." % (search.count()))
    print("------")
    for hit in search.scan():
        print("%s | %s | %s" % (hit.time, hit.kubernetes.pod_name, hit.log))


def pod_query(es, pod, namespace, index):
    search = Search(using=es, index=index) \
        .filter({"term": {"kubernetes.pod_name.keyword": pod}}) \
        .filter({"term": {"kubernetes.namespace_name.keyword": namespace}}) \
        .sort('@timestamp', {"order": "asc"})
    return search


def label_query(es, application, component, namespace, index):
    search = Search(using=es, index=index) \
        .filter({"term": {"kubernetes.labels.component": component}}) \
        .filter({"term": {"kubernetes.labels.application": application}}) \
        .filter({"term": {"kubernetes.namespace_name.keyword": namespace}}) \
        .sort('@timestamp', {"order": "asc"})
    return search


if __name__ == "__main__":
    sys.exit(main())
