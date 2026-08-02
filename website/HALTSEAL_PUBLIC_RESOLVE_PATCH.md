# HALTSEAL Public Resolve Challenge — website implementation patch

## Target page

```text
https://meridianverity.com/haltseal/
```

## Surgical placement and product-language alignment

Keep the hero, primary product framing, and final buyer CTA unchanged. Apply the following **current-authority provenance micro-patch** inside the existing interactive instrument, then insert the developer proof surface after that instrument and before the buyer-hosted provider-route section.

### Current-authority provenance micro-patch

Primary label:

```text
Current authority
```

Provenance line:

```text
Derived from receiver policy and live state
```

Compact alternative where space is constrained:

```text
Receiver-derived · Current
```

Receipt/details coordinate:

```text
Policy
Purchase Control v3
```

The visible authority and final action must use the same material-field order:

```text
Amount · terms · merchant · destination
```

The canonical public demonstration remains:

```text
Authorized amount      $250.00
Terms                  ONE_TIME · exactly one authorized purchase
Merchant               Merchant Alpha
Destination            Account A
```

Only `terms` changes to `RECURRING_MONTHLY` in the changed-terms scene. The explanation should state that the proposed action **fails to align with every material field of current authority**.

## Developer proof surface

```html
<section id="developer-proof-surface" aria-labelledby="developer-proof-title">
  <p class="eyebrow">Developer proof surface</p>
  <h2 id="developer-proof-title">Call the same boundary over HTTP.</h2>
  <p>
    Submit one complete synthetic payment action against a server-issued authority challenge.
    HALTSEAL returns <code>ACCEPT</code>, <code>HOLD</code>, or <code>REFUSE</code> and a signed
    receipt you can verify independently.
  </p>
  <p class="proof-provenance">Receiver policy · short-lived permit · live state</p>
  <pre><code>POST /resolve
One complete synthetic action
One bounded decision
One signed receipt
No live provider call</code></pre>
  <div class="actions">
    <a class="button button-primary" href="https://eval.meridianverity.com/haltseal/evaluation/v1">Call the public challenge API</a>
    <a class="button" href="https://github.com/meridianverity/haltseal/tree/main/examples/curl">Copy the curl example</a>
    <a class="button" href="https://github.com/meridianverity/haltseal/tree/main/verifier">Verify a receipt</a>
    <a class="button" href="https://github.com/meridianverity/haltseal/blob/main/openapi/haltseal-public-resolve-v1.yaml">View the OpenAPI contract</a>
  </div>
  <p class="boundary-note">
    Synthetic evaluation · No payment credentials · No live provider request · No production or patent rights
  </p>
</section>
```

## Bridge to the existing buyer CTA

```html
<p>
  The public challenge proves the contract. A written-scope buyer evaluation substitutes one
  buyer-owned authority source and one protected provider boundary.
</p>
```

Retain:

```text
Bring one purchase or payout.
```

## Launch behavior

- hide or disable the primary hosted-API CTA until `/health/ready` passes;
- the GitHub curl, verifier, and OpenAPI links may be published independently;
- add `rel="noopener noreferrer"` to external links when opening a new tab;
- do not embed live receipt JWS values in analytics events;
- do not send action bodies, challenge tokens, or receipt contents to analytics;
- track only CTA category and aggregate success/error class.
