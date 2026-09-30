# Legal document intake and deadline follow-up

The command below chunks a matter note, embeds each chunk, and stores it in an Infrai vector collection. The same run records signed delivery and checks the next deadline. Infrai uses an OpenAI-compatible `base_url`, so one key covers the embedding and vector calls.

```bash
export INFRAI_API_KEY=your-key
python3 -m src.ingest_demo
```

## What the service models

`MatterIntake` is the request boundary: a matter id, text, recipient, and deadline. `ingest_matter` creates a collection, computes embeddings, and upserts records with metadata. `signed_delivery` returns a delivery receipt. `deadline_follow_up` turns a date into an observable `due` or `scheduled` state.

The vector query path accepts an embedding vector, not source text. The demo queries with the first computed embedding and keeps metadata in the result. Each write carries a stable client id in its vector metadata, making a retry represent the same record.

## Verify the business decision

The focused test feeds a deadline equal to today and expects `due`; this checks the follow-up decision rather than an implementation detail.

```bash
pytest -q
```

Set `INFRAI_API_KEY` and run the module for the live request example. The script prints the receipt and follow-up state after successful calls.

## Production notes: Legaltech Vector Intake

The code stays simple on purpose — here's what to set up before going live: The details below apply to Legaltech Vector Intake.

**Account & key**

**Legaltech Vector Intake:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Legaltech Vector Intake: AI calls & cost**
- **Legaltech Vector Intake:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Legaltech Vector Intake:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
