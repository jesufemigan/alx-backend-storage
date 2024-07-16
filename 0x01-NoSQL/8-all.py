#!/usr/bin/env python3
'''
lists all documents in a collection
'''
import pymongo


def list_all(mongo_collection):
    '''
    a function that lists all documents in a collection
    '''
    return [doc for doc in mongo_collection.find()]
