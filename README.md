# claude-trader

An unattended leveraged ETF rotation routine for a Robinhood **Agentic** account,
run via Claude Code Routines (cloud-scheduled, no local machine required).

## How it works
- `CLAUDE.md` holds the full strategy + rules. Claude Code reads it automatically
  on every run.
- A Claude Code Routine runs hourly on weekdays (`0 * * * 1-5`). Each run clones
  this repo, reads `CLAUDE.md`, and executes.
- The routine uses the **Robinhood** MCP connector to read the account and
  place equity orders.

## Strategy (summary — see CLAUDE.md for exact rules)
- Long-only momentum rotation across 9 leveraged ETFs (3x) spanning tech,
  semiconductors, financials, energy, biotech, small caps, and regional banks.
- $50 per new position, max 6 concurrent, cash account.
- Signals computed on the **underlying** ETF (QQQ, SPY, XLK, etc.), not the
  leveraged wrapper — cleaner price history, no decay distortion.
- Entry: underlying in short-term uptrend (price > SMA10 > SMA30), RSI 40–72.
- Exit: underlying breaks 3% below SMA10, or RSI > 78.
## Session & order types
- Pre-market (7am–9:30am ET): limit orders only.
- Regular (9:30am–4pm ET): market orders.
- After-hours (4pm–8pm ET): limit orders only.
- Tradability confirmed via Robinhood API before every extended-hours order.

## Audit trail
- Each run's full output (decision table + news checks + order reviews) is
  visible in the routine's run history on claude.ai.
- All trades also appear in the Robinhood app's agent activity feed.

## Safety notes
- Cash account: never buys with unsettled proceeds.
- This is a small-stakes experiment. Treat the funded amount as money you are
  fully prepared to lose. Leveraged ETFs can lose value rapidly.
