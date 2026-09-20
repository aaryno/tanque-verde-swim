import subprocess, json, os, sys, time, urllib.request, base64
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp import WS
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
url, shot = sys.argv[1], sys.argv[2]
prof = "/tmp/tvmobile/chrome-ws-profile"; os.makedirs(prof, exist_ok=True)
p = subprocess.Popen([CHROME, "--headless=new", "--remote-debugging-port=9334",
    f"--user-data-dir={prof}2", "--no-first-run", "--no-default-browser-check",
    "--disable-gpu", "--hide-scrollbars", "--window-size=390,2800",
    "--force-device-scale-factor=1", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(100):
        try: urllib.request.urlopen("http://127.0.0.1:9334/json/version", timeout=1).read(); break
        except Exception: time.sleep(0.2)
    time.sleep(2.5)
    tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:9334/json/list").read())
    ws = WS([x for x in tabs if x["type"]=="page"][0]["webSocketDebuggerUrl"])
    ws.call("Runtime.enable"); ws.call("Page.enable")
    probe = """(()=>{
      const W = document.documentElement.clientWidth;
      // what content would be lost if the capture were cropped to 390?
      const lost = [];
      document.querySelectorAll('h1,h2,h3,td,th,p,li,a').forEach(el=>{
        const cs=getComputedStyle(el); if(cs.display==='none') return;
        const r=el.getBoundingClientRect(); if(!r.width) return;
        if (r.right > 390.5) lost.push({tag:el.tagName, left:+r.left.toFixed(1), right:+r.right.toFixed(1),
             text:(el.textContent||'').trim().slice(0,45)});
      });
      return {clientWidth:W, scrollWidth:document.scrollingElement.scrollWidth,
              pastCrop390: lost.length, sample: lost.slice(0,8)};
    })()"""
    r = ws.call("Runtime.evaluate", {"expression": probe, "returnByValue": True})
    print(json.dumps(r["result"]["value"], indent=1))
    s = ws.call("Page.captureScreenshot", {"format":"png","captureBeyondViewport":True})
    os.makedirs(os.path.dirname(shot), exist_ok=True); open(shot,"wb").write(base64.b64decode(s["data"]))
    from PIL import Image; print("screenshot size:", Image.open(shot).size)
finally: p.terminate()
