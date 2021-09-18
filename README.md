# SimplePoll

Send a quick multiple-choice poll to a live remote audience.

## Run

1. Install the dependencies:

```
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip3 install -r requirements.txt
```

2. Start the server:

```
(venv) python3 poll.py
```

## Use

1.  Go to `http://localhost:8000`
2.  Create a poll by entering the title and options.
3.  Copy the poll URL (not the admin URL!) and send it to your audience (eg. via videoconference chat).
5.  Go to the poll results page.

## Persistence

Polls are stored in RAM. Unless the `BACKUP_FILE` environment variable is set, all polls will be
lost when the service is stopped. To enable backups:

```
$ BACKUP_FILE=polls.json python3 poll.py
```

Also, there is a limit on the amount of polls stored (currently set at 100), so old ones
will be eventually evicted.
