const base = process.env.HALTSEAL_BASE_URL || 'http://127.0.0.1:8787/haltseal/evaluation/v1';
async function post(path, body, headers={}) { const r=await fetch(base+path,{method:'POST',headers:{'content-type':'application/json',...headers},body:JSON.stringify(body)}); if(!r.ok) throw new Error(await r.text()); return r.json(); }
const challenge=await post('/challenges',{profile:'payment.one-time-purchase.v1'});
const result=await post('/resolve',{challenge_token:challenge.challenge_token,action:{amount_minor:25000,currency:'USD',merchant_id:'merchant_synthetic_alpha',terms:'ONE_TIME',destination_id:'account_synthetic_a'}},{'Idempotency-Key':'typescript-public-example-0001'});
console.log(JSON.stringify(result,null,2));
