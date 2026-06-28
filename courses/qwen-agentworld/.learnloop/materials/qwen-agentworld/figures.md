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

**Extracted table**:

| Domain | Action |  |  | Observation | Core Capabi |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |
| MCP | JSON T | ool Call |  | Tool response (file content, DB, etc.) | Factual world |
| Search | Web Se | arch / | Web Extractor | Conversation history (query + results) | Factual world |
| SWE | Read / | Edit / B | ash / ... | Tool output (flie content + diffs) | Code executi |
| Terminal | Bash C | omman | ds / Keystrokes | Terminal output (stdout + shell prompt) | Long-context |
| Android | Touch | / Swipe | / Type / ... | UI view hierarchy + app state | Visual state r |
| Web | Click / | Type / | Navigate / ... | Accessibility tree + browser state | Visual state r |
| OS | Mouse | / Keyb | oard | Accessibility tree + window/app state | Visual state r |

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

**Extracted table**:

| Domain | SFT RL | Train Avg. | tokens Avg. | turns |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |
| MCP | 179 | 4,156 | 62,702 | 28.9 |
| Search | 1,042 | 20,004 | 18,873 | 6.2 |
| Terminal | 1,580 | 34,125 | 5,805 | 12.0 |
| SWE | 249 | 8,181 | 36,734 | 24.7 |
| Android | 1,337 | 11,498 | 30,064 | 19.3 |
| Web | 1,605 | 8,716 | 19,417 | 10.2 |
| OS | 1,102 | 5,628 | 25,439 | 12.4 |
|  |  |  |  |  |
| Total | 7,094 | 92,308 | 19,443 | 13.4 |

::: figure
src: assets/qwen-agentworld-table-3.png
alt: Table 3 from qwen-agentworld.pdf
caption: Table 3: Seven turn categories for information-theoretic loss masking. Categories are determined from statistical signals rather than tool names. Keep ratio is the fraction of tokens used in loss computation.
source: 本地 qwen-agentworld.pdf p.10
:::

**Extracted table**:

| Category | Statistical sign | atur | e | Intuition | Keep |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |
| retrieval | Nov ≥60%, R | > 1 |  | read_file →contents | 100% |
| expansion | OL ≥50%, No | v ≥ | 50%, R > 1.5 | fetch →page + metadata | 100% |
| action | Nov ≥50%, R | ≤1 | or short | send_email →“sent” | 100% |
| transform | Nov < 50%, R | < 1 |  | long input →status word | 50% |
| boilerplate | OL ≥50%, No | v < | 50% | API echo | 10% |
| echo | OL ≥70%, No | v < | 30% | think(x) →{thought:x} | 5% |
| other | uncategorized |  |  | — | 100% |

::: figure
src: assets/qwen-agentworld-table-4.png
alt: Table 4 from qwen-agentworld.pdf
caption: Table 4: Rejection sampling statistics per domain. “Candidates” is the number of queries with complete rollouts. “Retain rate” is the fraction of queries whose best-of-three trajectory exceeds the quality threshold. “Final SFT” is the count after filtering.
source: 本地 qwen-agentworld.pdf p.11
:::

**Extracted table**:

| Domain | Candidates Retai | n rate Final | SFT Avg. | turns |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |
| MCP | 261 | 68.6% | 179 | 24.3 |
| Search | 1,466 | 71.1% | 1,042 | 3.3 |
| Terminal | 1,826 | 86.5% | 1,580 | 5.9 |
| SWE | 402 | 61.9% | 249 | 26.9 |
| Android | 1,975 | 67.7% | 1,337 | 15.9 |
| Web | 2,697 | 59.5% | 1,605 | 3.0 |
| OS | 1,623 | 67.9% | 1,102 | 5.4 |
|  |  |  |  |  |
| Total | 10,250 | 69.2% | 7,094 | 8.5 |

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

