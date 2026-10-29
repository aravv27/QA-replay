import os, time, html
from flask import Flask, request

app = Flask(__name__)
KEY = os.environ.get("KEY", "aravind123")
TTL = 6 * 3600  # seconds before question/answer expire

data = {"q": "", "a": "", "t": 0}


def expire():
    if data["t"] and time.time() - data["t"] > TTL:
        data.update(q="", a="", t=0)


def ok():
    return request.args.get("key") == KEY


@app.post("/ask")
def ask():
    if not ok():
        return "bad key", 403
    data.update(q=request.get_data(as_text=True), a="", t=time.time())
    return "question saved"


@app.get("/answer")
def answer():
    if not ok():
        return "bad key", 403
    expire()
    return data["a"] or "no answer yet"


@app.post("/reply")
def reply():
    if not ok():
        return "bad key", 403
    data["a"] = request.form.get("a", "")
    return "Sent! You can close this page."


@app.get("/")
def page():
    if not ok():
        return "bad key", 403
    expire()
    q = html.escape(data["q"]) or "(no question yet - this page refreshes itself)"
    return f"""<!doctype html><meta name=viewport content="width=device-width,initial-scale=1">
<title>Question</title>
<body style="font-family:sans-serif;max-width:700px;margin:2em auto;padding:0 1em">
<h3>Question</h3><pre style="white-space:pre-wrap;background:#eee;padding:1em">{q}</pre>
<form method=post action="/reply?key={html.escape(KEY)}">
<h3>Your answer (paste code)</h3>
<textarea name=a rows=16 style="width:100%;font-family:monospace"></textarea><br>
<button style="margin-top:.5em;padding:.5em 1.5em">Send</button></form>
<script>setInterval(()=>fetch("/ping"),240000)</script></body>"""


@app.get("/ping")
def ping():
    return "pong"
