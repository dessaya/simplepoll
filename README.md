# Simple poll

Example:

```
$ python3 poll.py 'http://localhost:8000'

Question: Cats or dogs?
Option (leave blank when done): Cats FTW
Option (leave blank when done): Dogs FTW
Option (leave blank when done): 

Listening on 0.0.0.0:8000
Poll results at http://localhost:8000/responses
Send the following to your audience:

Cats or dogs?
Cats FTW: http://localhost:8000/0
Dogs FTW: http://localhost:8000/1
```

Note: the `base-url` parameter is only used to generate the links. The HTTP
server listens on `0.0.0.0:8000` regardless.
