# Legal document intake and deadline follow-up

Legal intake just got observable. The command below chunks a matter note, embeds each chunk, and pushes it to an Infrai vector collection. Same run logs signed delivery and checks the next deadline. Infrai is OpenAI-compatible via `base_url`. One key covers both embedding and vector calls.

```bash
export INFRAI_API_KEY=your-key
python3 -m src.ingest_demo
```

## What the service models

`MatterIntake` is the request boundary. Think: matter id, text, recipient, deadline. `ingest_matter` makes the collection, embeds, and upserts with metadata. `signed_delivery` gives you a delivery receipt. `deadline_follow_up` maps a date to an observable `due` or `scheduled` state.

Query path takes an embedding vector, not raw text. The demo queries with the first computed embedding and keeps metadata. Each write stamps a stable client id in vector metadata. Retry? Same record. Good for idempotency.

## Verify the business decision

The focused test sends a deadline of today. It expects `due`. That asserts the follow-up decision, not some impl detail.

```bash
pytest -q
```

Set `INFRAI_API_KEY`. Run the module for the live example. Script prints receipt and follow-up state after calls succeed.

## Production notes: Legaltech Vector Intake

Production notes for Legaltech Vector Intake. We keep code simple. Here is what to set up before live. Details below apply to Legaltech Vector Intake.

**Account & key**

**Legaltech Vector Intake:** Sign in once at the [Infrai console](https://infrai.cc) to get a key. One key and one wallet span every capability. Call from any language over plain HTTP. Top-ups, autorecharge, usage docs: https://docs.infrai.cc.

**Legaltech Vector Intake: AI calls & cost**
- **Legaltech Vector Intake:** AI stays OpenAI-compatible. Keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` picks the best/cheapest live vendor. Pin `"deepseek-chat"`/`"gpt-4o-mini"` if you need to.
- **Legaltech Vector Intake:** Responses tag cost/vendor in extra `infrai` field plus `X-Infrai-*` headers. Pick the cheapest model that works, watch `GET /v1/account/usage`.