# claude-trader

An unattended equities trading routine for a Robinhood **Agentic** account,
run via Claude Code Routines (cloud-scheduled, no local machine required).

## How it works
- `CLAUDE.md` holds the full strategy + rules. Claude Code reads it automatically
  on every run.
- A Claude Code Routine is scheduled on weekdays at fixed times (e.g. 10:00,
  12:00, 14:00 ET). Each run clones this repo, reads `CLAUDE.md`, and executes.
- The routine uses the connected **Robinhood** MCP connector to read the account
  and place equity orders.

## Strategy (summary — see CLAUDE.md for exact rules)
- Long-only trend/momentum on a fixed ~25-symbol liquid universe.
- $50 per new position, max 6 concurrent, equities only (account is cash).
- Buy established uptrends (price > SMA50 > SMA200, RSI 40–70); exit on trend
  break (price < SMA50 by 2%) or RSI > 80.
- Reviews every order before placing it, and prints an audit table each run.

## Audit trail
- Each routine run's full output (the decision table + order reviews) is visible
  in the routine's run history on claude.ai.
- All trades also appear in the Robinhood app's agent activity feed.

## Safety notes
- Equities only — options/crypto are not available on the agentic account yet.
- Cash account: never buys with unsettled proceeds.
- Market-open guard: does nothing when the market is closed.
- This is a small-stakes experiment. Treat the funded amount as money you are
  fully prepared to lose.
