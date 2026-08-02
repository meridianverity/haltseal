#!/usr/bin/env node
import fs from 'node:fs';
import crypto from 'node:crypto';

const ISSUER='https://eval.meridianverity.com';
const AUDIENCE='haltseal-public-receipt';
const PROFILE_VERSION='haltseal-public-resolve-1';
const RECEIPT_TYP='HALTSEAL-EVAL-RECEIPT+jws';
const BOUNDARY={
  synthetic:true,
  live_provider_call:false,
  payment_credentials_accepted:false,
  production_rights:false,
  patent_license_granted:false,
  profile_version:PROFILE_VERSION,
};

class StrictParser {
  constructor(text) { this.t=text; this.i=0; }
  parse() { const v=this.value(); this.ws(); if(this.i!==this.t.length) throw new Error('trailing JSON data'); return v; }
  ws(){ while(this.i<this.t.length && /[\x20\t\r\n]/.test(this.t[this.i])) this.i++; }
  value(){ this.ws(); const c=this.t[this.i]; if(c==='{') return this.object(); if(c==='[') return this.array(); if(c==='"') return this.string(); if(c==='t') return this.literal('true',true); if(c==='f') return this.literal('false',false); if(c==='n') return this.literal('null',null); if(c==='-' || /[0-9]/.test(c)) return this.number(); throw new Error('invalid JSON value'); }
  literal(s,v){ if(this.t.slice(this.i,this.i+s.length)!==s) throw new Error('invalid literal'); this.i+=s.length; return v; }
  string(){ const start=this.i++; let esc=false; while(this.i<this.t.length){ const c=this.t[this.i++]; if(esc){ esc=false; continue; } if(c==='\\'){ esc=true; continue; } if(c==='"'){ return JSON.parse(this.t.slice(start,this.i)); } if(c<' ') throw new Error('control character in string'); } throw new Error('unterminated string'); }
  number(){ const start=this.i; if(this.t[this.i]==='-') this.i++; if(this.t[this.i]==='0') this.i++; else { if(!/[1-9]/.test(this.t[this.i])) throw new Error('invalid number'); while(/[0-9]/.test(this.t[this.i])) this.i++; } if(this.t[this.i]==='.' || this.t[this.i]==='e' || this.t[this.i]==='E') throw new Error('floating-point JSON is outside the public profile'); const n=Number(this.t.slice(start,this.i)); if(!Number.isSafeInteger(n)) throw new Error('unsafe integer'); return n; }
  object(){ this.i++; const out={}; const keys=new Set(); this.ws(); if(this.t[this.i]==='}'){this.i++; return out;} while(true){ this.ws(); if(this.t[this.i]!== '"') throw new Error('object key must be string'); const k=this.string(); if(keys.has(k)) throw new Error(`duplicate JSON member: ${k}`); keys.add(k); this.ws(); if(this.t[this.i++]!==':') throw new Error('missing colon'); out[k]=this.value(); this.ws(); const c=this.t[this.i++]; if(c==='}') return out; if(c!==',') throw new Error('invalid object delimiter'); } }
  array(){ this.i++; const out=[]; this.ws(); if(this.t[this.i]===']'){this.i++; return out;} while(true){ out.push(this.value()); this.ws(); const c=this.t[this.i++]; if(c===']') return out; if(c!==',') throw new Error('invalid array delimiter'); } }
}
const strictParse = text => new StrictParser(text).parse();
const encodeB64u = bytes => Buffer.from(bytes).toString('base64').replace(/=/g,'').replace(/\+/g,'-').replace(/\//g,'_');
function decodeB64uCanonical(s){
  if(typeof s!=='string' || !/^[A-Za-z0-9_-]+$/.test(s) || s.length%4===1) throw new Error('base64url segment is not canonical unpadded base64url');
  const decoded=Buffer.from(s.replace(/-/g,'+').replace(/_/g,'/')+'='.repeat((4-s.length%4)%4),'base64');
  if(encodeB64u(decoded)!==s) throw new Error('base64url segment is not canonical');
  return decoded;
}
const canonical = v => {
  if(v===null || typeof v==='boolean' || Number.isSafeInteger(v)) return JSON.stringify(v);
  if(typeof v==='string'){ if(!/^[\x20-\x7e]+$/.test(v)) throw new Error('non-ASCII value outside public profile'); return JSON.stringify(v); }
  if(Array.isArray(v)) return '['+v.map(canonical).join(',')+']';
  if(typeof v==='object') return '{'+Object.keys(v).sort().map(k=>JSON.stringify(k)+':'+canonical(v[k])).join(',')+'}';
  throw new Error('unsupported canonical type');
};
const digest = (ctx,v) => 'sha256:'+crypto.createHash('sha256').update(ctx+'\0'+canonical(v),'ascii').digest('hex');
function exactKeys(o, keys, label){ if(!o || typeof o!=='object' || Array.isArray(o)) throw new Error(`${label} must be object`); const a=Object.keys(o).sort(), b=[...keys].sort(); if(JSON.stringify(a)!==JSON.stringify(b)) throw new Error(`${label} field set mismatch`); }
function exactString(v,re,label){ if(typeof v!=='string'||!re.test(v)) throw new Error(`${label} is invalid`); return v; }
function exactInteger(v,min,max,label){ if(!Number.isSafeInteger(v)||v<min||v>max) throw new Error(`${label} is invalid`); return v; }
function deepEqual(a,b){ return canonical(a)===canonical(b); }

const ACTION_FIELDS=new Set(['amount_minor','currency','merchant_id','terms','destination_id']);
const AUTHORITY_FIELDS=new Set(['authorized_amount_minor','currency','merchant_id','terms','destination_id','remaining_uses','status']);
const RECEIPT_FIELDS=new Set(['iss','aud','jti','iat','profile_version','challenge_id','authority','authority_digest','action','action_digest','decision','reason_codes','emission','consumption','boundary']);
const EMISSION_FIELDS=new Set(['disposition','synthetic_request_record_id','existing_request_record_id','new_request_count','total_request_count_for_use','outcome']);
const CONSUMPTION_FIELDS=new Set(['state_before','state_after']);
const BOUNDARY_FIELDS=new Set(['synthetic','live_provider_call','payment_credentials_accepted','production_rights','patent_license_granted','profile_version']);
const ID=/^[a-z][a-z0-9_]{2,79}$/;
const RECEIPT_ID=/^hsr_[a-z0-9_]{8,80}$/;
const CHALLENGE_ID=/^hsc_[a-z0-9_]{8,80}$/;
const REQUEST_ID=/^hsreq_[a-z0-9_]{8,80}$/;
const DIGEST=/^sha256:[0-9a-f]{64}$/;
const REASON=/^[A-Z0-9_]{3,64}$/;

function validateAction(a){
  exactKeys(a,ACTION_FIELDS,'action');
  exactInteger(a.amount_minor,1,100000,'amount_minor');
  if(a.currency!=='USD') throw new Error('currency must be USD');
  if(!['merchant_synthetic_alpha','merchant_synthetic_beta'].includes(a.merchant_id)) throw new Error('merchant_id outside synthetic universe');
  if(!['ONE_TIME','RECURRING_MONTHLY'].includes(a.terms)) throw new Error('terms outside synthetic universe');
  if(!['account_synthetic_a','account_synthetic_b'].includes(a.destination_id)) throw new Error('destination_id outside synthetic universe');
  return a;
}
function validateAuthority(a){
  exactKeys(a,AUTHORITY_FIELDS,'authority');
  exactInteger(a.authorized_amount_minor,1,100000,'authorized_amount_minor');
  exactInteger(a.remaining_uses,0,1,'remaining_uses');
  if(!['CURRENT','REVOKED'].includes(a.status)) throw new Error('authority status invalid');
  validateAction({amount_minor:a.authorized_amount_minor,currency:a.currency,merchant_id:a.merchant_id,terms:a.terms,destination_id:a.destination_id});
  return a;
}
function validateBoundary(b){ exactKeys(b,BOUNDARY_FIELDS,'boundary'); if(!deepEqual(b,BOUNDARY)) throw new Error('boundary mismatch'); }
function validateRequestId(v,label){ if(v===null) return null; return exactString(v,REQUEST_ID,label); }
function validateReceiptProfile(p){
  exactKeys(p,RECEIPT_FIELDS,'receipt');
  if(p.iss!==ISSUER||p.aud!==AUDIENCE||p.profile_version!==PROFILE_VERSION) throw new Error('receipt profile mismatch');
  exactString(p.jti,RECEIPT_ID,'receipt jti');
  exactInteger(p.iat,0,Number.MAX_SAFE_INTEGER,'receipt iat');
  exactString(p.challenge_id,CHALLENGE_ID,'challenge_id');
  exactString(p.authority_digest,DIGEST,'authority_digest');
  exactString(p.action_digest,DIGEST,'action_digest');
  if(!['ACCEPT','HOLD','REFUSE'].includes(p.decision)) throw new Error('decision invalid');
  if(!Array.isArray(p.reason_codes)||p.reason_codes.length<1||p.reason_codes.some(v=>typeof v!=='string'||!REASON.test(v))||new Set(p.reason_codes).size!==p.reason_codes.length) throw new Error('reason_codes invalid');
  validateBoundary(p.boundary); validateAuthority(p.authority); validateAction(p.action);
  exactKeys(p.emission,EMISSION_FIELDS,'emission'); exactKeys(p.consumption,CONSUMPTION_FIELDS,'consumption');
  const e=p.emission,c=p.consumption;
  if(!['ONE_SYNTHETIC_REQUEST','NO_REQUEST','NO_NEW_REQUEST'].includes(e.disposition)) throw new Error('emission disposition invalid');
  if(!['RECORDED','NONE','UNKNOWN'].includes(e.outcome)) throw new Error('emission outcome invalid');
  const sid=validateRequestId(e.synthetic_request_record_id,'synthetic_request_record_id');
  const xid=validateRequestId(e.existing_request_record_id,'existing_request_record_id');
  exactInteger(e.new_request_count,0,1,'new_request_count'); exactInteger(e.total_request_count_for_use,0,1,'total_request_count_for_use');
  if(!['AVAILABLE','CONSUMED'].includes(c.state_before)||!['AVAILABLE','CONSUMED'].includes(c.state_after)) throw new Error('consumption state invalid');
  if(p.decision==='ACCEPT'){
    if(sid===null||!deepEqual(e,{disposition:'ONE_SYNTHETIC_REQUEST',synthetic_request_record_id:sid,existing_request_record_id:null,new_request_count:1,total_request_count_for_use:1,outcome:'RECORDED'})) throw new Error('ACCEPT emission invariant failed');
    if(!deepEqual(c,{state_before:'AVAILABLE',state_after:'CONSUMED'})) throw new Error('ACCEPT consumption invariant failed');
  } else if(p.decision==='HOLD'){
    if(xid===null||!deepEqual(e,{disposition:'NO_NEW_REQUEST',synthetic_request_record_id:null,existing_request_record_id:xid,new_request_count:0,total_request_count_for_use:1,outcome:'UNKNOWN'})) throw new Error('HOLD emission invariant failed');
    if(!deepEqual(c,{state_before:'CONSUMED',state_after:'CONSUMED'})) throw new Error('HOLD consumption invariant failed');
  } else {
    if(c.state_before!==c.state_after) throw new Error('REFUSE consumption must not change state');
    const total=c.state_before==='CONSUMED'?1:0;
    if(!deepEqual(e,{disposition:'NO_REQUEST',synthetic_request_record_id:null,existing_request_record_id:null,new_request_count:0,total_request_count_for_use:total,outcome:'NONE'})) throw new Error('REFUSE emission invariant failed');
  }
  return {authority:p.authority,action:p.action,emission:e,consumption:c};
}
function evaluate(auth,a,unknown,consumed){ if(unknown) return ['HOLD',['PROVIDER_OUTCOME_UNKNOWN'],'NO_NEW_REQUEST']; if(auth.status==='REVOKED') return ['REFUSE',['AUTHORITY_REVOKED'],'NO_REQUEST']; if(consumed || auth.remaining_uses===0) return ['REFUSE',['AUTHORIZED_USE_ALREADY_CONSUMED'],'NO_REQUEST']; const r=[]; if(a.amount_minor!==auth.authorized_amount_minor)r.push('AMOUNT_MISMATCH'); if(a.currency!==auth.currency)r.push('CURRENCY_MISMATCH'); if(a.merchant_id!==auth.merchant_id)r.push('MERCHANT_MISMATCH'); if(a.terms!==auth.terms)r.push('TERMS_MISMATCH'); if(a.destination_id!==auth.destination_id)r.push('DESTINATION_MISMATCH'); return r.length?['REFUSE',r,'NO_REQUEST']:['ACCEPT',['AUTHORITY_CURRENT','ACTION_EXACT','USE_AVAILABLE'],'ONE_SYNTHETIC_REQUEST']; }
async function verifyReceipt(token,jwks){
  if(typeof token!=='string' || token.trim()!==token) throw new Error('compact JWS must not contain surrounding whitespace');
  const parts=token.split('.'); if(parts.length!==3) throw new Error('compact JWS must have three segments');
  const headerText=decodeB64uCanonical(parts[0]).toString('utf8'), payloadText=decodeB64uCanonical(parts[1]).toString('utf8');
  const h=strictParse(headerText), p=strictParse(payloadText); exactKeys(h,new Set(['alg','kid','typ']),'header');
  if(h.alg!=='EdDSA'||h.typ!==RECEIPT_TYP||typeof h.kid!=='string'||h.kid.length===0) throw new Error('header profile mismatch');
  exactKeys(jwks,new Set(['keys']),'JWKS'); if(!Array.isArray(jwks.keys)) throw new Error('JWKS keys missing');
  const matches=jwks.keys.filter(k=>k&&typeof k==='object'&&!Array.isArray(k)&&k.kid===h.kid); if(matches.length!==1) throw new Error('kid must resolve once');
  const jwk=matches[0]; exactKeys(jwk,new Set(['kty','crv','x','kid','use','alg']),'JWK'); if(jwk.kty!=='OKP'||jwk.crv!=='Ed25519'||jwk.use!=='sig'||jwk.alg!=='EdDSA') throw new Error('unsupported JWK'); decodeB64uCanonical(jwk.x);
  const key=await crypto.webcrypto.subtle.importKey('jwk',jwk,{name:'Ed25519'},false,['verify']);
  const ok=await crypto.webcrypto.subtle.verify('Ed25519',key,decodeB64uCanonical(parts[2]),Buffer.from(parts[0]+'.'+parts[1],'ascii')); if(!ok) throw new Error('invalid signature');
  const {authority,action,emission,consumption}=validateReceiptProfile(p);
  if(p.action_digest!==digest('HALTSEAL-ACTION-CJ-1',action)) throw new Error('action digest mismatch');
  if(p.authority_digest!==digest('HALTSEAL-AUTHORITY-CJ-1',authority)) throw new Error('authority digest mismatch');
  const unknown=p.decision==='HOLD'; const consumed=p.decision==='REFUSE'&&consumption.state_before==='CONSUMED';
  const [d,reasons,disp]=evaluate(authority,action,unknown,consumed); if(p.decision!==d||JSON.stringify(p.reason_codes)!==JSON.stringify(reasons)||emission.disposition!==disp) throw new Error('semantic replay mismatch');
  return {signature:'VALID',semantic_replay:'PASS',decision:p.decision,reason_codes:p.reason_codes,action_digest:p.action_digest,authority_digest:p.authority_digest,emission,receipt_id:p.jti,profile_version:p.profile_version};
}
if(process.argv.length<4){ console.error('usage: node haltseal_verify.mjs RECEIPT.jws JWKS.json'); process.exit(2); }
try { const token=fs.readFileSync(process.argv[2],'utf8').trimEnd(); const jwks=strictParse(fs.readFileSync(process.argv[3],'utf8')); console.log(JSON.stringify(await verifyReceipt(token,jwks),null,2)); }
catch(e){ console.error(JSON.stringify({signature:'INVALID',semantic_replay:'FAIL',error:String(e.message||e)},null,2)); process.exit(1); }
