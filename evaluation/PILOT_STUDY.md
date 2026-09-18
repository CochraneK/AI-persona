# Human Ontology Tier-B Pilot Study

## Purpose

Test whether independent reviewers map the same human facts to the same Human Ontology semantics.

## Materials

`pilot_annotation_pack.csv` contains a blinded, deterministically shuffled annotation pack derived from the 24 adversarial boundary cases.

- annotators: 3;
- rows: 168;
- expected ontology answers are **not** included;
- each row asks for canonical home, kind, temporal class, relation predicate, source type, confidence and ambiguity note.

## Recruitment target

Pilot:
- 3 independent annotators;
- preferably at least one ontology/data-modelling reviewer and at least one human/behavioral/social/health-domain reviewer;
- ontology authors should not be the only raters.

Formal follow-up:
- expand beyond the adversarial set to 100+ atomic facts;
- preserve independent annotation before adjudication.

## Procedure

1. Give each reviewer only their rows / instructions and the public ontology documentation.
2. Do not provide the preferred answer key.
3. Collect completed CSVs.
4. Combine rows without altering annotations.
5. Run:

```bash
python scripts/analyze_annotation_reliability.py evaluation/pilot_annotation_pack.csv --json
```

6. Review disagreements before revealing ontology-author expectations.
7. Classify each disagreement as ontology ambiguity, instruction ambiguity, insufficient information or annotator error.

## Preregistered project targets

These are engineering/review thresholds, not universal psychometric laws:

- kappa >= .80: candidate for stable first-class semantics;
- .67–.79: wording/boundary review;
- < .67: redesign or stronger semantic instructions required.

Report agreement separately for canonical home, kind, temporality, relation predicate and source type.
