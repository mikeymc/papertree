{analyst_persona} Your audience is the portfolio owner — they want to understand exactly what happened, why, and what it means.

## Run Statistics

- Total Universe: {universe_size}
- Total Universe: {universe_size}
- Candidates: {candidates}
- Qualifiers: {qualifiers}
- Theses: {theses}
- Targets: {targets}
- Trades: {trades}
- Portfolio value: ${portfolio_value:,.2f}
- Portfolio return: {portfolio_return_pct:.2f}%
- S&P 500 return: {spy_return_pct:.2f}%
- Alpha: {alpha:.2f}%

## Buys

{buys}

## Sells

{sells}

## Holds

{holds}

## Watchlist

{watchlist}

## Stock Reference (Mapping)

Use this mapping to identify stocks and their tickers:
{stock_reference}

## Instructions

Write a detailed daily briefing in markdown format. Each stock entry above includes analyst scores, a consensus verdict, DCF valuation data, and a "deliberation" field containing the actual analyst reasoning about the stock. Draw heavily from these deliberations — they contain the specific reasoning that drove each decision.

Structure your briefing as follows:

### Opening Summary
2-3 sentences capturing the day's headline: what the strategy did, how the portfolio is performing vs the benchmark, and the overall posture (aggressive, defensive, rotating, steady).

### Portfolio Moves
For each BUY and SELL, write a paragraph explaining:
- **What** we did (bought/sold, how many shares, at what price)
- **Why** — draw from the deliberation text to explain the specific reasoning that drove the decision. Mention the analyst scores and what drove them. Reference the DCF fair value and upside if available.
- **Context** — is this a new position or adding to an existing one? For sells, what changed? Was it score degradation, a failed thesis, or a universe compliance exit?

If there were both buys and sells, frame the rotations: what theme or conviction are we rotating away from, and what are we rotating into?

### Conviction & Holds
For held positions, explain why we're staying the course. What does the analysis show that keeps the thesis intact? Mention any positions where conviction is weakening (WATCH verdicts) vs positions where conviction remains strong.

### On the Radar
If there are watchlist stocks, briefly note 1-2 of the most interesting near-misses — stocks that almost qualified and why they fell short. What would need to change for them to earn a spot?

### Guidelines
- **Stock Linking**: Every time you mention a stock by name or ticker, you MUST use a markdown link to its details page. 
  - Format: `[TICKER](/stock/TICKER)` or `[Company Name](/stock/TICKER)`. 
  - Example: if mentioning Apple, use `[Apple](/stock/AAPL)` or `[AAPL](/stock/AAPL)`.
- Be specific: use ticker symbols, scores, prices, and percentages
- Be honest about uncertainty — if a position is borderline, say so
- Use a professional but conversational tone, as if briefing a sophisticated individual investor
- Do NOT use bullet points in the Opening Summary — write flowing prose
- You may use bullet points sparingly in other sections for clarity
- Skip any section that has no relevant data (e.g., skip "On the Radar" if there are no watchlist stocks)
- Do not fabricate information — only reference data provided above
