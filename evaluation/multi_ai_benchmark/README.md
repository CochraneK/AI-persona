# Multi-AI Semantic Benchmark

Tier B1 evaluates **cross-model semantic robustness**. Different AI systems act as independent computational raters over the same blinded ontology-mapping tasks.

This is **not equivalent to independent human/expert validation**. Models may share training data, architectural conventions, vendor data, or correlated biases. The benchmark therefore reports both:

1. **agreement** — do different models map the same fact the same way?
2. **accuracy / boundary safety** — are they agreeing with the adversarial gold boundary and refusing unsupported inferences?

High agreement with low accuracy is explicitly reported as **agreement-but-wrong**.

## Benchmark design

Each atomic item contains:
- a synthetic vignette;
- a neutral fact key;
- a hidden gold semantic namespace used only by the scorer;
- candidate forbidden inferences used to test false deterministic inference.

The model receives:
- the vignette;
- the fact key;
- the 18 namespace descriptions;
- the six ontological kinds;
- allowed relation predicates;
- epistemic source types;
- candidate inferences to judge as entailed / not entailed.

The model does **not** receive the gold domain.

## Providers

The standard-library runner supports:
- OpenAI Responses API;
- Anthropic Messages API;
- Gemini generateContent API;
- generic OpenAI-compatible Chat Completions endpoints (for example Qwen / DeepSeek / other compatible providers).

Model IDs are configuration, not ontology facts. Keep them in environment variables so a dated benchmark can pin whatever model versions are actually used.

## Setup

Copy the example config and set only environment variables:

```bash
cp evaluation/multi_ai_benchmark/models.example.json evaluation/multi_ai_benchmark/models.local.json

export OPENAI_API_KEY=...
export HO_OPENAI_MODEL=...

export ANTHROPIC_API_KEY=...
export HO_ANTHROPIC_MODEL=...

export GEMINI_API_KEY=...
export HO_GEMINI_MODEL=...

export DASHSCOPE_API_KEY=...
export HO_QWEN_MODEL=...
export HO_QWEN_BASE_URL=...

export DEEPSEEK_API_KEY=...
export HO_DEEPSEEK_MODEL=...
```

Never commit API keys or local model configuration.

## Run

Build/check benchmark cases:

```bash
python scripts/build_multi_ai_benchmark.py
python scripts/build_multi_ai_benchmark.py --check
```

Preview prompts without calling any API:

```bash
python scripts/run_multi_ai_benchmark.py \
  --config evaluation/multi_ai_benchmark/models.example.json \
  --dry-run
```

Run configured models:

```bash
python scripts/run_multi_ai_benchmark.py \
  --config evaluation/multi_ai_benchmark/models.local.json
```

Analyze:

```bash
python scripts/analyze_multi_ai_benchmark.py \
  evaluation/multi_ai_benchmark/outputs \
  --json-out evaluation/multi_ai_benchmark/report.local.json \
  --md-out evaluation/multi_ai_benchmark/REPORT.local.md
```

## Tier-B1 preregistered project targets

These are project review gates, not universal scientific cutoffs:

- at least **3 model families/providers** successfully complete the benchmark;
- >= 95% response completeness;
- >= .80 pairwise agreement on canonical domain;
- >= .80 Fleiss' kappa on canonical domain when balanced;
- >= 90% per-model adversarial domain accuracy;
- <= 5% forbidden-inference false-positive rate;
- **0 critical agreement-but-wrong items**.

Failure triggers ontology/prompt review. It must not be “fixed” by hiding difficult cases.

## Evidence claim

Passing Tier B1 supports:

> the reviewed ontology boundaries are robust across the tested AI raters under this benchmark protocol.

It does **not** support:

> humans independently agree with the ontology;

or:

> the ontology is universally or clinically validated.
