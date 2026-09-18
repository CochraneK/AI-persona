# Methodological References for Human Ontology Evaluation

This file records why the evaluation framework uses multiple evidence layers. It is not a claim that Human Ontology is endorsed by any listed organization.

## OBO Foundry — manual + automated review

- OBO Foundry ontology review SOP: https://obofoundry.org/docs/SOP.html
- OBO Foundry Standardization Guidelines: https://obofoundry.org/docs/StandardizationGuidelines.html

Relevant principles for this project:
- automated checks do not replace manual scientific/semantic review;
- relation usage should respect intended definitions/domain/range;
- logical consistency, unsatisfiable classes and circular definitions are formal-quality concerns.

## W3C SHACL

- SHACL Recommendation (2017): https://www.w3.org/TR/shacl/
- SHACL 1.2 Core Working Draft: https://www.w3.org/TR/shacl12-core/

SHACL motivates a future RDF instance-validation layer. The 2017 Recommendation is the stable normative reference; 1.2 is tracked as evolving work and should not be treated as a finalized dependency.

## OQuaRE / competency-question evaluation

- OQuaRE / GoodOD evaluation study: https://pmc.ncbi.nlm.nih.gov/articles/PMC4141745/

The study compares ontology-quality evaluation using OQuaRE with gold-standard and competency-question approaches, supporting the use of multiple complementary evaluation methods rather than one global metric.

## FAIR semantic artefacts

- FAIR-IMPACT assessment tools: https://fair-impact.eu/fair-assessment-tools
- FAIR-IMPACT FAIR-by-design methodology: https://fair-impact.eu/semantic-artefact-fair-design-methodology

Tools such as FOOPS! and O'FAIRe are candidates for a later published RDF/OWL artefact. FAIR assessment concerns findability/accessibility/interoperability/reusability; it is not a substitute for substantive human-science validity.

## Project-specific thresholds

The inter-rater thresholds in `EVALUATION_PROTOCOL.md` are **predeclared project review targets**, not universal psychometric or ontology-science cutoffs. They are used to trigger review/redesign consistently and must be reported as such.

## Evidence discipline

A citation to an external standard supports the **method used to evaluate the ontology**, not the truth of every Human Ontology concept. Empirical priors, mappings and domain-specific scientific claims require their own source/version/population evidence.
