# Trade journal

`trades.csv` holds one row per option round trip: what the agent bought, the
signal values that justified it, how and why it closed, and the P&L. It is a
record for the weekly review (`review/WEEKLY_REVIEW.md`), never an input to
trading decisions.

## Where it lives

- Trading runs append to `journal/trades.csv` on the data branch
  **`claude/trade-journal`** (via `journal/sync.sh`), so trading runs never
  push to `main`.
- Each weekly review PR copies the latest journal into `main`, so `main`
  holds a snapshot as of the last merged review.

## Files

| File | Purpose |
|---|---|
| `trades.csv` | The journal. Rows with `signal_source=reconstructed` were backfilled from Robinhood history; `live` rows were written by a trading run. |
| `record.py` | Appends an `open` row or closes one: `python3 journal/record.py open|close --file PATH --json '{...}'`. |
| `sync.sh` | `pull` checks out the latest journal from `claude/trade-journal` into `/tmp/trade-journal`; `push "msg"` commits and pushes it back. |
| `analyze.py` | Prints win rate, P&L and breakdowns by bucket with a bootstrap interval: `python3 journal/analyze.py [csv]`. |
| `readout-*.md` | Written readouts. |

## Columns

`trade_id` (`YYYY-MM-DD-SYM-C|Pstrike`), `status` (open/closed), contract
fields, `entry_*` (time, fill price, cost, DTE, underlying price, SMA10,
SMA30, RSI14, delta, IV), `earnings_before_expiry`, `entry_rule_match`,
`exit_*` (time, price, proceeds, DTE, underlying price, SMA10, RSI14, reason,
placed_by), `holding_days`, `pnl` ($), `return_pct`, `rules_version` (git
short SHA of `CLAUDE.md` in force), `signal_source`, order ids, `notes`.

`exit_reason`: `signal_exit`, `dte_time_stop`, `earnings_proximity`,
`manual_close`, `expired`, `other` (backfill also uses
`signal_exit_unconfirmed`, see the first readout).
