import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)


def push(s):
    r.rpush('rssh_output', s)


def pop():
    return r.lpop('rssh_output')


def clear():
    r.delete('rssh_output')