|  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | Model |  |  |  |  |  |  |  | Avg. |
|  |  | MCP | Search | Term. | SWE | Android | Web | OS |  |
|  |  |  |  |  |  |  |  |  |  |
|  | Claude Opus 4.8 | 54.93 | 35.14 | 59.18 | 64.10 | 61.50 | 54.66 | 66.62 | 56.59 |
| ier | Claude Opus 4.6 | 69.90 | 29.30 | 57.51 | 64.55 | 61.74 | 51.42 | 70.20 | 57.80 |
| ront | Claude Sonnet 4.6 | 70.00 | 28.79 | 56.98 | 64.52 | 58.03 | 50.78 | 63.17 | 56.04 |
| F | GPT-5.4 | 70.10 | 37.26 | 53.69 | 66.29 | 60.00 | 51.80 | 68.58 | 58.25 |
|  |  |  |  |  |  |  |  |  |  |
|  | Gemini 3.1 Pro | 59.07 | 30.21 | 52.47 | 59.07 | 61.40 | 52.83 | 66.92 | 54.57 |
|  |  |  |  |  |  |  |  |  |  |
| ight | DeepSeek-V4-Pro | 63.27 | 27.61 | 51.26 | 59.44 | 55.17 | 50.32 | 63.70 | 52.97 |
| we | Kimi K2.6 | 65.23 | 27.48 | 52.54 | 58.77 | 58.93 | 50.20 | 60.80 | 53.42 |
| pen- | GLM-5.1 | 67.60 | 22.46 | 47.32 | 52.07 | 59.10 | 51.50 | 59.13 | 51.31 |
| O | MiniMax-M2.7 | 55.82 | 27.30 | 41.62 | 37.44 | 52.40 | 50.52 | 57.73 | 46.12 |
|  |  |  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |  |  |
| n | Qwen3.6-35B-A3B | 42.96 | 18.78 | 43.81 | 40.71 | 51.88 | 46.53 | 55.48 | 42.88 |
| Qwe | Qwen3.6-Plus | 55.28 | 21.94 | 50.58 | 59.08 | 57.65 | 50.78 | 60.33 | 50.81 |
|  | Qwen3.6-Max-Preview | 67.01 | 24.71 | 50.86 | 57.11 | 57.74 | 48.58 | 60.95 | 52.42 |
|  |  |  |  |  |  |  |  |  |  |
|  | Qwen3.5-35B-A3B | 57.87 | 25.98 | 46.13 | 47.58 | 53.18 | 47.10 | 56.27 | 47.73 |
| Ours | Qwen-AgentWorld-35B-A3B | 64.79 | 36.69 | 53.96 | 65.63 | 58.17 | 49.55 | 65.92 | 56.39 |
|  | Qwen3.5-397B-A17B | 68.31 | 30.81 | 55.30 | 64.44 | 54.90 | 48.55 | 60.85 | 54.74 |
|  | Qwen-AgentWorld-397B-A17B | 68.24 | 37.82 | 57.73 | 68.49 | 60.20 | 50.98 | 67.89 | 58.71 |

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

**Extracted table**:

| el | Claw-Eval | QwenClawBench |
| --- | --- | --- |
|  |  |  |
| n3.5-35B-A3B | 65.4 | 47.9 |
| Sim RL (w/ Qwen3.6-Plus) | 66.7 | 47.8 |
| Sim RL (w/ Qwen-AgentWorld-397B-A17B) | 69.7 | 55.0 |
|  |  |  |
| ∆ | +4.3 | +7.1 |

::: figure
src: assets/qwen-agentworld-table-7.png
alt: Table 7 from qwen-agentworld.pdf
caption: Table 7: Controllable Sim RL results on Tool Decathlon and MCPMark. “w/ Qwen-AgentWorld-397B- A17B controlled” adds targeted environment control instructions during Sim RL.
source: 本地 qwen-agentworld.pdf p.19
:::

**Extracted table**:

