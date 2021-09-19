from bottle import route, run, request, response, redirect, HTTPResponse, template
from collections import OrderedDict
import random
import string
import os
import json
import markdown

md = markdown.Markdown(output_format="html5", extensions=['fenced_code', 'nl2br'])

PORT = int(os.environ.get('PORT', '8000'))
BACKUP_FILE = os.environ.get('BACKUP_FILE', '')

_ALNUM = string.ascii_lowercase + string.digits
def make_key():
    return ''.join(random.choices(_ALNUM, k=6))

def full_link(path):
    return f'{request.urlparts.scheme}://{request.urlparts.netloc}{path}'.rstrip('/')

def basepath():
    netloc = request.urlparts.netloc
    return netloc[netloc.index('/'):].rstrip('/') if '/' in netloc else ''

def link(path):
    return f'{basepath()}{path}'

class Poll:
    def __init__(self, question, options, multiple_choice):
        self.key = make_key()
        self.question = question
        self.options = options
        self.multiple_choice = multiple_choice
        self.responses = [0 for i in range(len(options))]
        self.responses_count = 0

    def cast_vote(self, votes):
        if not self.multiple_choice and len(votes) != 1:
            error(400, 'Expected exactly one vote')
        for i in votes:
            if i >= len(self.options):
                error(400, 'Invalid option index')
            self.responses[i] += 1
        self.responses_count += 1

    def percentage(self, i):
        if not self.responses_count:
            return 0
        return int((self.responses[i] / self.responses_count) * 100 + 0.5)

    def admin_url(self):
        return link(f'/{self.key}/admin')

    def results_url(self):
        return link(f'/{self.key}/results')

    def vote_url(self):
        return full_link(f'/{self.key}')

    def cast_url(self, i):
        return link(f'/{self.key}/{i}')

    def to_dict(self):
        return self.__dict__

    def enumerate_options(self, show):
        opts = list(enumerate(self.options))
        if not show:
            # return options in random (but always the same) order
            random.Random(self.key).shuffle(opts)
        return opts

    @staticmethod
    def from_dict(d):
        p = object.__new__(Poll)
        p.__dict__.update(d)
        return p

class Backup:
    @staticmethod
    def save():
        if not BACKUP_FILE:
            return
        print()
        print(f'Saving {len(polls)} polls to {BACKUP_FILE}')
        with open(BACKUP_FILE, 'w') as f:
            f.write(json.dumps([p.to_dict() for p in polls.values()]))

    @staticmethod
    def load():
        if not BACKUP_FILE:
            return
        try:
            with open(BACKUP_FILE) as f:
                backup = json.loads(f.read())
                for p in backup:
                    polls[p['key']] = Poll.from_dict(p)
                print(f'Loaded {len(backup)} polls from {BACKUP_FILE}')
        except Exception as e:
            print(f'Could not load backup file {BACKUP_FILE}: {e}')

def evict_old_polls():
    while len(polls) > 100:
        key, _ = polls.popitem(last=False)
        print(f'Evicted poll {key}')

def get_poll(key):
    return polls.get(key, None) or error(404, 'Not Found')

_GITHUB_LINK = '''<a href="https://github.com/dessaya/simplepoll" class="github-corner" aria-label="View source on GitHub"><svg width="80" height="80" viewBox="0 0 250 250" style="fill:#151513; color:#fff; position: absolute; top: 0; border: 0; right: 0;" aria-hidden="true"><path d="M0,0 L115,115 L130,115 L142,142 L250,250 L250,0 Z"></path><path d="M128.3,109.0 C113.8,99.7 119.0,89.6 119.0,89.6 C122.0,82.7 120.5,78.6 120.5,78.6 C119.2,72.0 123.4,76.3 123.4,76.3 C127.3,80.9 125.5,87.3 125.5,87.3 C122.9,97.6 130.6,101.9 134.4,103.2" fill="currentColor" style="transform-origin: 130px 106px;" class="octo-arm"></path><path d="M115.0,115.0 C114.9,115.1 118.7,116.5 119.8,115.4 L133.7,101.6 C136.9,99.2 139.9,98.4 142.2,98.6 C133.8,88.0 127.5,74.4 143.8,58.0 C148.5,53.4 154.0,51.2 159.7,51.0 C160.3,49.4 163.2,43.6 171.4,40.1 C171.4,40.1 176.1,42.5 178.8,56.2 C183.1,58.6 187.2,61.8 190.9,65.4 C194.5,69.0 197.7,73.2 200.1,77.6 C213.8,80.2 216.3,84.9 216.3,84.9 C212.7,93.1 206.9,96.0 205.4,96.6 C205.1,102.4 203.0,107.8 198.3,112.5 C181.9,128.9 168.3,122.5 157.7,114.1 C157.9,116.9 156.7,120.9 152.7,124.9 L141.0,136.5 C139.8,137.7 141.6,141.9 141.8,141.8 Z" fill="currentColor" class="octo-body"></path></svg></a><style>.github-corner:hover .octo-arm{animation:octocat-wave 560ms ease-in-out}@keyframes octocat-wave{0%,100%{transform:rotate(0)}20%,60%{transform:rotate(-25deg)}40%,80%{transform:rotate(10deg)}}@media (max-width:500px){.github-corner:hover .octo-arm{animation:none}.github-corner .octo-arm{animation:octocat-wave 560ms ease-in-out}}</style>'''

