# Performance Report

Tool: k6  
Scenario: 10 virtual users call `GET /tasks` for 30 seconds.  
Target threshold: p95 latency below 500 ms.

## Command

```bash
k6 run perf/load-test.js
```

## Expected Interpretation

- `http_req_duration p(95)` is the main latency metric for the rubric.
- `http_req_failed` should stay close to 0%.
- Grafana should show a short increase in request rate during the run.

## Result Placeholder

Replace this section after the final local run:

- p95 latency: TBD ms
- total requests: TBD
- failed requests: TBD
- observation: The API should stay under the 500 ms p95 threshold for the local demo workload.
