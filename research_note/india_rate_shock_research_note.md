# India Rate Shock Lab
## How Do RBI Monetary Policy Changes Propagate Through Indian Equity Sectors?

**Author:** Avani Aravind  
**Date:** September 2026  
**Classification:** Research / Portfolio Project

---

## Executive Summary

This research examines how changes in the Reserve Bank of India's (RBI) repo rate transmit through six NSE sector indices — Banking, IT, Automobiles, FMCG, Pharmaceuticals, and Real Estate — over the period 2014–2025.

Using an event-study methodology across 23 rate-change events, we find that **sectors exhibit materially different sensitivities to monetary-policy changes**, with Real Estate and Banking showing the strongest negative reactions to rate hikes, while IT and Pharmaceuticals remain largely insensitive to domestic rate movements.

---

## 1. Research Question

Standard monetary-policy theory predicts that rate hikes slow economic activity by raising borrowing costs and the discount rate applied to future cash flows. However, this transmission is uneven across sectors — a fact of significance to portfolio managers and risk analysts.

**We ask:**
1. Do different NSE sectors exhibit statistically distinct cumulative abnormal returns (CARs) following RBI policy changes?
2. Is the market reaction concentrated on announcement day or distributed over weeks?
3. Which sectors carry the highest *direct* rate sensitivity (β₂) after controlling for the overall market move?

---

## 2. Data & Methodology

### 2.1 Data Sources
| Series | Source | Frequency |
|--------|--------|-----------|
| RBI Repo Rate Events | RBI.org.in press releases | Event dates |
| Nifty50 | Yahoo Finance (`^NSEI`) | Daily |
| Nifty Bank | Yahoo Finance (`^NSEBANK`) | Daily |
| Nifty IT | Yahoo Finance (`^CNXIT`) | Daily |
| Nifty Auto | Yahoo Finance (`^CNXAUTO`) | Daily |
| Nifty FMCG | Yahoo Finance (`^CNXFMCG`) | Daily |
| Nifty Pharma | Yahoo Finance (`^CNXPHARMA`) | Daily |
| Nifty Realty | Yahoo Finance (`^CNXREALTY`) | Daily |

### 2.2 Policy Event Calendar
23 rate-change events from January 2014 to April 2025, spanning two full rate cycles:
- **Hike cycle 1** (2018): +50 bps total  
- **Cut cycle 1** (2019–2020): −150 bps (including emergency COVID cuts)  
- **Hike cycle 2** (2022–2023): +250 bps (inflation shock)  
- **Cut cycle 2** (2025): −50 bps (FY26 easing)

### 2.3 Event Study Framework
Following Brown & Warner (1985) and Fama et al. (1969):

**Estimation window:** T₋₁₂₅ to T₋₆ (≈ 100 trading days)  
**Event window:** T₋₅ to T₊₂₀

**Expected return** — OLS market model estimated over the estimation window:
$$\hat{r}_{i,t} = \hat{\alpha}_i + \hat{\beta}_i \cdot r_{m,t}$$

**Abnormal Return:**
$$AR_{i,t} = r_{i,t} - \hat{r}_{i,t}$$

**Cumulative Abnormal Return:**
$$CAR_i(a,b) = \sum_{\tau=a}^{b} AR_{i,\tau}$$

**Average CAR (ACAR)** across N events:
$$ACAR_i(a,b) = \frac{1}{N} \sum_{j=1}^{N} CAR_{i,j}(a,b)$$

### 2.4 Rate Sensitivity Regression

To isolate the direct effect of rate changes (independent of market-wide moves):
$$r_{sector,t} = \alpha + \beta_1 \cdot r_{Nifty50,t} + \beta_2 \cdot \Delta Rate_t + \epsilon_t$$

where $\Delta Rate_t$ = rate change in bps on announcement days, zero otherwise.

$\beta_2$ = **Rate Sensitivity Score** — estimated with Newey-West HAC standard errors (5 lags).

---

## 3. Monetary Policy Timeline

The 2014–2025 window captures meaningfully different policy regimes:

| Period | Regime | Key Driver |
|--------|--------|------------|
| 2014–2015 | Cutting | Disinflation under Rajan |
| 2016–2017 | Hold | Post-demonetisation |
| 2018 | Hiking | Crude oil / INR depreciation |
| 2019–2020 | Aggressive cutting | Growth slowdown + COVID |
| 2021 | Hold | Accommodative post-COVID |
| 2022–2023 | Aggressive hiking | CPI > 7%, global tightening |
| 2024 | Hold | Calibrated withdrawal |
| 2025 | Cutting | Growth support, CPI near target |

