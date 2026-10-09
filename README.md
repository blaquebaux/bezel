# bezel

**The structured-product fee autopsy — defined-outcome / buffered ETFs.**

A bezel is the frame that holds the stone: you pay for the setting, not the gem. Buffered /
defined-outcome ETFs (Innovator `BUFR`, `DFND`, `BALT`…) sell a downside "buffer" for a cap on upside.
This is BLOCK's "where the fee lives" made tradable — the companion study to
[*Where the Fee Lives*](https://www.blaquebaux.com/block/derivatives-honesty.html): *a modification
never conjures return, it relocates risk onto an axis the buyer isn't watching.* Self-contained; Alpaca
SIP daily; SPY fetched **both** total-return and price-only to expose the forgone-dividend fee.

## Verdict

**CONDITIONAL — the buffer is real, but it is symmetric beta-reduction dressed as asymmetry, and the
fee is findable.** You give up dividends and upside to cushion drawdowns you could cushion nearly as
well with SPY + cash, for a fraction of the cost. A defined *outcome*, honestly — just not a free one.

| fund | Sharpe | CAGR | maxDD | up-capture | down-capture | give-up vs SPY |
|---|---|---|---|---|---|---|
| **BUFR** | +0.88 | +9.3% | −14% | **59%** | **57%** | **−3.1%/yr** |
| DFND | +0.30 | +4.3% | −23% | 41% | 39% | −8.1%/yr |
| BALT | +1.70 | +5.9% | −5% | 17% | 13% | −6.5%/yr |
| SPY | +0.76 | +12.4% | −24% | 100% | 100% | — |
| 70% SPY / 30% cash | +0.84 | +10.0% | −17% | ~70% | ~70% | ~0 |

*Window 2021-07 … 2025-12 (4.4y — the buffered ETFs' available history; includes the 2022 bear).*

## Where the fee lives (the autopsy)

Three charges, none of them on the fact sheet's headline:

1. **Forgone dividends — 1.5%/yr.** Buffered ETFs reset on the *price* return of the index, so you
   silently forgo SPY's dividend. SPY total +12.4%/yr vs SPY price-only +10.9%/yr — that 1.5% is gone
   before any cap or fee.
2. **The cap — paid as symmetric capture.** `BUFR`'s up-capture (59%) ≈ its down-capture (57%). The
   "buffer" did not deliver asymmetry; it delivered **~58% equity beta**. Buffer value (100 − down-capture)
   almost exactly equals its cost (100 − up-capture). You dialed down beta and called it protection.
3. **The expense** — on top, ~0.7%/yr.

Total for `BUFR`: **−3.1%/yr vs SPY** (1.5% dividends + 1.6% cap/expense). For the deeper-buffer funds
it's far worse (`DFND` −8.1%, `BALT` −6.5%).

## Replicate it for near-free

A plain **70% SPY / 30% cash** nearly matches `BUFR`'s risk profile — Sharpe +0.84 vs +0.88, maxDD −17%
vs −14%, at ~0 extra cost vs 3.1%/yr. The structure buys you a slightly cleaner drawdown and a *defined*
number, but most of what you pay for is reduced equity beta you can rent for the price of holding cash.
The honest exception is a mandate that genuinely values the *certainty* of the stated outcome over the
cost — for everyone else, the setting costs more than the stone.

## Why symmetric, and `bezel_2`

The symmetric-capture finding is partly the **window**: 2021–2025 had a grind-down 2022, not a single
catastrophic month, so the buffer's cap on losses never had a severe event to shine against (annual-reset
buffers protect the first ~9–15%, then you eat the rest). The structure's asymmetry only really shows in
a sharp crash — which this window didn't deliver and `BUFR`'s mid-2020 inception missed. **`bezel_2`** =
the exact synthetic decomposed from the options chain (deep-ITM call + the put spread that finances the
buffer) via Massive/OPRA, for a period-exact fee attribution, plus a severe-crash test.

## Reproduce

```bash
export ALPACA_KEY_ID=... ALPACA_SECRET_KEY=...
python3 research/bezel_1.py
```

---

*Blaque Baux — a Carter Warrens research initiative. Research only; not investment advice. The verdict
falls where the data puts it — and the fee lives where the brochure doesn't look.*
