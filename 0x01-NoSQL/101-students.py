#!/usr/bin/env python3
'''
task studwents
'''


def top_students(mongo_collection):
    '''all students in a collection sorted by aveage'''
    students = mongo_collection.aggregate([{'$project': {'_id': 1, 'name': 1,
        'averageScore': {'$avg': '$topics.score'}}}, {'$sort': {'averageScore':
            -1}}])
    return students