|  | Tool |  |  |  | MCPMar | k |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| odel | Decathlon | Filesys. | GitHub | Postgres | Notion | Playwright | WebArena | Avg. |
|  |  |  |  |  |  |  |  |  |
| wen3.5-35B-A3B-SFT | 32.4 | 16.7 | 17.4 | 28.6 | 25.0 | 0.0 | 33.3 | 21.5 |
| Sim RL (w/ Qwen-AgentWorld-397B-A17B) | 31.5 | 16.7 | 17.4 | 42.9 | 32.1 | 0.0 | 28.6 | 24.6 |
| Sim RL (w/ Qwen-AgentWorld-397B-A17B controlled) | 36.1 | 30.0 | 17.4 | 47.6 | 42.9 | 0.0 | 38.1 | 33.8 |
|  |  |  |  |  |  |  |  |  |
| ∆ | +3.7 | +13.3 | +0.0 | +19.0 | +17.9 | +0.0 | +4.8 | +12.3 |

::: figure
src: assets/qwen-agentworld-table-8.png
alt: Table 8 from qwen-agentworld.pdf
caption: Table 8: Controllable Sim RL results on WideSearch, using fictional-world simulation.
source: 本地 qwen-agentworld.pdf p.20
:::

**Extracted table**:

| n3.5-35B-A3B-SFT | 34.02 | 13.72 |
| --- | --- | --- |
| Sim RL (w/ Qwen-AgentWorld controlled) | 50.31 | 24.21 |
|  |  |  |
| ∆ | +16.29 | +10.49 |
|  |  |  |
| n3.5-397B-A17B-SFT | 70.11 | 45.69 |
| Sim RL (w/ Qwen-AgentWorld controlled) | 73.98 | 51.74 |
|  |  |  |
| ∆ | +3.87 | +6.05 |

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

**Extracted table**:

| 6.2 Applicatio | n II: Agent Foun | dation Mode | l |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |
| Takeaways |  |  |  |  |  |  |
|  |  |  |  |  |  |  |
| LWM trainin | g unifies the world | model and t | he agent, instil | ling next-state pred | iction as an | internalized |
| reasoning cap | ability: |  |  |  |  |  |
| • Radical cro | ss-task generalizat | ion. Single-tur | n, non-agentic | LWM RL warm-up w | ith no tool c | alls transfers |
| to multi-tu | rn, tool-calling age | ntic tasks acros | s seven bench | marks of five domain | s. |  |
|  |  |  |  |  |  |  |
| • Domain g | eneralization. Gain | s emerge on t | wo completely | out-of-distribution | domains en | tirely absent |
| from LWM | training (+11.3 on | Claw-Eval, + | 9.7 on QwenCl | awBench, and +9.0 | on BFCL v4) | , confirming |
| transferabl | e capabilities rather | than domain- | specific shortc | uts. |  |  |
|  |  |  |  |  |  |  |
| • Next-state | prediction as meta | -reasoning pa | ttern. LWM tr | aining teaches the ag | ent to ment | ally simulate |
| environme | nt responses before | acting, which | generalizes ac | ross task formats an | d domains. |  |
|  |  |  |  |  |  |  |
| In Application I | the agent and w | orld model a | re separate m | odels. Here we un | ify them: t | he same model |
| that selects actio | ns (agent) also pr | edicts enviro | nment states ( | world model). The | underlyin | g mechanism is |
| that LWM traini | ng enables the ag | ent to menta | lly simulate t | he consequences o | f a candidat | e action before |
| committing, eff | ectively using wo | rld modeling | as an interna | l planning step th | at improve | s action quality. |
| This aligns with | the unified world | -model–acto | r architecture | envisioned by LeC | un et al. (20 | 22) and echoes |
| the World Actio | n Model paradig | m emerging | in vision-lan | guage-action resea | rch (Ye et a | l., 2026b). |
|  |  |  |  |  |  |  |
| LWM RL warm- | up familiarizes th | e agent with | how environ | ment states evolve | in response | to user actions: |
| how different t | ool calls and sear | ch queries y | ield differen | t responses, which | tools are | more effective, |
| and how state t | ransitions propa | gate across tu | rns. This am | ounts to learning | next-state | prediction as a |
| meta-reasoning | pattern, in which | the agent int | ernally simu | lates what will hap | pen before | deciding what |
| to do. We valid | ate this effect by | running LW | M RL on Qwe | n3.5-35B-A3B-SFT | , which is | fundamentally |
| a single-turn t | ask that involves | reasoning | with no tool | calls or multi-tur | n interacti | on (predicting |
| the next enviro | nment state given | a user actio | n). After war | m-up, we evaluat | e the same | model directly |
| on multi-turn, t | ool-calling agent | ic tasks acro | ss seven ben | chmarks without a | ny additio | nal fine-tuning, |
| including three | out-of-domain be | nchmarks ab | sent from LW | M training. All be | nchmarks u | se a maximum |
| sequence lengt | h of 256k tokens. | Claw-Eval, | QwenClawB | ench, SWE-Bench | Verified, a | nd SWE-Bench |
| Pro scores are a | veraged over 3 i | ndependent | rollouts; Ter | minal-Bench 2.0 sc | ores are a | veraged over 5 |
| runs; BFCL v4 | uses a single roll | out. SWE-Be | nch Verified | and SWE-Bench P | ro are eva | luated with an |
| internal agent s | caffold (bash and | file-edit tools | ); we correct | several problemati | c tasks in t | he public set of |
| SWE-Bench Pro | and evaluate all | baselines on | the refined b | enchmark. Termi | nal-Bench 2 | .0 is evaluated |
| under the Term | inus-2 harness wi | th a 3-hour ti | meout and 8 | CPU / 32 GB RAM | . |  |

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

