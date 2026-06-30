# LearnLoop Course Blueprint: Qwen-AgentWorld

## Learner Job
After completing this course, a researcher or engineer should be able to:

1. **Explain the role of world models in general agent systems**: articulate why next-state prediction is a necessary (not merely useful) cognitive mechanism for general agents, and how it complements the policy (state-to-action) component.
2. **Design and implement a language world model (LWM) training pipeline**: understand the three-stage recipe (CPT -> SFT -> RL), apply information-theoretic loss masking, construct unified trajectory schemas, and implement hybrid rubric-and-rule reward design for RL.
3. **Evaluate world model fidelity using multi-dimensional rubrics**: construct or adapt benchmarks like AgentWorldBench, design reference-grounded LLM judges with differentiated matching criteria, and interpret five-dimensional rubric scores (Format, Factuality, Consistency, Realism, Quality).
4. **Apply world models as environment simulators for agentic RL**: implement controllable simulation (environment adaptation and fictional-world construction), scale simulated environments for Sim RL, and diagnose sim-to-real transfer gaps.
5. **Integrate world-model training as an agent foundation model warm-up**: use LWM pre-training to improve downstream agent performance across diverse benchmarks, and explain the mechanism (prediction-driven action refinement) behind the transfer.
6. **Compare decoupled vs. unified agent-world-model architectures**: analyze trade-offs between using a separate simulator (scalability, controllability) and unifying world modeling into the agent itself (internalized planning, reduced infrastructure).

## Target Audience
- AI researchers studying agent world models, simulation, and agentic RL
- Engineers building training infrastructure for LLM agents
- Graduate students and advanced practitioners in NLP/RL who want to move beyond policy-only agent training
- Prerequisites: familiarity with transformer architectures, basic RL (PPO/GRPO), and agent tool-use patterns

## Module Plan

### Module 1: Foundations — Why Language World Models?
- **Content form**: Perspective + Reference
- **Learning actions**:
  - Explain the agent-environment loop and the missing world-model piece (cite LeCun et al., 2022; Richens et al., 2025)
  - Contrast policy-only agent training with world-model-augmented agents
  - Map the seven domains of Qwen-AgentWorld to their core capabilities (Table 1)
  - Articulate the two complementary paradigms: Decouple (simulator) vs. Unify (foundation model)
- **Key evidence needed**:
  - Figure 1 (overview diagram)
  - Table 1 (seven domains, actions, observations, capabilities)
  - Figure 2 (unified domain diagram)
  - Claim: "any agent capable of generalizing across a sufficiently broad range of tasks must have learned a world model" (Richens et al., 2025)
- **Proposed semantic components**:
  - concept: world model, policy, observation, action, stateful vs. stateless environments
  - compare: policy-only vs. world-model-augmented agents
  - figure: Figure 1, Figure 2, Table 1

### Module 2: The Unified Environment Trajectory Schema
- **Content form**: Tutorial + Reference
- **Learning actions**:
  - Construct a system prompt with the five components (task description, action space, initial state, demonstrations, simulation instruction)
  - Distinguish static vs. dynamic components per domain
  - Normalize raw agentic trajectories into the unified schema
  - Apply trajectory-to-turn expansion and filtering (retry-cycle skipping, no-change turn filtering)
- **Key evidence needed**:
  - Figure 3 (Terminal system prompt anatomy with static/dynamic coloring)
  - Figure 4 (SWE and Android interaction examples)
  - Section 2.2 formal schema definition
  - Claim: "Because each trajectory is expanded into turn-level prediction samples, the model receives supervision at every turn"
- **Proposed semantic components**:
  - concept: unified environment trajectory schema, turn-level expansion
  - flow: trajectory -> turns -> training samples
  - figure: Figure 3, Figure 4

### Module 3: Three-Stage Training Recipe
- **Content form**: Tutorial + Practice
- **Learning actions**:
  - Implement CPT with information-theoretic loss masking (compute OL, Nov, Jac, R; assign categories and keep ratios)
  - Design SFT reasoning traces with rejection sampling and prompt template diversification
  - Configure RL with hybrid rubric-and-rule rewards (9:1 ratio) and mitigate reward collapse/hacking
  - Diagnose training stability issues (shared-prefix collapse, reward shaping alternatives)
- **Key evidence needed**:
  - Figure 5 (three-stage pipeline diagram)
  - Table 2 (SFT/RL data statistics per domain)
  - Table 3 (seven turn categories for loss masking)
  - Table 4 (rejection sampling statistics)
  - Section 3.4.2 (training stability failure modes and solutions)
  - Claim: "Factuality shows the largest relative improvement (11.3%) yet remains the lowest-scoring dimension throughout"
- **Proposed semantic components**:
  - flow: CPT -> SFT -> RL with feedback loops
  - concept: information-theoretic loss masking, rejection sampling, reward hacking, echo trap
  - figure: Figure 5, Table 3
  - decision: when to use rubric vs. rule-based rewards

### Module 4: AgentWorldBench — Evaluating World Models
- **Content form**: Tutorial + Reference
- **Learning actions**:
  - Construct a reference-grounded LLM judge with five-dimensional rubrics
  - Apply differentiated matching criteria (deterministic / pre-existing / runtime metadata)
  - Calibrate judge prompts via double-blind Turing tests
  - Interpret per-domain scores and identify failure modes (e.g., Search as weakest domain)
