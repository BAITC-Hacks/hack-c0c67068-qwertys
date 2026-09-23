# Roadmap (after the hackathon / only if everything else is done)

From ballots + the 186-idea pool (CLAUDE-pool = simulated, 1 voice). Nothing here is implemented or promised.

- Uncertainty: quantile/conformal P10–P90 with measured coverage (S-03, TS-A07, ML-04); analog ensemble (NWP-12); pseudo-ensemble spread from day1/day2 runs (TS-A11).
- Weather: multi-NWP blend once per-source Feb availability is proven (S-04, NWP-07); valley speed-up factor by direction sector (NWP-11); regime-conditioned power curve (NWP-06); shear-based hub extrapolation (NWP-03).
- Data quality: MAD power-curve outlier filter (DQ-01), curtailment/fault mask (DQ-03), icing regime (DQ-04), unsupervised regime labeler (DQ-11), power-curve drift audit (DQ-08).
- Models: two-stage MOS→power (ML-01), residual over physics curve (ML-02), joint two-turbine model (ML-12), Chronos-2 / TiRex-2 covariate TSFM (CMP-01, CMP-10).
- Operator product: alerts (S-07: cut-out, ramps, icing with RH), nomination sheet (OP-01) and MWh only after rated power is known (R07), newsvendor quantile choice with the operator's penalty asymmetry (OP-11), maintenance window recommender (OP-07), LLM shift-handover note with numeric guardrail (OP-12, AG-08).
- Agentic: provider abstraction OpenAI / NVIDIA NIM / Ollama with failover (LLM-01, LLM-11), human-in-the-loop review state (AG-09), multi-agent roles (AG-07), NIM fleet across farms (CMP-11).
- Business: IPP / wind-farm operator as first customer, KEGOC as consumer of aggregated bands, other Kazakh corridors (Zhanatas, Ereymentau) by per-site retraining, portfolio balancing (BIZ-02/03/09/11). No savings numbers without measured data.

Missing evidence: publication time of ECMWF runs (R03), day1/day2 semantics (R04), SCADA timezone metadata (R02), rated power / normalization (R07).