**Extracted table**:

|  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | Model |  |  |  |  |  |  |  | Avg. |
|  |  | MCP | Search | Term. | SWE | Android | Web | OS |  |
|  |  |  |  |  |  |  |  |  |  |
| r | Claude Opus 4.6 | 76.90 | 77.55 | 68.60 | 54.40 | 80.06 | 75.71 | 61.81 | 70.72 |
| ntie | Claude Sonnet 4.6 | 76.43 | 71.90 | 64.43 | 55.27 | 75.23 | 77.16 | 52.57 | 67.57 |
| Fro | GPT-5.4 | 82.90 | 66.95 | 68.13 | 62.37 | 81.08 | 81.61 | 67.46 | 72.93 |
|  | Gemini 3.1 Pro | 68.77 | 61.45 | 62.33 | 53.47 | 76.73 | 75.32 | 65.50 | 66.22 |
|  |  |  |  |  |  |  |  |  |  |
| ight | DeepSeek-V4-Pro | 69.90 | 56.85 | 57.40 | 44.50 | 76.36 | 72.83 | 61.28 | 62.73 |
| we | Kimi K2.6 | 70.30 | 69.40 | 55.53 | 45.20 | 61.90 | 75.63 | 62.49 | 62.92 |
| pen- | GLM-5.1 | 72.53 | 71.70 | 55.47 | 41.77 | 67.98 | 72.06 | 55.98 | 62.50 |
| O | MiniMax-M2.7 | 55.03 | 44.30 | 32.40 | 25.17 | 71.87 | 70.36 | 49.39 | 49.79 |
|  |  |  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |  |  |
| n | Qwen3.6-35B-A3B | 49.50 | 47.00 | 41.30 | 35.07 | 59.79 | 67.83 | 44.03 | 49.22 |
| Qwe | Qwen3.6-Plus | 67.57 | 67.90 | 58.43 | 47.57 | 63.81 | 69.85 | 54.29 | 61.35 |
|  | Qwen3.6-Max-Preview | 73.40 | 64.05 | 59.37 | 45.03 | 60.19 | 67.02 | 50.47 | 59.93 |
|  |  |  |  |  |  |  |  |  |  |
|  | Qwen3.5-35B-A3B | 57.80 | 40.70 | 36.83 | 28.50 | 61.10 | 68.49 | 44.07 | 48.21 |
| Ours | Qwen-AgentWorld-35B-A3B | 60.47 | 44.90 | 54.53 | 48.73 | 62.34 | 72.37 | 57.61 | 57.28 |
|  | Qwen3.5-397B-A17B | 67.33 | 63.50 | 51.80 | 44.17 | 69.25 | 70.22 | 54.03 | 60.04 |
|  | Qwen-AgentWorld-397B-A17B | 72.37 | 58.95 | 62.63 | 60.33 | 76.79 | 80.74 | 58.01 | 67.12 |