def html(s):
    markdown_p = 'display: inline-block; margin-bottom: 0;'
    return f'''
        <!doctype html><html><head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/yegor256/tacit@gh-pages/tacit-css-1.5.1.min.css"/>
        <style>
            td {{ vertical-align: middle; }}
            h1:first-of-type, h2:first-of-type {{ margin-top: 0; }}
            body {{ background: #f0f0f0; }}
            tbody tr:hover {{ background: #f0f0f0; }}
            table {{ width: auto; }}
            td, th {{ border: none; }}
            form, fieldset {{ margin-bottom: 0; }}
            form label p {{ {markdown_p} }}
            th p {{ {markdown_p} }}
            .question {{
                border-bottom: 1px solid #f0f0f0;
                margin-bottom: 1em;
            }}
        </style>
        <title>SimplePoll</title>
        </head><body><section>
            <article>{s}</article>
            <footer><nav><ul><li><a class="brand" href="{link('/')}">SimplePoll</a></li></ul></nav></footer>
        </section>{_GITHUB_LINK}</body></html>
    '''

def error(status, msg):
    raise HTTPResponse(html(f'<h1>Oops</h1><p>{msg}</p>'), status)

@route('/', method="GET")
def index():
    nl = '\n'
    return html(f'''
        <h2>Step 1: Configure your poll</h2>
        <form action="{link('/')}" method="post">
            <label for="question">Poll question</label>
            <textarea style="width: 100%" name="question" id="question" rows="3" cols="50" placeholder="What is your favorite ice cream flavor?"></textarea>
            <label for="options">Options (one per line)</label>
            <textarea style="width: 100%" id="options" name="options" rows="5" cols="50" placeholder="Vanilla{nl}Chocolate{nl}Strawberry"></textarea>
            <label><input type="checkbox" name="multiple_choice">Multiple choice</label>
            <div><label><strong>Tip:</strong> You can use <a href="https://www.markdownguide.org/basic-syntax/">Markdown</a>!</label></div>
            <div><input type="submit" value="Create poll"></div>
        </form>
    ''')


@route('/', method="POST")
def create_poll():
    question = md.reset().convert(request.forms.question.strip())
    options = [
        md.reset().convert(s.strip())
        for s in request.forms.options.split('\n')
        if s.strip()
    ]
    multiple_choice = request.forms.multiple_choice == "on"

    if len(options) < 2:
        error(400, 'We need at least 2 options.')

    for _ in range(5):
        poll = Poll(question, options, multiple_choice)
        if poll.key not in polls:
            break
    else:
        error(500, 'Failed to find an unused key')

    polls[poll.key] = poll
    evict_old_polls()

    redirect(poll.admin_url())

@route('/<key>/admin', method="GET")
def poll_admin(key):
    poll = get_poll(key)
    return html(template(
        '''
            <script>
            function copy(s, btn) {
                navigator.clipboard.writeText(s).then(() => { btn.innerHTML = "Copied!"; });
            }
            </script>
            <h2>Step 2: Share the poll link to your audience</h2>
            % vote_url = poll.vote_url()
            <center>
            <div><a style="font-size:xx-large" href="{{!vote_url}}">{{!vote_url}}</a></large>
            <div><button style="font-size:smaller" onclick="copy('{{!vote_url}}', this)">Copy to clipboard</button></div>
            </center>
            <h2>Step 3: View the results</h2>
            <center><a href="{{!poll.results_url()}}"><button>View poll results</button></a></center>
        ''',
        poll=poll,
    ))

@route('/<key>/results', method="GET")
def poll_results(key):
    return html(template(
        '''
            <div class="question">{{!poll.question}}</div>
            <p>Responses: {{!poll.responses_count}}</p>
            <center><table>
                <tbody>
                % for (i, option) in poll.enumerate_options(show):
                    % p = poll.percentage(i)
                    % option = option if show else '???'
                    <tr>
                        <th style="max-width: 50%; text-align: end;">{{!option}}</th>
                        <td style="text-align: end; padding: 0 1em;"><nobr>{{!poll.responses[i]}} votes</nobr></td>
                        <td style="text-align: end;"><nobr>{{p}}%</nobr></td>
                        <td style="min-width: 200px"><div style="width:100%; height: 1em; border: 1px solid #007bff; background: #fff"><div style="width:{{!p}}%; height:100%; background-color: #007bff"></div></div></td>
                    </tr>
                % end
                </tbody>
            </table></center>
            % if not show:
                <center><a href="?show"><button>Show results!</button></a></center>
            % end
            <a href="{{!poll.admin_url()}}">Back to admin page</a>
        ''',
        poll=get_poll(key),
        show='show' in request.query,
    ))

@route('/<key>', method="GET")
def poll_vote_form(key):
    poll = get_poll(key)
    return html(template(
        '''
            <div class="question">{{!poll.question}}</div>
            <form action="{{!poll.vote_url()}}" method="post">
                <fieldset>
                % type = 'checkbox' if poll.multiple_choice else 'radio'
                % required = '' if poll.multiple_choice else 'required'
                % for (i, option) in enumerate(poll.options):
                    <label><input type="{{!type}}" name="option" value="{{!i}}" {{!required}}>{{!option}}</label>
                % end
                <input type="submit" value="Vote">
                </fieldset>
            </form>
        ''',
        poll=poll,
    ))

@route('/<key>', method="POST")
def poll_cast_vote(key):
    votes = [int(i) for i in request.forms.getall('option')]
    get_poll(key).cast_vote(votes)
    return html('<h1>Thank you for participating!</h1>')

polls = OrderedDict()
Backup.load()
try:
    run(host='localhost', port=PORT)
finally:
    Backup.save()
