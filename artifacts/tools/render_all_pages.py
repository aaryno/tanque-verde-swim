import sys, os, json, time, base64, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp import launch_chrome, page_ws

port, outdir, listfile = sys.argv[1], sys.argv[2], sys.argv[3]
pages = [l.strip() for l in open(listfile) if l.strip()]
os.makedirs(outdir, exist_ok=True)
proc = launch_chrome()
res = {}
try:
    ws = page_ws(); ws.call("Page.enable"); ws.call("Runtime.enable")
    ws.call("Emulation.setDeviceMetricsOverride", {"width":390,"height":844,
        "deviceScaleFactor":1,"mobile":True,"screenWidth":390,"screenHeight":844})
    for p in pages:
        ws.call("Page.navigate", {"url": f"http://127.0.0.1:{port}{p}"})
        time.sleep(1.4)
        s = ws.call("Page.captureScreenshot", {"format":"png","captureBeyondViewport":True})
        raw = base64.b64decode(s["data"])
        name = p.strip("/").replace("/","__") or "index.html"
        open(os.path.join(outdir, name + ".png"), "wb").write(raw)
        res[p] = hashlib.sha256(raw).hexdigest()
finally:
    proc.terminate()
json.dump(res, open(os.path.join(outdir, "hashes.json"), "w"), indent=1)
print(f"rendered {len(res)} pages -> {outdir}")