- **Key evidence needed**:
  - Figure 6 (AgentWorldBench composition overview)
  - Figure 7 (main results bar chart per domain)
  - Table 5 (full rubric mean results across all models)
  - Section 4.2 (evaluation protocol, reference-grounded judging, content-type classification)
  - Claim: "pairwise Spearman rank correlations are rho = 0.92-0.99 (all p < 10^-5)" across judges
- **Proposed semantic components**:
  - concept: reference-grounded judging, differentiated matching, Turing-test calibration
  - compare: model rankings across domains (Table 5)
  - figure: Figure 6, Figure 7, Table 5
  - evidence: judge consistency statistics

### Module 5: Application I — World Model as Environment Simulator
- **Content form**: Practice + Perspective
- **Learning actions**:
  - Implement zero-shot environment scaling (e.g., synthesize 4k OpenClaw environments)
  - Design controllable simulation instructions for environment adaptation (targeted perturbations)
  - Construct fictional-world simulations with self-consistent factuality
  - Compare Sim RL vs. Real RL and diagnose state-bottleneck issues
- **Key evidence needed**:
  - Table 6 (Sim RL on OpenClaw environments)
  - Table 7 (controllable Sim RL on Tool Decathlon / MCPMark)
  - Table 8 (fictional-world Sim RL on WideSearch)
  - Figure 9 (Sim RL vs. Real RL training curves and tool-call divergence)
  - Section 6.1.2 (controllable simulation design)
  - Claim: "controllable Sim RL exceeds Real RL trained using a live search engine (50.3% vs. 45.6%)"
- **Proposed semantic components**:
  - concept: controllable simulation, environment adaptation, fictional-world construction, sim-to-real transfer
  - compare: Sim RL vs. Real RL (Figure 9)
  - figure: Table 6, Table 7, Table 8, Figure 9
  - decision: when to use decoupled simulator vs. real environment

### Module 6: Application II — World Model as Agent Foundation Model
- **Content form**: Practice + Perspective
- **Learning actions**:
  - Apply LWM RL warm-up to improve downstream agent performance without additional fine-tuning
  - Identify prediction-driven action refinement in agent thinking traces
  - Quantify prediction accuracy before vs. after LWM training
  - Explain cross-domain transfer mechanisms (e.g., Terminal RL training improving SWE and Search)
- **Key evidence needed**:
  - Table 9 (agent foundation model results across 7 benchmarks)
  - Figure 10 (prediction accuracy improvement: 69.9% -> 78.3%)
  - Figure 11 (mailman case study of prediction-driven action refinement)
  - Figure 8 (cross-domain generalization: Terminal RL -> MCP/SWE/Search gains)
  - Section 6.2 (unified agent foundation model mechanism)
  - Claim: "LWM RL warm-up on single-turn, non-agentic trajectories transfers to multi-turn, tool-calling agentic tasks"
- **Proposed semantic components**:
  - concept: prediction-driven action refinement, mental simulation, meta-reasoning pattern
  - flow: LWM warm-up -> internalized prediction -> refined action -> improved agent performance
  - figure: Table 9, Figure 10, Figure 11, Figure 8
  - evidence: cross-domain transfer numbers

### Module 7: Analysis and Reasoning Patterns (Optional Deep-Dive)
- **Content form**: Reference + Perspective
- **Learning actions**:
  - Analyze LWM chain-of-thought reasoning patterns (deliberative self-correction, information leakage prevention, epistemic boundary awareness)
  - Examine micro-level fidelity improvements during RL (URL realism, byte-level arithmetic, schema consistency)
  - Map reasoning patterns to downstream agent capabilities
- **Key evidence needed**:
  - Figure 12 (representative LWM reasoning patterns)
  - Figure 13 (micro-level fidelity improvements across RL steps)
  - Section 7.1 (aggregate statistics: 1,347 "Wait!" interrupts across 129 turns)
  - Section 7.2 (character-level byte arithmetic, cross-turn API schema fidelity)
- **Proposed semantic components**:
  - concept: deliberative self-correction, theory of mind in world models, epistemic boundary awareness
  - figure: Figure 12, Figure 13
  - timeline: RL training dynamics (Figure 16 shows Format converges ~90 steps, Consistency ~250 steps)

## Cross-Module Dependencies
- Module 1 provides motivation and terminology for all subsequent modules.
- Module 2 (schema) is prerequisite for Module 3 (training data processing).
- Module 3 (training recipe) is prerequisite for Module 4 (evaluation of trained models) and Module 7 (analysis of training dynamics).
- Module 4 (evaluation) is prerequisite for Modules 5 and 6 (applications), as both rely on interpreting AgentWorldBench-style metrics.
- Modules 5 and 6 are independent of each other and can be taken in either order after Module 4.
- Module 7 is optional and assumes completion of Modules 3 and 4.

## Key Design Decisions
- **Depth over breadth**: Each module targets a specific technical skill (schema construction, loss masking, judge calibration, controllable simulation, warm-up integration) rather than summarizing the paper section-by-section.
- **Evidence-first**: Every module explicitly ties learning actions to figures, tables, and claims from the paper, with section IDs preserved for later module drafting.
- **Uncertainty marked**: Where the paper makes comparative claims (e.g., GUI domain gaps reflect multimodal pre-training advantage), these are noted as interpretations rather than facts.
- **No unsupported timelines**: No claims about when specific capabilities will be "mature" or market-ready.
