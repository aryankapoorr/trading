#!/usr/bin/env python3
"""Summarize journal/trades.csv for the weekly review. Stdlib only.

Usage: python3 journal/analyze.py [path/to/trades.csv]
Prints overall stats, breakdowns by bucket, and a bootstrap confidence
interval on the average trade so the review can tell signal from noise.
"""
import csv, random, statistics, sys
from collections import defaultdict
from pathlib import Path

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name('trades.csv')
rows = list(csv.DictReader(open(path)))
closed = [r for r in rows if r['status'] == 'closed']
opened = [r for r in rows if r['status'] == 'open']
f = lambda r, k: float(r[k]) if r.get(k) not in (None, '') else None

def stats(rs):
    p = [f(r, 'pnl') for r in rs]
    w = [x for x in p if x > 0]; l = [x for x in p if x <= 0]
    return dict(n=len(p), wins=len(w), win_rate=len(w) / len(p) if p else 0, total=sum(p),
                avg=statistics.mean(p) if p else 0, avg_win=statistics.mean(w) if w else 0,
                avg_loss=statistics.mean(l) if l else 0,
                profit_factor=(sum(w) / -sum(l)) if l and sum(l) < 0 else float('inf'))

def line(label, s):
    return (f"{label:<28} n={s['n']:>3}  win {s['win_rate']:>4.0%}  total ${s['total']:>8.2f}  "
            f"avg ${s['avg']:>7.2f}  avg win ${s['avg_win']:>7.2f}  avg loss ${s['avg_loss']:>7.2f}")

def bucket(name, key_fn):
    groups = defaultdict(list)
    for r in closed: groups[key_fn(r)].append(r)
    print(f"\nBy {name}:")
    for k in sorted(groups, key=str): print('  ' + line(str(k), stats(groups[k])))

def dte_b(r):
    d = f(r, 'entry_dte'); return 'unknown' if d is None else ('<21' if d < 21 else '21-25' if d <= 25 else '26-31')
def delta_b(r):
    d = f(r, 'entry_delta_est')
    if d is None: return 'unknown'
    d = abs(d); return '<0.35' if d < 0.35 else '0.35-0.45' if d < 0.45 else '0.45-0.55' if d <= 0.55 else '>0.55'
def rsi_b(r):
    x = f(r, 'entry_rsi14')
    if x is None: return 'unknown'
    if r['option_type'] == 'call': return 'call RSI<55' if x < 55 else 'call RSI 55-62' if x < 62 else 'call RSI>=62'
    return 'put RSI<35' if x < 35 else 'put RSI 35-45' if x < 45 else 'put RSI>=45'
def hold_b(r):
    h = f(r, 'holding_days'); return '<=5d' if h <= 5 else '6-14d' if h <= 14 else '15d+'

if not closed:
    print('No closed trades yet.'); sys.exit()
s = stats(closed)
print(f"Journal: {path}  ({len(closed)} closed, {len(opened)} open)")
print(line('ALL CLOSED', s))
print(f"Profit factor {s['profit_factor']:.2f}")
pnls = sorted((f(r, 'pnl'), r['trade_id']) for r in closed)
best = pnls[-1]
print(f"Without the single best trade ({best[1]}, ${best[0]:.2f}): total ${s['total'] - best[0]:.2f}")
random.seed(0)
vals = [p for p, _ in pnls]
boots = sorted(statistics.mean(random.choices(vals, k=len(vals))) for _ in range(5000))
print(f"Bootstrap 90% interval on avg trade: ${boots[250]:.2f} to ${boots[4750]:.2f}"
      + ("  <- includes $0: no evidence of an edge either way yet" if boots[250] <= 0 <= boots[4750] else ""))
bucket('call vs put', lambda r: r['option_type'])
bucket('exit reason', lambda r: r['exit_reason'])
bucket('entry DTE', dte_b)
bucket('entry |delta| (estimated)', delta_b)
bucket('entry RSI14', rsi_b)
bucket('holding period', hold_b)
bucket('rules version', lambda r: r['rules_version'])
bucket('underlying', lambda r: r['underlying'])
if opened:
    print(f"\nOpen positions ({len(opened)}): " + ', '.join(r['trade_id'] for r in opened))
print("\nRule of thumb: treat any bucket with n < 10 as anecdote, not evidence.")