::: figure
src: assets/qwen-agentworld-table-11.png
alt: Table 11 from qwen-agentworld.pdf
caption: Table 11: Rule-based evaluation on text-based domains: accuracy (%, ↑) on three sub-capabilities. Ctrl: controllability; Err: error handling; LC: long-context consistency. The highest and second-best scores are shown in bold and underlined, respectively.
source: 本地 qwen-agentworld.pdf p.39
:::

**Extracted table**:

|  |  |  | MCP |  |  | Term. |  | Sear | ch |  | SWE |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  | Model |  |  |  |  |  |  |  |  |  |  |  | Avg |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  | Ctrl | Err | LC | Ctrl | Err | LC | Ctrl | LC | Ctrl | Err | LC |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| r | Claude Opus 4.6 | 72.3 | 78.4 | 80.0 | 68.7 | 81.0 | 56.1 | 74.2 | 80.9 | 52.8 | 59.6 | 50.8 | 69.4 |
| ntie | Claude Sonnet 4.6 | 74.3 | 77.0 | 78.0 | 63.9 | 77.0 | 52.4 | 72.0 | 71.8 | 57.5 | 59.1 | 49.2 | 67.0 |
| Fro | GPT-5.4 | 76.2 | 84.5 | 88.0 | 62.0 | 88.7 | 53.7 | 70.5 | 63.4 | 59.8 | 65.4 | 61.9 | 70.1 |
|  | Gemini 3.1 Pro | 59.6 | 71.7 | 75.0 | 60.0 | 77.0 | 50.0 | 61.8 | 61.1 | 52.0 | 58.4 | 50.0 | 61.5 |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| ight | DeepSeek-V4-Pro | 63.4 | 72.3 | 74.0 | 50.6 | 74.0 | 47.6 | 54.9 | 58.8 | 52.0 | 52.9 | 28.6 | 57.2 |
| we | Kimi K2.6 | 65.3 | 71.6 | 74.0 | 49.4 | 73.3 | 43.9 | 66.3 | 72.5 | 43.3 | 55.8 | 36.5 | 60.1 |
| pen- | GLM-5.1 | 67.3 | 74.3 | 76.0 | 49.4 | 74.3 | 42.7 | 70.1 | 73.3 | 42.5 | 49.5 | 33.3 | 60.4 |
| O | MiniMax-M2.7 | 39.6 | 63.5 | 62.0 | 30.1 | 50.0 | 17.1 | 41.7 | 46.9 | 29.1 | 27.4 | 19.0 | 39.2 |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| n | Qwen3.6-35B-A3B | 37.6 | 66.9 | 44.0 | 37.3 | 61.0 | 25.6 | 45.1 | 48.9 | 41.7 | 36.5 | 27.0 | 43.2 |
| Qwe | Qwen3.6-Plus | 60.4 | 70.3 | 72.0 | 51.8 | 74.7 | 48.8 | 63.3 | 72.5 | 52.0 | 55.8 | 34.9 | 60.4 |
|  | Qwen3.6-Max-Preview | 69.3 | 70.9 | 80.0 | 54.8 | 75.7 | 47.6 | 60.2 | 67.9 | 44.1 | 57.7 | 33.3 | 60.5 |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  | Qwen3.5-35B-A3B | 54.5 | 64.9 | 54.0 | 32.5 | 50.0 | 28.0 | 33.3 | 48.1 | 34.6 | 30.3 | 20.6 | 41.0 |
| Ours | Qwen-AgentWorld-35B-A3B | 52.5 | 68.9 | 60.0 | 50.0 | 67.3 | 46.3 | 37.1 | 52.7 | 48.0 | 60.1 | 38.1 | 52.2 |
|  | Qwen3.5-397B-A17B | 60.4 | 73.6 | 68.0 | 47.0 | 65.7 | 42.7 | 59.8 | 67.2 | 44.1 | 56.7 | 31.7 | 56.7 |
|  | Qwen-AgentWorld-397B-A17B | 63.4 | 75.7 | 78.0 | 59.0 | 77.7 | 51.2 | 56.1 | 61.8 | 61.4 | 62.5 | 57.1 | 63.6 |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| Table 12 | : Rule-based evaluation on | GU | I dom | ains: | acc | uracy | (%, | ↑) on | thre | e su | b-cap | abilit | ies. |
| controlla | bility; Err: error handling; LC | : lon | g-con | text c | onsi | stency | . The | high | est a | nd se | cond | -best | scor |
| shown i | n bold and underlined, respe | ctive | ly. |  |  |  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  |  | A | ndroi | d |  | Web |  |  | O | S |  |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  | Model |  |  |  |  |  |  |  |  |  |  |  | Avg |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  |  | Ctrl | Err | LC | Ctrl | Err | LC | Ct | rl | Err | LC |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| r | Claude Opus 4.6 |  | 80.9 | 79.4 | 79.7 | 82.8 | 60.0 | 84. | 3 70 | .9 5 | 9.0 5 | 2.0 | 72.1 |
| ntie | Claude Sonnet 4.6 |  | 77.9 | 69.8 | 76.0 | 81.7 | 68.0 | 81. | 8 60 | .9 4 | 9.0 4 | 5.1 | 67.8 |
| Fro | GPT-5.4 |  | 77.4 | 82.5 | 83.9 | 79.6 | 80.0 | 85. | 2 71 | .2 7 | 2.0 5 | 4.6 | 76.3 |
|  | Gemini 3.1 Pro |  | 72.6 | 87.3 | 74.2 | 79.0 | 68.0 | 79. | 0 60 | .4 8 | 0.5 5 | 0.0 | 72.3 |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| ight | DeepSeek-V4-Pro |  | 73.2 | 85.7 | 73.6 | 78.3 | 62.0 | 78. | 2 68 | .3 6 | 1.0 5 | 0.8 | 70.1 |
| we | Kimi K2.6 |  | 63.9 | 58.7 | 61.9 | 79.1 | 69.0 | 78. | 8 71 | .2 6 | 0.0 5 | 2.8 | 66.2 |
| pen- | GLM-5.1 |  | 68.0 | 65.1 | 69.9 | 78.5 | 64.0 | 73. | 7 62 | .6 5 | 3.0 5 | 0.4 | 65.0 |
| O | MiniMax-M2.7 |  | 66.9 | 77.8 | 73.1 | 68.5 | 73.0 | 69. | 6 51 | .6 5 | 1.0 4 | 3.5 | 63.9 |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| n | Qwen3.6-35B-A3B |  | 56.7 | 66.7 | 58.6 | 72.4 | 60.0 | 71. | 1 50 | .1 3 | 8.0 4 | 4.0 | 57.5 |
| Qwe | Qwen3.6-Plus |  | 62.3 | 69.8 | 61.6 | 69.2 | 66.0 | 74. | 4 58 | .3 5 | 5.0 4 | 7.0 | 62.6 |
|  | Qwen3 6-Max-Preview |  | 60 1 | 68 3 | 55 2 | 68 6 | 58 0 | 74 | 5 47 | 7 5 | 3 0 5 | 0 9 | 59 6 |

