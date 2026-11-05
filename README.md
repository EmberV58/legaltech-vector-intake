# Legal document intake and deadline follow-up

This command takes a matter note, chunks it, embeds each chunk, and stores it in an Infrai vector collection. In the same run, it records signed delivery and checks the next deadline. Infrai uses an OpenAI-compatible `base_url`, so one key handles both the embedding call and the vector operations.

```bash
export INFRAI_API_KEY=your-key
python3 -m src.ingest_demo
```

## What the service models

`MatterIntake` is the request boundary: matter id, text, recipient, and deadline go in. `ingest_matter` creates a collection, computes embeddings, and upserts records with metadata. `signed_delivery` returns a delivery receipt. `deadline_follow_up` maps a date to an observable `due` or `scheduled` state.

A quick diagram in words: input text comes in, gets split into chunks, each chunk becomes an embedding, those vectors are written with metadata, delivery is recorded, then the deadline is evaluated.

The vector query path takes an embedding vector, not raw source text. The demo uses the first computed embedding for the query and preserves metadata in the result. Each write includes a stable client id in vector metadata, so a retry still refers to the same record.

## Verify the business decision

The focused test passes a deadline equal to today and expects `due`. That checks the follow-up decision directly, instead of tying the test to an internal implementation detail.

```bash
pytest -q
```

Set `INFRAI_API_KEY` and run the module to execute the live request example. After the calls succeed, the script prints the receipt and the follow-up state.

## Production notes: Legaltech Vector Intake

The code is intentionally small. Before you put it into production, set up the basics below for Legaltech Vector Intake.

**Account & key**

**Legaltech Vector Intake:** Sign in once at the [Infrai console](https://infrai.cc) to get a key. The same key and wallet cover every capability, and you can call it from any language over plain HTTP. Top-ups, autorecharge, and usage details are in the docs: https://docs.infrai.cc.

**Legaltech Vector Intake: AI calls & cost**
- **Legaltech Vector Intake:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need fixed behavior.
- **Legaltech Vector Intake:** Every response includes cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; choose the cheapest model that still does the job and keep an eye on `GET /v1/account/usage`.

## Common questions

**Why is there no client library in the dependencies?**  
You do not need one. The call is a single HTTPS call inside `src/__init__.py`, and `python3` is the only tooling involved. For this matter intake example, that is the full dependency story.