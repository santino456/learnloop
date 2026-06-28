# Extracted Figures

::: figure
src: assets/qwen-agentworld-fig-1.png
alt: Figure 1 from qwen-agentworld.pdf
caption: Figure 1: Overview of Qwen-AgentWorld. Top: Qwen-AgentWorld is a unified native language world model across seven domains. Bottom: We explore two complementary strategies for applying world modeling to enhance language agents (mainly using the 35B-A3B model as agent): Decouple and Unify , where the world model serves as the environment simulator and agent foundation model, respectively.
source: 本地 qwen-agentworld.pdf p.1
:::

::: figure
src: assets/qwen-agentworld-fig-2.png
alt: Figure 2 from qwen-agentworld.pdf
caption: Figure 2: Qwen-AgentWorld unifies seven categories of interactive environment simulation within a single language world model.
source: 本地 qwen-agentworld.pdf p.4
:::

::: figure
src: assets/qwen-agentworld-fig-3.png
alt: Figure 3 from qwen-agentworld.pdf
caption: Figure 3: Anatomy of a Terminal domain LWM RL system prompt, showing the five components defined in §2.2. Blue = static (shared across trajectories); red = dynamic (injected per trajectory).
source: 本地 qwen-agentworld.pdf p.5
:::

::: figure
src: assets/qwen-agentworld-fig-4.png
alt: Figure 4 from qwen-agentworld.pdf
caption: Figure 4: Representative interaction examples from a text-based domain (SWE) and a GUI domain (Android), illustrating the breadth of the observation space.
source: 本地 qwen-agentworld.pdf p.6
:::

::: figure
src: assets/qwen-agentworld-table-1.png
alt: Table 1 from qwen-agentworld.pdf
caption: Table 1: The seven domains covered by Qwen-AgentWorld, with their action, observation, and core capability exercised by next-state prediction.
source: 本地 qwen-agentworld.pdf p.7
:::

::: figure
src: assets/qwen-agentworld-fig-5.png
alt: Figure 5 from qwen-agentworld.pdf
caption: Figure 5: Three-stage training pipeline of Qwen-AgentWorld. Stage 1 CPT injects world knowledge; Stage 2 SFT instills next-state-prediction thinking patterns; Stage 3 RL sharpens output quality.
source: 本地 qwen-agentworld.pdf p.7
:::

::: figure
src: assets/qwen-agentworld-table-2.png
alt: Table 2 from qwen-agentworld.pdf
caption: Table 2: SFT and RL training data statistics across all seven domains. Average token counts and turn counts are computed over the RL training pool.
source: 本地 qwen-agentworld.pdf p.8
:::

::: figure
src: assets/qwen-agentworld-table-3.png
alt: Table 3 from qwen-agentworld.pdf
caption: Table 3: Seven turn categories for information-theoretic loss masking. Categories are determined from statistical signals rather than tool names. Keep ratio is the fraction of tokens used in loss computation.
source: 本地 qwen-agentworld.pdf p.10
:::

::: figure
src: assets/qwen-agentworld-table-4.png
alt: Table 4 from qwen-agentworld.pdf
caption: Table 4: Rejection sampling statistics per domain. “Candidates” is the number of queries with complete rollouts. “Retain rate” is the fraction of queries whose best-of-three trajectory exceeds the quality threshold. “Final SFT” is the count after filtering.
source: 本地 qwen-agentworld.pdf p.11
:::

::: figure
src: assets/qwen-agentworld-fig-6.png
alt: Figure 6 from qwen-agentworld.pdf
caption: Figure 6: Overview of AgentWorldBench composition. Left: Domain distribution across seven domains, source benchmarks mapped to each domain, and the five evaluation dimensions (Format, Factuality, Consistency, Realism, Quality). Right: Summary statistics, per-domain average context length and trajectory depth. All ground-truth observations are obtained from real environment execution.
source: 本地 qwen-agentworld.pdf p.13
:::

::: figure
src: assets/qwen-agentworld-fig-7.png
alt: Figure 7 from qwen-agentworld.pdf
caption: Figure 7: Main results on AgentWorldBench: five-dimensional rubric mean per domain. Qwen- AgentWorld-397B-A17B achieves the highest overall average among all evaluated models, with consistent advantages on text-based domains and competitive performance on GUI domains.
source: 本地 qwen-agentworld.pdf p.15
:::

::: figure
src: assets/qwen-agentworld-table-5.png
alt: Table 5 from qwen-agentworld.pdf
caption: Table 5: AgentWorldBench main results: five-dimensional rubric mean (↑) per domain. The highest and second-best scores per domain are shown in bold and underlined, respectively.
source: 本地 qwen-agentworld.pdf p.16
:::

**Extracted table**:

|  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  | +14.2 |  |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |

::: figure
src: assets/qwen-agentworld-fig-8.png
alt: Figure 8 from qwen-agentworld.pdf
caption: Figure 8: Cross-domain generalization when training Stage 3 (RL) on Terminal data alone. (a) Terminal (in-domain) improves by +14.2 points over the SFT baseline. (b) All three held-out domains improve without receiving any domain-specific training signal: MCP (+5.0), SWE (+11.5), and Search (+11.8).
source: 本地 qwen-agentworld.pdf p.16
:::

::: figure
src: assets/qwen-agentworld-table-6.png
alt: Table 6 from qwen-agentworld.pdf
caption: Table 6: Sim RL on simulated OpenClaw environments. Qwen3.5-35B-A3B is trained via Sim RL using different environment simulators. ∆reports gains over the base model.
source: 本地 qwen-agentworld.pdf p.18
:::

