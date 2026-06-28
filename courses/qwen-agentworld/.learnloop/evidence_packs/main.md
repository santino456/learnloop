# Evidence Pack: Qwen-AgentWorld

## Verified Facts (High Confidence)

### Model and Training
- Qwen-AgentWorld is released in two sizes: **35B-A3B** and **397B-A17B** (active parameter counts are 3B and 17B respectively).
- Training uses a **three-stage pipeline**: Continual Pre-Training (CPT) -> Supervised Fine-Tuning (SFT) -> Reinforcement Learning (RL).
- CPT injects world knowledge from **10M+ environment interaction trajectories** across 7 domains, plus specialized-domain corpora (industrial control, cybersecurity, law, medicine, finance, current affairs).
- SFT uses **7,094 trajectories** (69.2% retention from 10,250 candidates after rejection sampling).
- RL uses **GSPO** (Group Sequence Policy Optimization) with a hybrid reward combining a five-dimensional LLM judge rubric and rule-based verifiers at a **9:1 ratio**.
- The unified schema has **five components**: task description, action space, initial state, demonstrations, simulation instruction.

### Domains Covered
The model covers **seven domains** with the following action/observation representations (Table 1, p.7):
1. **MCP**: JSON tool calls -> tool responses
2. **Search**: Web search/extractor -> conversation history
3. **Terminal**: Bash commands/keystrokes -> terminal output
4. **SWE**: Read/edit/bash tools -> file content + diffs
5. **Android**: Touch/swipe/type -> UI view hierarchy + app state
6. **Web**: Click/type/navigate -> accessibility tree + browser state
7. **OS**: Mouse/keyboard -> accessibility tree + window/app state

### Benchmark (AgentWorldBench)
- **2,170 turn-level evaluation samples** across 7 domains.
- Built from **5 frontier models** on **9 established benchmarks** (e.g., Terminal-Bench 1.0/2.0, OSWorld-Verified, Tool Decathlon, MCPMark, WideSearch).
- Evaluated on **5 dimensions**: Format, Factuality, Consistency, Realism, Quality (each 1-5, normalized to 0-100).
- **Reference-grounded judging**: judge compares predicted vs. real environment observation.
- **Differentiated matching criteria**: deterministic content (exact match), pre-existing content (format/plausibility), runtime metadata (format/range only).

### Main Results (AgentWorldBench)
- **Qwen-AgentWorld-397B-A17B** achieves highest overall average: **58.71** (vs. GPT-5.4 at 58.25, Claude Opus 4.6 at 57.80).
- On **text-based domains**, Qwen-AgentWorld leads with 58.07 average (vs. GPT-5.4 at 56.84).
- On **GUI domains**, Claude Opus 4.8 leads (60.93), with Qwen-AgentWorld ranking fifth (59.69); the gap is attributed to multimodal pre-training advantages.
- **Search is the weakest domain for all models**: best score 37.82 (Qwen-AgentWorld-397B-A17B) vs. 68.49 on SWE.
- World-model training improves Qwen3.5-35B-A3B from 47.73 to 56.39 (+8.66 points); at 397B scale from 54.74 to 58.71 (+3.97 points).

### Cross-Domain Generalization
- Training RL on **Terminal data alone** improves Terminal by +14.2 points and transfers to held-out domains: MCP (+5.0), SWE (+11.5), Search (+11.8) (Figure 8, p.16).
- This suggests RL reinforces **generalizable world knowledge** rather than domain-specific formats.

### Application I: Environment Simulator
- **Zero-shot scaling**: Simulated 4k OpenClaw environments, yielding Claw-Eval +4.3 and QwenClawBench +7.1 (Table 6, p.18).
- **Controllable simulation** on MCP: Tool Decathlon +3.7, MCPMark +12.3 (Table 7, p.19).
- **Fictional-world simulation** on Search: WideSearch F1 by Item +16.29 (35B) and +3.87 (397B) (Table 8, p.20).
- **Sim RL vs. Real RL on WideSearch**: Sim RL reaches 50.3% F1 by Item vs. Real RL 45.6% (Figure 9, p.20).
- Sim RL increases web_extractor calls (2.5 -> 4.0) while Real RL decreases them (2.5 -> 1.5), showing controllable simulation shapes agent behavior.

### Application II: Agent Foundation Model
- LWM RL warm-up on **single-turn, non-agentic trajectories** transfers to **multi-turn, tool-calling agentic tasks** without additional fine-tuning (Table 9, p.21).
- In-domain gains: Terminal-Bench 2.0 (+6.30), SWE-Bench Verified (+3.39), SWE-Bench Pro (+5.24), WideSearch F1 Item (+12.79), F1 Row (+6.87).
- Out-of-domain gains: Claw-Eval (+11.3), QwenClawBench (+9.7), BFCL v4 (+9.0).
- **Prediction accuracy** improves from 69.9% to 78.3% (+8.4%) after LWM RL (Figure 10, p.22).

