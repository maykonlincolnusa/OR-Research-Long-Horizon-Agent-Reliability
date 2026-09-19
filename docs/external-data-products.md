# External data products

## NASA Exoplanet Archive

The first external integration is a read-only dashboard backed by the official NASA Exoplanet Archive TAP service. It uses the `PSCompPars` table because the archive documents it as a more complete, one-row-per-planet table for statistical views of confirmed exoplanets.

The service sends four fixed ADQL queries only: total planets, discovery-method aggregate, discovery-year aggregate and a small recent-record projection. It does not accept arbitrary ADQL from users, does not persist raw NASA rows and caches a response for 15 minutes in process. Each response reports source endpoint, retrieval timestamp and SHA-256 fingerprints of the fixed queries.

This integration is intentionally outside the software-agent benchmark. Its purpose is to demonstrate production data-engineering concerns — source provenance, constrained queries, freshness, response validation, read-only access and a visualization — without conflating an unrelated scientific data source with agent-reliability evidence.

Sources: [NASA TAP guide](https://exoplanetarchive.ipac.caltech.edu/docs/API_resources.html) · [PS/PSCompPars column guidance](https://exoplanetarchive.ipac.caltech.edu/docs/API_TD_columns.html).
