import sys, json, time, base64, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp import launch_chrome, page_ws

PROBE = r"""
(() => {
  const VW = document.documentElement.clientWidth;
  const out = {viewport: VW,
    innerWidth: window.innerWidth,
    scrollWidth: document.scrollingElement.scrollWidth,
    bodyScrollWidth: document.body.scrollWidth,
    devicePixelRatio: window.devicePixelRatio,
    overflow: [], probes: {}};
  const seen = new Set();
  document.querySelectorAll('*').forEach(el => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return;
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) return;
    if (r.right > VW + 0.5 || r.left < -0.5) {
      const key = el.tagName + '|' + (el.className||'') + '|' + Math.round(r.left) + '|' + Math.round(r.right);
      if (seen.has(key)) return; seen.add(key);
      out.overflow.push({tag: el.tagName, cls: (typeof el.className === 'string' ? el.className : ''),
        id: el.id||'', left: +r.left.toFixed(1), right: +r.right.toFixed(1),
        width: +r.width.toFixed(1),
        text: (el.textContent||'').trim().slice(0,60)});
    }
  });
  // text clipping: element's own content wider than its box
  const clip = [];
  document.querySelectorAll('h1,h2,h3,p,td,th,li,a,span,div').forEach(el => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none') return;
    if (el.scrollWidth > el.clientWidth + 1 && el.clientWidth > 0 &&
        (cs.overflow === 'hidden' || cs.overflowX === 'hidden' || cs.textOverflow === 'ellipsis' || cs.whiteSpace === 'nowrap')) {
      clip.push({tag: el.tagName, cls: (typeof el.className==='string'?el.className:''),
        scrollWidth: el.scrollWidth, clientWidth: el.clientWidth,
        whiteSpace: cs.whiteSpace, overflowX: cs.overflowX,
        text: (el.textContent||'').trim().slice(0,50)});
    }
  });
  out.clipped = clip;
  const probe = (sel, name) => {
    const el = document.querySelector(sel);
    if (!el) { out.probes[name] = null; return; }
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    out.probes[name] = {left:+r.left.toFixed(1), right:+r.right.toFixed(1), width:+r.width.toFixed(1),
      scrollWidth: el.scrollWidth, clientWidth: el.clientWidth,
      fontSize: cs.fontSize, whiteSpace: cs.whiteSpace, overflowX: cs.overflowX,
      text:(el.textContent||'').trim().slice(0,60)};
  };
  probe('.hero-expanded h1','h1');
  probe('.hero-expanded h2','h2');
  probe('.hero-expanded .subtitle','subtitle');
  probe('#season-content p.lead','season_lead');
  probe('#schedule-content p.lead','schedule_lead');
  probe('#schedule-content table','schedule_table');
  probe('#schedule-content .table-responsive','schedule_wrap');
  probe('body','body');
  probe('#main-nav','main_nav');
  // every schedule date cell
  out.dates = [...document.querySelectorAll('#schedule-content tbody tr')].map(tr => {
    const td = tr.querySelector('td');
    const r = td.getBoundingClientRect();
    const rr = tr.getBoundingClientRect();
    return {text: td.textContent.trim(), left:+r.left.toFixed(1), right:+r.right.toFixed(1),
            cellW:+r.width.toFixed(1), contentW: td.scrollWidth,
            rowLeft:+rr.left.toFixed(1), rowRight:+rr.right.toFixed(1)};
  });
  // every 'Where' cell
  out.where = [...document.querySelectorAll('#schedule-content tbody tr')].map(tr => {
    const tds = tr.querySelectorAll('td');
    const td = tds[tds.length-1];
    const r = td.getBoundingClientRect();
    return {text: td.textContent.trim().slice(0,40), left:+r.left.toFixed(1), right:+r.right.toFixed(1), width:+r.width.toFixed(1)};
  });
  return out;
})()
"""

def run(url, width, height, shot=None, mobile=True, probe=PROBE, ws=None, full=True):
    ws.call("Page.enable"); ws.call("Runtime.enable")
    ws.call("Emulation.setDeviceMetricsOverride", {
        "width": width, "height": height, "deviceScaleFactor": 1, "mobile": mobile,
        "screenWidth": width, "screenHeight": height})
    ws.call("Emulation.setUserAgentOverride", {"userAgent":
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"})
    ws.call("Page.navigate", {"url": url})
    time.sleep(2.2)
    res = ws.call("Runtime.evaluate", {"expression": probe, "returnByValue": True})
    val = res["result"].get("value")
    if shot:
        params = {"format": "png"}
        if full:
            params["captureBeyondViewport"] = True
        s = ws.call("Page.captureScreenshot", params)
        os.makedirs(os.path.dirname(shot), exist_ok=True)
        with open(shot, "wb") as f:
            f.write(base64.b64decode(s["data"]))
    return val

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("url"); ap.add_argument("--width", type=int, default=390)
    ap.add_argument("--height", type=int, default=844)
    ap.add_argument("--shot"); ap.add_argument("--viewport-only", action="store_true")
    a = ap.parse_args()
    proc = launch_chrome()
    try:
        ws = page_ws()
        v = run(a.url, a.width, a.height, a.shot, ws=ws, full=not a.viewport_only)
        print(json.dumps(v, indent=1))
    finally:
        proc.terminate()
