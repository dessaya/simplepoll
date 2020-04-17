from bottle import route, run, request, response, redirect, HTTPResponse
import os
from datetime import datetime
import random
import string
from collections import OrderedDict

PORT = int(os.environ.get('PORT', '8000'))

alnum = string.ascii_lowercase + string.digits
def make_key():
    return ''.join(random.choices(alnum, k=6))

def link(path):
    return f'{request.url[:-len(request.path)].rstrip("/")}{path}'.rstrip('/')

class Poll:
    def __init__(self, title, options):
        self.key = make_key()
        self.title = title
        self.options = options
        self.started_at = datetime.now()
        self.responses = {}

    def percentage(self, i):
        total = sum(v for k, v in self.responses.items())
        if not total:
            return 0
        p = int((self.responses.get(i, 0) / total) * 100 + 0.5)
        return f'<div style="width:300px; height: 1em; border: 1px solid #007bff"><div style="width:{p}%; height:100%; background-color: #007bff"></div></div>'

polls = OrderedDict()

def evict_old_polls():
    while len(polls) > 100:
        key, _ = polls.popitem(last=False)
        print(f'Evicted poll {key}')

def get_poll(key):
    return polls.get(key, None) or error(404, 'Not Found')

def html(s):
    return f'''<!doctype html><html><head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Simple poll</title>
        <link rel="stylesheet" href="https://unpkg.com/marx-css/css/marx.min.css">
        </head><body><main role="main">{s}</main></body></html>'''

def error(status, msg):
    raise HTTPResponse(html(f'<h1>Oops</h1><p>{msg}</p>'), status)

@route('/', method="GET")
def index():
    return html(f'''
        <h1>Configure your poll</h1>
        <form action="{link('/')}" method="post">
            <div>
            <input name="title" id="title" type="text" placeholder="Title" />
            </div>
            <div>
            <textarea id="options" name="options" rows="10" cols="50" placeholder="Options (one per line)"></textarea>
            </div>
            <input type="submit" value="Create poll">
        </form>
    ''')

@route('/', method="POST")
def create_poll():
    title = request.forms.title.strip()
    options = [s.strip() for s in request.forms.options.split('\n') if s.strip()]

    if len(options) < 2:
        error(400, 'We need at least 2 options.')

    poll = Poll(title, options)
    polls[poll.key] = poll
    evict_old_polls()
    redirect(link(f'/{poll.key}'))

@route('/<key>', method="GET")
def index(key):
    poll = get_poll(key)
    links = []
    stats = []
    for (i, option) in enumerate(poll.options):
        url = link(f'/{key}/{i}')
        links.append(f'<li>{option}: <a href="{url}">{url}</a></li>')
        stats.append(f'<tr><th>{option}</th><td>{poll.responses.get(i, 0)}</td><td>{poll.percentage(i)}</td></tr>')

    return html(f'''
        <h1>{poll.title}</h1>
        <ul>{''.join(links)}</ul>
        <table>
            <thead><tr><th>Option</th><th>Votes</th><th>%</th></tr></thead>
            {''.join(stats)}
        </table>
    ''')

@route('/<key>/<i:int>', method="GET")
def vote(key, i):
    poll = get_poll(key)
    if i >= len(poll.options):
        error(404, 'Not Found')
    poll.responses[i] = poll.responses.get(i, 0) + 1
    return html(f'<center class="hero"><h1>Thank you for voting!</h1><p>You voted: <b>{poll.options[i]}</b></p></center>')

run(host='localhost', port=PORT)
