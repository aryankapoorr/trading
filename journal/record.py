#!/usr/bin/env python3
"""Append or close a row in the trade journal. Stdlib only.

Open (after a buy-to-open fills or is placed):
  python3 journal/record.py open --file PATH --json '{"underlying":"XLU","option_type":"call",
    "strike":"44","expiration":"2026-12-18","quantity":"1","entry_time_utc":"2026-11-25T17:37:00Z",
    "entry_price":"0.67","entry_underlying_px":"43.59","entry_sma10":"43.49","entry_sma30":"43.08",
    "entry_rsi14":"56.2","entry_delta":"0.45","entry_iv":"0.19","entry_order_id":"...",
    "rules_version":"<git short sha>"}'

Close (after a sell-to-close is placed):
  python3 journal/record.py close --file PATH --json '{"underlying":"XLU","option_type":"call",
    "strike":"44","expiration":"2026-12-18","exit_time_utc":"...","exit_price":"1.10",
    "exit_underlying_px":"45.0","exit_sma10":"44.1","exit_rsi14":"79.2",
    "exit_reason":"signal_exit","exit_order_id":"..."}'

exit_reason is one of: signal_exit, dte_time_stop, earnings_proximity,
manual_close, expired, other. Live entries are tagged signal_source=live;
live delta/IV go in entry_delta_est / entry_iv_est (the same columns the
backfill estimated).
"""
import argparse, csv, json, sys
from datetime import date
from pathlib import Path

COLS = ['trade_id','status','underlying','option_type','strike','expiration','quantity','entry_time_utc','entry_price','entry_cost',
 'entry_dte','entry_underlying_px','entry_sma10','entry_sma30','entry_rsi14','entry_delta_est','entry_iv_est','earnings_before_expiry',
 'entry_rule_match','exit_time_utc','exit_price','exit_proceeds','exit_dte','exit_underlying_px','exit_sma10','exit_rsi14','exit_reason',
 'exit_placed_by','holding_days','pnl','return_pct','rules_version','signal_source','entry_order_id','exit_order_id','notes']
REASONS = {'signal_exit','dte_time_stop','earnings_proximity','manual_close','expired','other'}

def norm_strike(s): return ('%f' % float(s)).rstrip('0').rstrip('.')
def key(r): return (r['underlying'].upper(), r['option_type'].lower(), norm_strike(r['strike']), r['expiration'])

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('action', choices=['open', 'close'])
    ap.add_argument('--file', default=str(Path(__file__).with_name('trades.csv'))); ap.add_argument('--json', required=True)
    a = ap.parse_args(); d = json.loads(a.json); path = Path(a.file)
    rows = list(csv.DictReader(open(path))) if path.exists() else []
    if a.action == 'open':
        if any(r.get('entry_order_id') == d.get('entry_order_id') for r in rows if d.get('entry_order_id')):
            print('already recorded'); return
        day = d['entry_time_utc'][:10]; qty = int(float(d.get('quantity', 1)))
        r = {c: '' for c in COLS}
        r.update(underlying=d['underlying'].upper(), option_type=d['option_type'].lower(), strike=norm_strike(d['strike']),
                 expiration=d['expiration'], quantity=str(qty), entry_time_utc=d['entry_time_utc'], entry_price=d['entry_price'],
                 entry_cost='%.2f' % (float(d['entry_price']) * 100 * qty),
                 entry_dte=str((date.fromisoformat(d['expiration']) - date.fromisoformat(day)).days),
                 entry_underlying_px=d.get('entry_underlying_px', ''), entry_sma10=d.get('entry_sma10', ''),
                 entry_sma30=d.get('entry_sma30', ''), entry_rsi14=d.get('entry_rsi14', ''),
                 entry_delta_est=d.get('entry_delta', ''), entry_iv_est=d.get('entry_iv', ''),
                 earnings_before_expiry='False', entry_rule_match='True', status='open', signal_source='live',
                 rules_version=d.get('rules_version', ''), entry_order_id=d.get('entry_order_id', ''), notes=d.get('notes', ''))
        r['trade_id'] = f"{day}-{r['underlying']}-{r['option_type'][0].upper()}{r['strike']}"
        rows.append(r)
    else:
        if d.get('exit_reason') not in REASONS: sys.exit(f"exit_reason must be one of {sorted(REASONS)}")
        k = key(d); hits = [r for r in rows if r['status'] == 'open' and key(r) == k]
        if not hits: sys.exit(f'no open journal row for {k}')
        r = hits[0]; qty = int(float(r['quantity'] or 1)); day = d['exit_time_utc'][:10]
        pnl = (float(d['exit_price']) - float(r['entry_price'])) * 100 * qty
        r.update(status='closed', exit_time_utc=d['exit_time_utc'], exit_price=d['exit_price'],
                 exit_proceeds='%.2f' % (float(d['exit_price']) * 100 * qty),
                 exit_dte=str((date.fromisoformat(r['expiration']) - date.fromisoformat(day)).days),
                 exit_underlying_px=d.get('exit_underlying_px', ''), exit_sma10=d.get('exit_sma10', ''),
                 exit_rsi14=d.get('exit_rsi14', ''), exit_reason=d['exit_reason'], exit_placed_by=d.get('exit_placed_by', 'agentic'),
                 holding_days=str((date.fromisoformat(day) - date.fromisoformat(r['entry_time_utc'][:10])).days),
                 pnl='%.2f' % pnl, return_pct='%.1f' % (pnl / float(r['entry_cost']) * 100), exit_order_id=d.get('exit_order_id', ''))
        if d.get('notes'): r['notes'] = (r['notes'] + ' ' + d['notes']).strip()
    w = csv.DictWriter(open(path, 'w', newline=''), fieldnames=COLS); w.writeheader(); w.writerows(rows)
    print(f"{a.action}: {r['trade_id']} ({r['status']})")

if __name__ == '__main__': main()
