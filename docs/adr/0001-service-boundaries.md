# ADR 0001: service boundaries for experiment execution

## Status

Accepted.

## Decision

Use five deployable services: control-plane, runner, model-gateway, evaluator and telemetry. Keep benchmark parsing, statistical analysis and dashboard rendering in the versioned research package until scale or access control requires a separate deployment.

## Consequences

- The runner can be isolated and autoscaled independently from APIs.
- Provider credentials remain outside runners and evaluators.
- The telemetry contract becomes a compatibility boundary; its version changes require migration.
- Local development has more moving parts, so Docker Compose is provided and single-process fixture mode remains available for fast tests.
