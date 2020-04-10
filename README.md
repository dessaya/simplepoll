# Simple poll

Example:

```
$ python3 poll.py 'http://localhost:8000' 'Cats or dogs?' 'Cats FTW' 'Dogs FTW'
Cats or dogs?
Cats FTW: http://localhost:8000/0
Dogs FTW: http://localhost:8000/1

http://localhost:8000/responses
```

*   Send all links but the last one to your audience.
*   Wait untill everyone has voted.
*   See the poll results at the last link.

Note: the `base-url` parameter is only used to generate the links. The HTTP
server listens on `0.0.0.0:8000` regardless.