### Reasoning Patterns (Analysis)
- Across 129 thinking traces, **1,347 "Wait!" self-correction interrupts** (10.4 per turn average; peak 56 in one SWE turn).
- Three reasoning subtypes: factual, epistemological, perspective-taking.
- **Information leakage prevention** in Search: model distinguishes what agent knows from what environment should reveal.
- **Epistemic boundary awareness**: model recognizes computational limits (e.g., cannot know np.random.randn(500) values beyond seed-known indices) and falls back to format-only output.

## Uncertain Claims / Interpretations

### Attributed to Multimodal Pre-Training
- The paper states that GUI domain gaps "reflect an advantage from multimodal pre-training that text-only world modeling does not fully capture." This is a **plausible interpretation** but not experimentally isolated (no ablation removing multimodal pre-training was reported).

### Necessity of World Models
- The claim that world models are **necessary** for general agents (citing Richens et al., 2025) is a theoretical result from a separate paper. Qwen-AgentWorld provides empirical support but does not independently prove necessity.

### "CPT Injects, SFT Activates, RL Sharpens"
- This framing is a useful pedagogical principle but the boundaries between stages are somewhat fluid. CPT already uses trajectory-format data; SFT also uses next-token prediction; RL improves upon SFT but does not exclusively "sharpen".

### Fictional-World Generalization
- The claim that fictional-world Sim RL "generalizes effectively to real-world search tasks" is supported by WideSearch results, but the mechanism (why invented facts transfer to real facts) is not deeply analyzed. It may rely on structural skill transfer (query reformulation, extraction) rather than factual knowledge transfer.

### Concurrent Work Validation
- The paper cites Shrivastava et al. (2026) as "independent validation" that auxiliary world-modeling loss doubles Terminal-Bench 2.0 performance. This is supportive but not a controlled replication of Qwen-AgentWorld's specific approach.

## Useful Diagrams and Tables

### Must-Include Figures
| Figure/Table | Location | Purpose |
|--------------|----------|---------|
| Figure 1 | p.1 | Overview of Qwen-AgentWorld and the two paradigms (Decouple/Unify) |
| Figure 2 | p.4 | Seven unified domains |
| Figure 3 | p.5 | Terminal system prompt anatomy (static vs. dynamic) |
| Figure 4 | p.6 | SWE and Android interaction examples |
| Figure 5 | p.7 | Three-stage training pipeline |
| Figure 6 | p.13 | AgentWorldBench composition |
| Figure 7 | p.15 | Main results bar chart |
| Figure 8 | p.16 | Cross-domain generalization |
| Figure 9 | p.20 | Sim RL vs. Real RL curves |
| Figure 10 | p.22 | Prediction accuracy improvement |
| Figure 11 | p.23 | Mailman case study |
| Figure 12 | p.24 | LWM reasoning patterns |
| Figure 13 | p.25 | Micro-level fidelity improvements |
| Table 1 | p.7 | Seven domains with capabilities |
| Table 2 | p.8 | SFT/RL data statistics |
| Table 3 | p.10 | Information-theoretic loss masking categories |
| Table 4 | p.11 | Rejection sampling statistics |
| Table 5 | p.16 | Main rubric results |
| Table 6 | p.18 | Sim RL on OpenClaw |
| Table 7 | p.19 | Controllable Sim RL on MCP |
| Table 8 | p.20 | Fictional-world Sim RL on Search |
| Table 9 | p.21 | Agent foundation model results |

### Training Dynamics Figure
- Figure 16 (p.37): Shows Format converges within ~90 RL steps, Consistency requires ~250 steps. Useful for understanding RL stability.

## What Should NOT Be Claimed

1. **Do NOT claim Qwen-AgentWorld is the "best" world model in all domains.** It leads on text-based domains but trails Claude Opus and GPT-5.4 on GUI domains.

2. **Do NOT claim the 397B model is universally better than the 35B model for all use cases.** The 35B model shows larger relative gains from world-model training (+8.66 vs. +3.97), suggesting efficiency trade-offs.

3. **Do NOT claim that fictional-world simulation replaces real-world data.** It is a complementary axis for training specific capabilities (query reformulation, extraction), not a substitute for factual grounding.

4. **Do NOT claim that LWM warm-up eliminates the need for downstream agent fine-tuning.** The paper evaluates without additional fine-tuning for isolation, but practical deployment would likely combine warm-up with task-specific training.

5. **Do NOT claim that the information-theoretic loss masking is the optimal approach.** It is one effective method; the paper does not compare against alternatives like learned importance weighting.

6. **Do NOT claim that AgentWorldBench is the only valid way to evaluate world models.** It is a comprehensive benchmark but focuses on rubric-based judging; rule-based verification (Appendix C) provides complementary signals.

7. **Do NOT claim that the "Wait!" self-correction pattern is unique to Qwen-AgentWorld.** The paper analyzes it as an emergent property but does not compare against other reasoning models.

8. **Do NOT invent release dates, commercial availability, or pricing.** The paper is a technical blog/research report; no commercial timeline is provided.

9. **Do NOT claim that Qwen-AgentWorld achieves human-level simulation fidelity.** The best overall score is 58.71/100, indicating substantial room for improvement, especially on Factuality (lowest-scoring dimension).

10. **Do NOT conflate the theoretical result (Richens et al., 2025) with the empirical contribution of this paper.** The paper builds on the theoretical claim but its contribution is engineering and empirical validation.
