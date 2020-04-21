# SimplePoll

Send a quick multiple-choice poll to a live remote audience.

Usage:

```
$ python3 poll.py
```

1.  Go to `http://localhost:8000`
2.  Create a poll by entering the title and options.
3.  Copy the poll URL (not the admin URL!) and send it to your audience (eg. via videoconference chat).
5.  Go to the poll results page.

Note: Polls are stored in RAM, and will be lost when the service is
restarted. Also, there is a limit of the amount of polls stored, so old ones
will be eventually evicted.
