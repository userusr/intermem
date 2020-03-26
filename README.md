# Dummy memcached client library

[![Build Status](https://travis-ci.org/userusr/intermem.svg?branch=master)](https://travis-ci.org/userusr/intermem)

This is dummy implementation of memcached protocol. Not fully upported only `set`, `get`
and `delete` commands.

Memcached protocol is
[here](https://github.com/memcached/memcached/blob/master/doc/protocol.txt).

## Testing

For testing on real server you should set `MEMCACHED_HOST` environment variable:

```bash
docker pull memcached:latest
docker run --rm --tty -d memcached:latest
MEMCACHED_HOST=172.17.0.2 pytest
```