::: figure
src: assets/qwen-agentworld-table-7.png
alt: Table 7 from qwen-agentworld.pdf
caption: Table 7: Controllable Sim RL results on Tool Decathlon and MCPMark. “w/ Qwen-AgentWorld-397B- A17B controlled” adds targeted environment control instructions during Sim RL.
source: 本地 qwen-agentworld.pdf p.19
:::

::: figure
src: assets/qwen-agentworld-table-8.png
alt: Table 8 from qwen-agentworld.pdf
caption: Table 8: Controllable Sim RL results on WideSearch, using fictional-world simulation.
source: 本地 qwen-agentworld.pdf p.20
:::

**Extracted table**:

|  |  |  |  | R |  | eal RL |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  | R | eal RL |
|  |  |  |  | S | S | im RL |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |

::: figure
src: assets/qwen-agentworld-fig-9.png
alt: Figure 9 from qwen-agentworld.pdf
caption: Figure 9: Controllable Sim RL vs. Real RL (trained against a live search engine) on WideSearch during the first 60 training steps. Both experiments use Qwen3.5-35B-A3B-SFT as the base model.
source: 本地 qwen-agentworld.pdf p.20
:::

::: figure
src: assets/qwen-agentworld-table-9.png
alt: Table 9 from qwen-agentworld.pdf
caption: Table 9: Agent foundation model: LWM RL warm-up on single-turn, non-agentic trajectories transfers to multi-turn, tool-calling agentic tasks. No additional fine-tuning is applied after LWM RL.
source: 本地 qwen-agentworld.pdf p.21
:::

::: figure
src: assets/qwen-agentworld-fig-10.png
alt: Figure 10 from qwen-agentworld.pdf
caption: Figure 10: Environment prediction accu- racy on Terminal-Bench 2.0 trajectories.
source: 本地 qwen-agentworld.pdf p.22
:::

::: figure
src: assets/qwen-agentworld-fig-11.png
alt: Figure 11 from qwen-agentworld.pdf
caption: Figure 11: Case study of prediction-driven action refinement on the mailman task from Terminal-Bench 2.0.
source: 本地 qwen-agentworld.pdf p.23
:::

::: figure
src: assets/qwen-agentworld-fig-12.png
alt: Figure 12 from qwen-agentworld.pdf
caption: Figure 12: Representative LWM reasoning patterns from Qwen-AgentWorld-397B-A17B’s thinking traces. Left: Multi-step causal reasoning in Terminal, where a chain spans package management, process lifecycle, curl semantics, and Python errors. Center: Information leakage prevention in Search, where the model distinguishes what the agent knows from what the environment should reveal to prevent answer contamination. Right: Epistemic boundary awareness in Terminal, where the model recognizes computational limits and falls back to format-only output rather than fabricating unknowable values.
source: 本地 qwen-agentworld.pdf p.24
:::

::: figure
src: assets/qwen-agentworld-fig-13.png
alt: Figure 13 from qwen-agentworld.pdf
caption: Figure 13: Micro-level fidelity improvements during RL training. Top: Search domain: evolution of a single sample across RL steps. URL identifiers, source diversity, and snippet specificity all improve, despite occupying a tiny fraction of total output tokens. Bottom left: Terminal domain: the model performs exact byte-level arithmetic by enumerating characters including invisible newlines. Bottom right: MCP domain: the model maintains cross-turn schema consistency (user IDs, parent-child references, UUID formats) across nine Notion API calls.
source: 本地 qwen-agentworld.pdf p.25
:::

::: figure
src: assets/qwen-agentworld-fig-14.png
alt: Figure 14 from qwen-agentworld.pdf
caption: Figure 14: Interaction examples from the GUI domains (continued). OS and Web are shown here; Android is in Section 2.3. Given the current screen and the agent’s action, the world model predicts the next GUI state in HTML, which is then rendered as a screenshot.
source: 本地 qwen-agentworld.pdf p.35
:::

::: figure
src: assets/qwen-agentworld-fig-15.png
alt: Figure 15 from qwen-agentworld.pdf
caption: Figure 15: Interaction examples from the text-based domains (continued). Terminal, MCP Tool Use, and Search are shown here; Software Engineering is in Section 2.3.
source: 本地 qwen-agentworld.pdf p.36
:::

::: figure
src: assets/qwen-agentworld-fig-16.png
alt: Figure 16 from qwen-agentworld.pdf
caption: Figure 16: Training dynamics across 440 RL steps (Qwen- AgentWorld-35B-A3B). Format converges within ∼90 steps. Consistency requires ∼250 steps.
source: 本地 qwen-agentworld.pdf p.37
:::

::: figure
src: assets/qwen-agentworld-table-10.png
alt: Table 10 from qwen-agentworld.pdf
caption: Table 10: Rule-based verification: per-domain accuracy (%, ↑) across four text domains (MCP, Search, Terminal, SWE) and three GUI domains (Android, Web, OS). The highest and second-best scores per column are shown in bold and underlined, respectively.
source: 本地 qwen-agentworld.pdf p.38
:::

::: figure
src: assets/qwen-agentworld-table-11.png
alt: Table 11 from qwen-agentworld.pdf
caption: Table 11: Rule-based evaluation on text-based domains: accuracy (%, ↑) on three sub-capabilities. Ctrl: controllability; Err: error handling; LC: long-context consistency. The highest and second-best scores are shown in bold and underlined, respectively.
source: 本地 qwen-agentworld.pdf p.39
:::

::: figure
src: assets/qwen-agentworld-table-12.png
alt: Table 12 from qwen-agentworld.pdf
caption: Table 12: Rule-based evaluation on GUI domains: accuracy (%, ↑) on three sub-capabilities. Ctrl: controllability; Err: error handling; LC: long-context consistency. The highest and second-best scores are shown in bold and underlined, respectively.
source: 本地 qwen-agentworld.pdf p.39
:::

