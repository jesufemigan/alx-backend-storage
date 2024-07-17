#!/usr/bin/env python3
'''
writing string to Redis
'''
import redis
import uuid
from typing import Union, Callable, Any
from functools import wraps


def call_history(method: Callable) -> Callable:
    '''
    store the history of inputs and outputs for a particular function
    '''
    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        '''
        calls a function
        '''
        in_key = '{}:inputs'.format(method.__qualname__)
        out_key = '{}:outputs'.format(method.__qualname__)
        self._redis.rpush(in_key, str(args))
        output = method(self, *args, **kwargs)
        self._redis.rpush(out_key, output)
        return output

    return invoker


def count_calls(method: Callable) -> Callable:
    '''
    tracks number of calls made to a method of Cache class
    '''
    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        '''
        invokes a method after incr
        '''
        if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)
    return invoker


def replay(method: Callable) -> None:
    '''
    history of previous callls
    '''
    fn_name = method.__qualname__
    db = method.__self__.redis
    inputs = db.lrange(fn_name + ':inputs', 0, -1)
    outputs = db.lrange(fn_name + ':outputs', 0 ,-1)

    print('{} was called {} times:'.format(fn_name, len(inputs)))
    for in_put, out_put in zip(inputs, outputs):
        in_put = in_put.decode('utf-8')
        out_put = out_put.decode('utf-8')
        print('{} (*{}) -> {}'.format(fn_name, in_put, out_put))


class Cache:
    '''
    a cache class
    '''
    def __init__(self) -> None:
        '''constructor for Cache class'''
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, float, int, bytes]) -> str:
        '''generate a random key and stores
        the input data in Redis
        '''
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Callable = None) -> Union[str, bytes, float,
                                                          int]:
        '''
        convert data type to desired format
        '''
        output = self._redis.get(key)
        return fn(output) if fn is not None else output

    def get_str(self, key: str) -> str:
        '''
        gets string from the redis db
        '''
        return self.get(key, lambda x: x.decode('utf-8'))

    def get_int(self, key: str) -> int:
        '''
        gets int from redis db
        '''
        return self.get(key, lambda x: int(x))
