# Simple poll

Send a quick multiple-choice poll to your audience.

Usage:

```
$ python3 poll.py
```

*   Go to `http://localhost:8000`
*   Create a poll by entering the title and options.
*   Your poll will look like:

    ----

    # Cats or dogs?

    * Cats: http://localhost:8000/1bxtpp/0
    * Dogs: http://localhost:8000/1bxtpp/1

        Option  Votes  %
        Cats    0      0
        Dogs    0      0

    ----

*   Send the links to your audience.
*   Each time someone performs a GET on one of the given URLs a vote is cast.
*   Refresh the page to view the results.

Note: Polls are stored in RAM, and will be lost when the service is
restarted. Also, there is a limit of the amount of polls stored, so old ones
will be eventually evicted.
