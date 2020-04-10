import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <base-url>")
    sys.exit(1)

base = sys.argv[1].rstrip('/')
question = input("Question: ")
options = []
while True:
    option = input("Option (leave blank when done): ")
    if not option:
        break
    options.append(option)

if len(options) < 2:
    print(f"We need at least 2 options.")
    sys.exit(1)

responses = {}

def percentage(i):
    total = sum(v for k, v in responses.items())
    if not total:
        return 0
    return int((responses.get(i, 0) / total) * 100 + 0.5)

def format_responses():
    s = [question, '']
    for (i, option) in enumerate(options):
        s.append(f'{option}: {responses.get(i, 0)} ({percentage(i)}%)')
    return '\n'.join(s)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def send(self, code, s):
        s = (f'''<!doctype html>
<html><head><meta charset="utf-8"></head>
<body>
<pre style="font-size: xxx-large">
{s}
</pre>
</body>
</html>''').encode('utf8')
        self.send_response(code)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", len(s))
        self.end_headers()
        self.wfile.write(s)

    def do_GET(self):
        if self.path == '/responses':
            self.send(200, format_responses())
            return
        if not self.path[1:].isdigit():
            self.send(404, 'Not found')
            return
        n = int(self.path[1:])
        if not 0 <= n < len(options):
            raise Exception(f"Invalid URL: {self.path}")
        responses[n] = responses.get(n, 0) + 1
        self.send(200, f'You voted: {options[n]}')

print()
print(f"Listening on 0.0.0.0:8000")
print(f'Poll results at {base}/responses')
print(f"Send the following to your audience:")
print()
print(question)
for (i, option) in enumerate(options):
    print(f'{option}: {base}/{i}')

httpd = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
httpd.serve_forever()