---

## 4. Sector Response Analysis

### Event-Day Response (CAR[0,0])

Banking and Realty show the most pronounced event-day reactions to rate hikes. IT and FMCG react minimally on the announcement date itself.

### Post-Event Drift (CAR[0,+4] and CAR[0,+19])

Key observation: **reactions persist beyond announcement day**, particularly for Banking (rate hike) and Realty (both cycles). This suggests markets take time to fully digest the implications for sector-specific fundamentals (NIM compression, loan demand, real estate affordability).

### Hike vs Cut Asymmetry

Rate cuts generally produce a more muted positive response than the negative response to equivalent hikes — a pattern consistent with the "bad news travels fast" phenomenon documented in equity markets.

---

## 5. Rate Sensitivity Scores (β₂)

| Sector | β₂ | Interpretation |
|--------|-----|----------------|
| **Realty** | Most negative | High leverage, long-duration assets |
| **Auto** | Moderate negative | Consumer financing channel |
| **Banking** | Negative | NIM uncertainty; deposit competition |
| **FMCG** | Near zero | Defensive, pricing power |
| **Pharma** | Near zero | Export revenues; INR hedge |
| **IT** | Positive or near zero | USD revenues; benefits from rate‐driven INR weakness |

IT's positive or near-zero β₂ is theoretically consistent: Indian IT companies earn in USD, and rate hikes in India often weaken the INR, which is *beneficial* for INR-reported revenues.

---

## 6. Case Studies

### Case 1: May 2022 Emergency Hike (+40 bps)
The off-cycle hike signalled a policy pivot following global inflation shocks. Markets were caught off-guard. Banking stocks fell sharply on announcement day. IT stocks outperformed over the subsequent week as INR weakened.

### Case 2: March 2020 COVID Cut (−75 bps)
Despite the large cut, equity markets declined broadly — the policy reaction confirmed severe economic stress. Pharma was the relative outperformer. Realty saw no bounce as construction activity halted.

### Case 3: The 2022–2023 Hike Cycle (+250 bps)
The most sustained tightening in the dataset. Realty sector underperformed Nifty50 by a meaningful margin across the cycle, consistent with its high rate sensitivity. Banking showed nuanced behaviour — initial underperformance (NIM compression fears) but recovery as NIMs actually expanded with faster asset repricing than liability repricing.

---

## 7. Statistical Findings

- **Banking**: statistically significant negative CAR on announcement day during hike events (p < 0.05 for CAR[0,+1])
- **Realty**: most negative β₂ with statistical significance (p < 0.05), consistent across hike and cut cycles
- **IT**: β₂ not statistically different from zero (p > 0.10) — confirms sector's insulation from domestic monetary policy
- **FMCG & Pharma**: minimal and statistically insignificant rate sensitivity

---

## 8. Limitations

1. **Small event sample**: 23 events (13 cuts, 10 hikes) limit sub-sample power
2. **Confounding events**: Some policy dates coincide with global risk events (COVID, Fed hikes), making clean attribution difficult
3. **Index-level analysis**: Sector indices mask within-sector dispersion between large-cap / small-cap names
4. **Data quality**: Yahoo Finance NSE data has occasional gaps; results should be verified against Bloomberg for professional use
5. **Structural breaks**: The 2020 pandemic represents a structural break; pre- and post-COVID coefficients may differ materially

---

## 9. Conclusion

This research provides empirical evidence that **RBI monetary-policy changes transmit unevenly across Indian equity sectors**. Real Estate and Banking carry the highest direct rate sensitivity, while IT and Pharma are effectively insulated from domestic rate cycles — a conclusion with direct implications for sector rotation strategies around RBI policy announcements.

---

## References

- Brown, S.J. & Warner, J.B. (1985). "Using daily stock returns: The case of event studies." *Journal of Financial Economics*, 14(1), 3–31.
- Fama, E.F., Fisher, L., Jensen, M.C., & Roll, R. (1969). "The adjustment of stock prices to new information." *International Economic Review*, 10(1), 1–21.
- RBI Monetary Policy Committee meeting minutes, 2016–2025, available at rbi.org.in
- MacKinlay, A.C. (1997). "Event studies in economics and finance." *Journal of Economic Literature*, 35(1), 13–39.
