import io
P="build.py"; s=io.open(P,encoding="utf-8").read()
def rep(a,b):
    global s
    assert a in s, a[:80]; s=s.replace(a,b,1)
rep('''    faqs += [(f["q"], f["a"]) for f in r["faqs"]][:2]\n''','')
a=s.index('<div class="block" id="process"><h2>How we process your application</h2>'); b=s.index('\n',a)
s=s[:a]+'''<div class="block" id="process"><h2>How the {e(c["name"])} application works</h2><p>Your file goes through consultation, documentation, appointment or online submission, and tracking. The full step-by-step process for {e(REGIONS[c["region"]]["name"])} visas is on the <a class="link" href="/countries/{c["region"]}">{e(REGIONS[c["region"]]["name"])} visa guide</a>.</p></div>'''+s[b:]
a=s.index('<div class="block"><h2>Why apply with us?</h2>'); b=s.index('</div>\n<div class="block" id="faqs">',a)
s=s[:a]+s[b+7:]
io.open(P,"w",encoding="utf-8").write(s); print("ok")
