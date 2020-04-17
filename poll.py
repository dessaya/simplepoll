from bottle import route, run, request, response, redirect, abort
import os
from datetime import datetime

BASE_URL = os.environ.get('POLL_BASE_URL', None)

class Poll:
    def __init__(self, question, options):
        self.question = question
        self.options = options
        self.started_at = datetime.now()
        self.responses = {}

    def percentage(self, i):
        total = sum(v for k, v in self.responses.items())
        if not total:
            return 0
        p = int((self.responses.get(i, 0) / total) * 100 + 0.5)
        return f'<div style="width:40vw; height: 1em; border: 1px solid #007bff"><div style="width:{p}%; height:100%; background-color: #007bff"></div></div>'

current = None

def html(s):
    return f'''<!doctype html><html><head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Simple poll</title>
        <link rel="stylesheet" href="https://unpkg.com/marx-css/css/marx.min.css">
        </head><body><main role="main">{s}</main></body></html>'''

@route('/', method="GET")
def index():
    return html('''
        <h1>Configure your poll</h1>
        <form action="/" method="post">
            <div>
            <input name="question" id="question" type="text" placeholder="Question" />
            </div>
            <div>
            <textarea id="options" name="options" rows="10" cols="50" placeholder="Options (one per line)"></textarea>
            </div>
            <input type="submit" value="Create poll">
        </form>
    ''')

@route('/', method="POST")
def create_poll():
    question = request.forms.get('question', '').strip()
    options = [s.strip() for s in request.forms.get('options', '').split('\n') if s.strip()]

    if len(options) < 2:
        abort(400, html("We need at least 2 options."))
        return

    global current
    current = Poll(question, options)
    redirect("/results")

@route('/results', method="GET")
def index():
    links = []
    stats = []
    for (i, option) in enumerate(current.options):
        url = f'{request.url[:-len(request.path)]}/{i}'
        links.append(f'<li>{option}: <a href="{url}">{url}</a></li>')
        stats.append(f'<tr><th>{option}</th><td>{current.responses.get(i, 0)}</td><td>{current.percentage(i)}</td></tr>')

    return html(f'''
        <h1>{current.question}</h1>
        <ul>{''.join(links)}</ul>
        <table>
            <thead><tr><th>Option</th><th>Votes</th><th>%</th></tr></thead>
            {''.join(stats)}
        </table>
    ''')

@route('/<i:int>', method="GET")
def vote(i):
    current.responses[i] = current.responses.get(i, 0) + 1
    return html(f'<center class="hero"><h1>Thank you for voting!</h1><p>You voted: <b>{current.options[i]}</b></p></center>')

run(host='localhost', port=8000)
