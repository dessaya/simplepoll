from bottle import route, run, request, response, redirect, HTTPResponse, template
from collections import OrderedDict
import random
import string
import os

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
        self.responses = {}

    def percentage(self, i):
        total = sum(v for k, v in self.responses.items())
        if not total:
            return 0
        return int((self.responses.get(i, 0) / total) * 100 + 0.5)

polls = OrderedDict()

def evict_old_polls():
    while len(polls) > 100:
        key, _ = polls.popitem(last=False)
        print(f'Evicted poll {key}')

def get_poll(key):
    return polls.get(key, None) or error(404, 'Not Found')

fork = '''<a href="https://github.com/dessaya/simplepoll" class="github-corner" aria-label="View source on GitHub"><svg width="80" height="80" viewBox="0 0 250 250" style="fill:#151513; color:#fff; position: absolute; top: 0; border: 0; right: 0;" aria-hidden="true"><path d="M0,0 L115,115 L130,115 L142,142 L250,250 L250,0 Z"></path><path d="M128.3,109.0 C113.8,99.7 119.0,89.6 119.0,89.6 C122.0,82.7 120.5,78.6 120.5,78.6 C119.2,72.0 123.4,76.3 123.4,76.3 C127.3,80.9 125.5,87.3 125.5,87.3 C122.9,97.6 130.6,101.9 134.4,103.2" fill="currentColor" style="transform-origin: 130px 106px;" class="octo-arm"></path><path d="M115.0,115.0 C114.9,115.1 118.7,116.5 119.8,115.4 L133.7,101.6 C136.9,99.2 139.9,98.4 142.2,98.6 C133.8,88.0 127.5,74.4 143.8,58.0 C148.5,53.4 154.0,51.2 159.7,51.0 C160.3,49.4 163.2,43.6 171.4,40.1 C171.4,40.1 176.1,42.5 178.8,56.2 C183.1,58.6 187.2,61.8 190.9,65.4 C194.5,69.0 197.7,73.2 200.1,77.6 C213.8,80.2 216.3,84.9 216.3,84.9 C212.7,93.1 206.9,96.0 205.4,96.6 C205.1,102.4 203.0,107.8 198.3,112.5 C181.9,128.9 168.3,122.5 157.7,114.1 C157.9,116.9 156.7,120.9 152.7,124.9 L141.0,136.5 C139.8,137.7 141.6,141.9 141.8,141.8 Z" fill="currentColor" class="octo-body"></path></svg></a><style>.github-corner:hover .octo-arm{animation:octocat-wave 560ms ease-in-out}@keyframes octocat-wave{0%,100%{transform:rotate(0)}20%,60%{transform:rotate(-25deg)}40%,80%{transform:rotate(10deg)}}@media (max-width:500px){.github-corner:hover .octo-arm{animation:none}.github-corner .octo-arm{animation:octocat-wave 560ms ease-in-out}}</style>'''

def html(s):
    return '<!doctype html><html><head>' \
        '<meta charset="utf-8">' \
        '<meta name="viewport" content="width=device-width, initial-scale=1">' \
        '<title>Simple poll</title>' \
        '<link rel="stylesheet" href="https://unpkg.com/marx-css/css/marx.min.css">' \
        f'</head><body><main role="main"><h1><a href="{link("/")}">SimplePoll</a></h1>{s}</main>{fork}</body></html>'

def error(status, msg):
    raise HTTPResponse(html(f'<h2>Oops</h2><p>{msg}</p>'), status)

@route('/', method="GET")
def index():
    return html(f'''
        <form action="{link('/')}" method="post">
            <h2>Step 1: Configure your poll</h2>
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

    for _ in range(5):
        poll = Poll(title, options)
        if poll.key not in polls:
            break
    else:
        error(500, 'Failed to find an unused key')

    polls[poll.key] = poll
    evict_old_polls()

    redirect(link(f'/{poll.key}'))

@route('/<key>', method="GET")
def admin(key):
    poll = get_poll(key)
    return html(template(
        '''
            <h2>Step 2: Share the voting links to your audience</h2>
            <pre id="share">{{poll.title}}
% for (i, option) in enumerate(poll.options):
* {{option}}: {{!link(f'/{poll.key}/{i}')}}
% end
</pre>
            <button id="sharebtn" onclick="share()">Copy to clipboard</button>
            <script>
            function share() {
                navigator.clipboard.writeText(document.querySelector("#share").innerText).then(() => {
                    document.querySelector("#sharebtn").innerHTML = "Copied!";
                });
            }
            </script>
            <hr/>
            <h2>Step 3: View the results</h2>
            <a href="{{!link(f'/{poll.key}/results')}}"><button>View poll results</button></a>
        ''',
        poll=poll,
        link=link,
    ))

@route('/<key>/results', method="GET")
def results(key):
    poll = get_poll(key)
    return html(template(
        '''
            <h2>{{poll.title}}</h2>
            <table style="width: 100%">
                % for (i, option) in enumerate(poll.options):
                    % p = poll.percentage(i)
                    <tr>
                        <th style="width: 50%">{{option}}</th>
                        <td><nobr>{{!poll.responses.get(i, 0)}} votes</nobr></td>
                        <td><nobr>{{p}}%</nobr></td>
                        <td style="min-width: 30%"><div style="width:100%; height: 1em; border: 1px solid #007bff"><div style="width:{{!p}}%; height:100%; background-color: #007bff"></div></div></td>
                    </tr>
                % end
            </table>
            <a href="{{!link(f'/{poll.key}')}}">Back to admin page</a>
        ''',
        poll=poll,
        link=link,
    ))

@route('/<key>/<i:int>', method="GET")
def vote(key, i):
    poll = get_poll(key)
    if i >= len(poll.options):
        error(404, 'Not Found')
    poll.responses[i] = poll.responses.get(i, 0) + 1
    return html(template(
        '<h2>Thank you for voting!</h2><p>You voted: <b>{{option}}</b></p>',
        option=poll.options[i],
    ))

run(host='localhost', port=PORT)
