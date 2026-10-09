#!/usr/bin/python3
# =============================================================================
# bezel_1.py — the structured-product fee autopsy (defined-outcome / buffered ETFs).
#
# A bezel is the frame that holds the stone — you pay for the setting, not the gem. Buffered /
# defined-outcome ETFs (Innovator BUFR, DFND, BALT…) sell a downside "buffer" in exchange for a cap on
# upside. BLOCK's law: a modification never conjures return, it relocates risk onto an axis the buyer
# isn't watching. This finds where the fee lives:
#   Q1  Scorecard: does the buffer cushion drawdowns — and what does it cost in return? (vs SPY)
#   Q2  WHERE THE FEE LIVES — decompose the gap to SPY into forgone dividends + cap drag + expense.
#   Q3  Up/down capture — did the buffer earn its price over the cycle, or only in the bad year?
#   Q4  Replicate it cheaper — does a plain SPY+cash "poor-man's buffer" match the risk profile?
# Self-contained; Alpaca SIP daily. SPY fetched BOTH total-return (adjustment=all) and price-only
# (adjustment=split) to expose the forgone-dividend fee the buffer quietly charges.
# =============================================================================
import os, json, math, urllib.request
import numpy as np

H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"]}
START, END = "2016-01-01", "2026-08-01"; _c = {}

def bars(s, adj="all"):
    k = (s, adj)
    if k in _c: return _c[k]
    u = (f"https://data.alpaca.markets/v2/stocks/bars?symbols={s}&timeframe=1Day&start={START}&end={END}"
         f"&adjustment={adj}&feed=sip&limit=10000")
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40))
        _c[k] = {b["t"][:10]: b["c"] for b in d.get("bars", {}).get(s, [])}
    except Exception: _c[k] = {}
    return _c[k]

def panel(specs):   # specs: list of (alias, symbol, adj)
    D = {a: bars(s, adj) for a, s, adj in specs}; D = {a: v for a, v in D.items() if len(v) > 250}
    dts = sorted(set.intersection(*[set(D[a]) for a in D]))
    return {a: np.array([D[a][d] for d in dts], float) for a in D}, dts

def rets(px): return px[1:] / px[:-1] - 1
def ann(r): r = np.asarray(r, float); c = np.cumprod(1+r); return c[-1]**(252/len(r))-1
def stats(r, months):
    r = np.asarray(r, float); c = np.cumprod(1+r); dd = (c/np.maximum.accumulate(c)-1).min()
    sh = r.mean()/r.std()*math.sqrt(252) if r.std()>0 else float("nan"); z=(r-r.mean())/r.std()
    mo = {}
    for m,x in zip(months,r): mo[m]=mo.get(m,1.0)*(1+x)
    return dict(sh=sh, cagr=ann(r), dd=float(dd), skew=float(np.mean(z**3)), worst=min(v-1 for v in mo.values()))

BUFFERED = ["BUFR", "DFND", "BALT"]

def main():
    specs = [("SPY","SPY","all"), ("SPYpx","SPY","split"), ("IEF","IEF","all"), ("BIL","BIL","all")] \
            + [(b, b, "all") for b in BUFFERED]
    P, dates = panel(specs); R = {a: rets(P[a]) for a in P}
    L = min(len(R[a]) for a in R); months = [d[:7] for d in dates[1:]][-L:]
    buf = [b for b in BUFFERED if b in R]
    print("="*92); print("BEZEL — the structured-product fee autopsy (buffered / defined-outcome ETFs)"); print("="*92)
    print(f"  window {dates[-L]}..{dates[-1]}  ({L/252:.1f}y)   buffered present: {', '.join(buf)}")
    spy, spypx = R["SPY"][-L:], R["SPYpx"][-L:]

    # ---- Q1: scorecard --------------------------------------------------------------------
    print("\n  Q1  SCORECARD — does the buffer cushion, and what does it cost?")
    print(f"      {'fund':8}{'Sharpe':>8}{'CAGR':>8}{'maxDD':>8}{'worstMo':>9}{'skew':>7}{'corr→SPY':>10}")
    for b in buf:
        s = stats(R[b][-L:], months); cc = np.corrcoef(R[b][-L:], spy)[0,1]
        print(f"      {b:8}{s['sh']:>+8.2f}{s['cagr']*100:>+7.1f}%{s['dd']*100:>+7.0f}%{s['worst']*100:>+8.1f}%{s['skew']:>+7.2f}{cc:>+10.2f}")
    ss = stats(spy, months); print(f"      {'SPY':8}{ss['sh']:>+8.2f}{ss['cagr']*100:>+7.1f}%{ss['dd']*100:>+7.0f}%{ss['worst']*100:>+8.1f}%{ss['skew']:>+7.2f}{1.0:>+10.2f}")

    # ---- Q2: where the fee lives -----------------------------------------------------------
    print("\n  WHERE THE FEE LIVES (annualized, vs SPY total return)")
    div = ann(spy) - ann(spypx)                      # forgone dividends (buffered track PRICE return)
    print(f"      SPY total return .............. {ann(spy)*100:+.1f}%/yr")
    print(f"      SPY price-only (no dividends) . {ann(spypx)*100:+.1f}%/yr   → forgone dividends = {div*100:.1f}%/yr (hidden fee #1)")
    for b in buf:
        gap_px = ann(spypx) - ann(R[b][-L:])         # cap drag + expense, vs price return
        total_gap = ann(spy) - ann(R[b][-L:])
        print(f"      {b}: total give-up vs SPY {total_gap*100:+.1f}%/yr = forgone divs {div*100:.1f}% + cap/expense {gap_px*100:+.1f}%")

    # ---- Q3: up / down capture -------------------------------------------------------------
    print("\n  Q3  UP / DOWN CAPTURE (did the buffer earn its price?)")
    up, dn = spy > 0, spy < 0
    for b in buf:
        rb = R[b][-L:]
        uc = rb[up].mean()/spy[up].mean()*100 if spy[up].mean()!=0 else float("nan")
        dc = rb[dn].mean()/spy[dn].mean()*100 if spy[dn].mean()!=0 else float("nan")
        print(f"      {b}: up-capture {uc:4.0f}%   down-capture {dc:4.0f}%   (buffer value = 100 − down-capture; cost = 100 − up-capture)")

    # ---- Q4: replicate cheaper -------------------------------------------------------------
    print("\n  Q4  POOR-MAN'S BUFFER — plain SPY+cash vs the structure")
    for frac in (0.70, 0.80):
        diy = frac*spy + (1-frac)*R["BIL"][-L:]; s = stats(diy, months)
        print(f"      {int(frac*100)}% SPY / {int((1-frac)*100)}% cash: Sharpe {s['sh']:+.2f}  CAGR {s['cagr']*100:+.1f}%  maxDD {s['dd']*100:+.0f}%  skew {s['skew']:+.2f}")
    bb = stats(R[buf[0]][-L:], months); print(f"      {buf[0]} (for reference): Sharpe {bb['sh']:+.2f}  CAGR {bb['cagr']*100:+.1f}%  maxDD {bb['dd']*100:+.0f}%  skew {bb['skew']:+.2f}")

    print("\n  READ: the buffer is REAL (down-capture < 100%), but you pay three ways — forgone dividends,")
    print("  a hard cap (up-capture < 100%), and the expense. Over a bull cycle the cap+divs cost more than")
    print("  the buffer saves; a plain SPY+cash mix often matches the drawdown cheaper. The fee lives in the")
    print("  dividend you forgo and the upside you cap — the axes the brochure doesn't print.")

if __name__ == "__main__":
    main()
