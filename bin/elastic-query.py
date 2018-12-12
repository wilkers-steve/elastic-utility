#!/usr/bin/env python

import argparse
from datetime import datetime
import getopt
import os
import re
import sys

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

def main():
    """Query a specific elasticsearch index or all indexes for logs, filtering
    by either by pod name and namespace or by kubernetes label values for the
    pod's application, component and namespace."""

    desc = ('Query elasticsearch indexes for logs, using a pods name and'
            ' namespace, or by label key:value pairs for the pod(s).'
            ' ex. \"elastic-query.py'
            ' --query pod'
            ' --uri http://admin:changeme@elasticsearch-logging.osh-infra:80'
            ' --pod elasticsearch-test'
            ' --namespace osh-infra\"'
            ' OR'
            ' \"elastic-query.py'
            ' --query labels'
            ' --uri http://admin:changeme@elasticsearch-logging.osh-infra:80'
            ' --labels kubernetes.labels.application:elasticsearch'
            ' kubernetes.labels.component:test')
    parser = argparse.ArgumentParser(description=desc)
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
    parser.add_argument(
        '--file','-f',
        metavar='file',
        type=str,
        required=False,
        help='Output results to file instead of console')

    args, unknown = parser.parse_known_args()

    es = Elasticsearch([args.uri])

    if args.query == "pod":
        search = pod_query(es, args.pod, args.namespace, args.index)
    elif args.query == "labels":
        search = label_query(es, args.labels, args.index)
    else:
        print("I'm sorry Dave, I'm afraid I can't do that")
        exit(1)
    print("Scan yielded %s results." % (search.count()))
    print("------")
    for hit in search.scan():
        if args.file:
            with open(os.path.abspath(args.file), 'a+') as f:
                if 'log' in hit:
                    f.write("{} | {}\n".format(hit["@timestamp"], hit["log"]))
                elif 'message' in hit:
                    f.write("{} | {}\n".format(hit["@timestamp"], hit["message"]))
                else:
                    f.write("{} | {} | {}\n".format(hit["@timestamp"], hit["HOSTNAME"], hit["MESSAGE"]))
        else:
            if 'log' in hit:
                print("{} | {}\n".format(hit["@timestamp"], hit["log"]))
            elif 'message' in hit:
                print("{} | {}\n".format(hit["@timestamp"], hit["message"]))
            else:
                print("{} | {} | {}\n".format(hit["@timestamp"], hit["HOSTNAME"], hit["MESSAGE"]))


def pod_query(es, pod, namespace, index):
    search = Search(using=es, index=index) \
        .filter({"term": {"kubernetes.pod_name.keyword": pod}}) \
        .filter({"term": {"kubernetes.namespace_name.keyword": namespace}})
    return search


def label_query(es, labels, index):
    search = Search(using=es, index=index)
    for label in labels:
        label_parts = re.split(':', label)
        label_key = label_parts[0]
        label_value = label_parts[1]
        search = search.filter({"term": {label_key: label_value}})
    return search


if __name__ == "__main__":
    sys.exit(main())
