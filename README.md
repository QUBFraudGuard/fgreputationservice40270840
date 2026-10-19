# fgreputationservice40270840

The slow half of QUBCloud-FraudGuard's screening. It looks up a risk score for each card from an external reputation service and flags risky transactions.

Part of [QUBCloud-FraudGuard](https://github.com/QUBFraudGuard).

## How it works

For each transaction it calls the external lookup with the card number. If the returned risk score is above the threshold (70), the transaction is `SUSPICIOUS`. Lookups for a batch run concurrently, which cut a 200-transaction batch from around 44 seconds to about 3 seconds.

## Fails closed

| Situation | Result |
| --- | --- |
| Lookup unreachable or times out (1 s) | Flagged |
| Non-2xx response | Flagged |
| Response missing `risk_score` | Flagged |
| Score above the threshold | Flagged |

The trade-off is that during an outage, legitimate transactions get blocked. I chose caution over letting anything through unchecked.

## API

```
GET /screen?items=5000-1234-UK,50000-9999-UK
```

Returns the same JSON shape as [fgscreeningservice](https://github.com/QUBFraudGuard/fgscreeningservice40270840). `GET /health` returns the service status.

## Configuration

| Variable | Purpose |
| --- | --- |
| `REPUTATION_SERVICE_URL` | Address of the external reputation lookup |

## Run it

```bash
git clone https://github.com/QUBFraudGuard/fgreputationservice40270840.git
cd fgreputationservice40270840
docker build -t fgreputationservice40270840 .
# 1. Start the external lookup (see externalreputationlookup40270840)
# 2. Start the reputation service, pointing at it
docker run -p 8072:8072 \
  -e REPUTATION_SERVICE_URL=http://host.docker.internal:<5000> \
  fgreputationservice40270840
```


## Related

[externalreputationlookup](https://github.com/QUBFraudGuard/externalreputationlookup40270840) · [fgproxy](https://github.com/QUBFraudGuard/fgproxy40270840)
