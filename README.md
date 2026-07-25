# claude-trader

An unattended options momentum routine for a Robinhood **Agentic** account,
run via Claude Code Routines (cloud-scheduled, no local machine required).

## How it works
- `CLAUDE.md` holds the full strategy + rules. Claude Code reads it automatically
  on every run.
- A Claude Code Routine runs every 2 hours during market hours on weekdays
  (`0 13-20/2 * * 1-5` UTC — ~9am, 11am, 1pm, 3pm ET; adjust by 1 hour around
  DST changes). Each run clones this repo, reads `CLAUDE.md`, and executes.
  Entries are daily-bar signals (no benefit from checking faster), and exits
  are capped-loss long options, so 2-hour granularity trades a little
  exit-reaction speed for roughly half the API/compute overhead of hourly.
- The routine uses the **Robinhood** MCP connector to read the account and
  place single-leg options orders.

## Strategy (summary — see CLAUDE.md for exact rules)
- Long-only options momentum: long calls on bullish signals, long puts on
  bearish signals. Both are debit-only (no margin, no shorting).
- Universe is discovered dynamically each run via a saved Robinhood scanner
  (liquid, optionable, $20–120 stocks/ETFs with real options volume and open
  interest), not a fixed ticker list — plus a small fixed anchor list of
  major index/sector ETFs (SPY, QQQ, IWM, DIA, XLF, XLK, XLE, XLU, SMH) as a
  liquidity backstop.
- Signals computed on the underlying via SMA10/SMA30/RSI14 (mirrored bands
  for calls vs. puts).
- Target spend ~$150–250 per contract (hard ceiling $260), targeting
  moderate delta (0.35–0.55), ~21–31 days to expiration. Max 3 concurrent
  positions, max 1 new opening order per run. Funding target: at least
  ~$840 (3 x $260 ceiling + $60 reserve), ideally ~$900–1,000 for headroom —
  below that, expect fewer than 3 positions to be achievable at once.
- Exit on signal reversal, a 7-day DTE time-stop, or an earnings date within
  5 days of expiration.
## Session & order types
- Options don't support extended-hours trading — orders only place during
  the regular session (9:30am–4pm ET), always as limit orders (ask for buys,
  bid for sells).
- Outside regular hours, a market-hours gate stops the run before any tool
  is called at all — no account check, no analysis, no decision table.
  Since options can never place outside the session anyway, there's nothing
  useful to compute, so this avoids burning tokens/API calls on a run that
  couldn't act.

## Audit trail
- Each run's full output (decision table + earnings checks + order reviews) is
  visible in the routine's run history on claude.ai.
- All trades also appear in the Robinhood app's agent activity feed.

## Safety notes
- Cash account: never buys with unsettled proceeds.
- This is a small-stakes experiment. Treat the funded amount as money you are
  fully prepared to lose. Long options can lose their entire premium.