::: figure
src: assets/qwen-agentworld-table-12.png
alt: Table 12 from qwen-agentworld.pdf
caption: Table 12: Rule-based evaluation on GUI domains: accuracy (%, ↑) on three sub-capabilities. Ctrl: controllability; Err: error handling; LC: long-context consistency. The highest and second-best scores are shown in bold and underlined, respectively.
source: 本地 qwen-agentworld.pdf p.39
:::

**Extracted table**:

|  |  | Android |  | Web |  |  | OS |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  |  |
|  | Model |  |  |  |  |  |  |  | Avg. |
|  |  |  |  |  |  |  |  |  |  |
|  | Ctrl | Err LC | Ctrl | Err | LC | Ctrl | Err | LC |  |
|  |  |  |  |  |  |  |  |  |  |
| r | Claude Opus 4.6 80. | 9 79.4 79.7 | 82.8 | 60.0 | 84.3 | 70.9 | 59.0 | 52.0 | 72.1 |
| ntie | Claude Sonnet 4.6 77. | 9 69.8 76.0 | 81.7 | 68.0 | 81.8 | 60.9 | 49.0 | 45.1 | 67.8 |
| Fro | GPT-5.4 77. | 4 82.5 83.9 | 79.6 | 80.0 | 85.2 | 71.2 | 72.0 | 54.6 | 76.3 |
|  | Gemini 3.1 Pro 72. | 6 87.3 74.2 | 79.0 | 68.0 | 79.0 | 60.4 | 80.5 | 50.0 | 72.3 |
|  |  |  |  |  |  |  |  |  |  |
| ight | DeepSeek-V4-Pro 73. | 2 85.7 73.6 | 78.3 | 62.0 | 78.2 | 68.3 | 61.0 | 50.8 | 70.1 |
| we | Kimi K2.6 63. | 9 58.7 61.9 | 79.1 | 69.0 | 78.8 | 71.2 | 60.0 | 52.8 | 66.2 |
| pen- | GLM-5.1 68. | 0 65.1 69.9 | 78.5 | 64.0 | 73.7 | 62.6 | 53.0 | 50.4 | 65.0 |
| O | MiniMax-M2.7 66. | 9 77.8 73.1 | 68.5 | 73.0 | 69.6 | 51.6 | 51.0 | 43.5 | 63.9 |
|  |  |  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |  |  |
| n | Qwen3.6-35B-A3B 56. | 7 66.7 58.6 | 72.4 | 60.0 | 71.1 | 50.1 | 38.0 | 44.0 | 57.5 |
| Qwe | Qwen3.6-Plus 62. | 3 69.8 61.6 | 69.2 | 66.0 | 74.4 | 58.3 | 55.0 | 47.0 | 62.6 |
|  | Qwen3.6-Max-Preview 60. | 1 68.3 55.2 | 68.6 | 58.0 | 74.5 | 47.7 | 53.0 | 50.9 | 59.6 |
|  |  |  |  |  |  |  |  |  |  |
|  | Qwen3.5-35B-A3B 57. | 2 66.0 60.1 | 74.3 | 63.6 | 67.6 | 47.7 | 41.4 | 43.1 | 57.9 |
| Ours | Qwen-AgentWorld-35B-A3B 53. | 0 95.2 51.4 | 66.2 | 84.3 | 66.6 | 60.1 | 53.0 | 60.9 | 65.6 |
|  | Qwen3.5-397B-A17B 67. | 4 65.1 73.8 | 71.0 | 68.0 | 71.7 | 58.9 | 54.0 | 46.5 | 64.0 |
|  | Qwen-AgentWorld-397B-A17B 81. | 3 88.7 64.9 | 75.8 | 84.5 | 82.0 | 56.5 | 60.0 | 57.2 | 72.3 |

