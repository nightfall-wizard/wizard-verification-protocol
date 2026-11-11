#!/usr/bin/env python3
"""Bounded AUNEYA wire research; no device, audit or network claim."""
import argparse,hashlib,hmac,json,re,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/auneya'))
import auneya_capsule_v112 as cap
import auneya_gate4_bundle_v118 as baseline
import auneya_gate4_adversarial_v119 as attacks
S=R/'schemas/auneya-capsule-wire-v1.20.schema.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
def need(ok,msg):
    if not ok:raise ValueError(msg)
def shape(v,s,root):
    if '$ref' in s:
        need(set(s)=={'$ref'} and s['$ref'].startswith('#/$defs/'),
             'invalid schema ref')
        return shape(v,root['$defs'][s['$ref'][8:]],root)
    if 'oneOf' in s:
        matched=0
        for item in s['oneOf']:
            try:shape(v,item,root);matched+=1
            except ValueError:pass
        need(matched==1,'oneOf');return
    t={'object':dict,'array':list,'integer':int,
       'string':str,'null':type(None)}
    if 'type' in s:need(type(v)==t[s['type']],'wrong type')
    if 'const' in s:need(v==s['const'],'wrong format')
    if type(v)==int:
        need(s.get('minimum',v)<=v<=s.get('maximum',v),'integer bound')
    if type(v)==str:
        need(s.get('minLength',0)<=len(v)<=s.get('maxLength',len(v)),
             'string bound')
        if 'pattern' in s:
            need(re.fullmatch(s['pattern'],v)!=None,'string pattern')
    if type(v)==dict:
        need(set(s.get('required',[]))<=set(v),'missing field')
        if s.get('additionalProperties') is False:
            need(set(v)<=set(s['properties']),'extra field')
        for k in v:
            if k in s.get('properties',{}):shape(v[k],s['properties'][k],root)
    if type(v)==list:
        need(s.get('minItems',0)<=len(v)<=s.get('maxItems',len(v)),
             'list size')
        for i in v:shape(i,s['items'],root)
def profile(file):
    sc=baseline.secure_read(S,32768)
    schema=json.loads(sc,object_pairs_hook=baseline.unique)
    need(schema['$schema']=='https://json-schema.org/draft/2020-12/schema'
         and schema['$id'].endswith('/schemas/auneya-capsule-wire-v1.20.schema.json'),
         'schema identity')
    raw=baseline.secure_read(file,3*1024*1024)
    obj=cap.strict_bytes(raw)
    shape(obj,schema,schema)
    for item in (obj['current'],obj['previous']):
        if item is None:continue
        pins=[x['pin'] for x in item['receipts']]
        need(pins==sorted(set(pins)),'keeper pins')
        cap.strict_bytes(cap.decoded(item['anchor_b64'],1024*1024))
        for receipt in item['receipts']:
            cap.strict_bytes(cap.decoded(receipt['payload_b64'],16*1024))
    return raw,sha(sc)
def build(trust,file,expected):
    need(re.fullmatch('[0-9a-f]{64}',expected)!=None,
         'external digest required')
    raw,schemahash=profile(file)
    need(hmac.compare_digest(sha(raw),expected),'digest mismatch')
    result=attacks.run(trust,file,expected)
    need(result['cases_passed']==15 and
         result['python_verified'] and result['node_verified'],
         'dual runtime campaign failed')
    need(profile(file)==(raw,schemahash),'input changed')
    return baseline.json_canonical({
        'format':'auneya-wire-conformance-v1.20',
        'schema_sha256':schemahash,'capsule_sha256':expected,
        'campaign_sha256':sha(baseline.json_canonical(result)),
        'negative_vectors_passed':15,'python_verified':True,
        'node_verified':True,'non_value_research_only':True,
        'independent_devices_proven':False,'external_retention_proven':False,
        'independent_audit_completed':False,'mainnet_active':False,
        'economic_activation':False})
def main():
    p=argparse.ArgumentParser()
    p.add_argument('action',choices=('create','verify'))
    for name in ('trust','capsule','expected'):
        p.add_argument('--'+name,required=True)
    p.add_argument('--output');p.add_argument('--input')
    a=p.parse_args()
    raw=build(a.trust,a.capsule,a.expected)
    if a.action=='create':
        if a.output:baseline.secure_write(a.output,raw)
        sys.stdout.buffer.write(raw)
    else:
        need(a.input,'--input required')
        need(hmac.compare_digest(baseline.secure_read(a.input,65536),raw),
             'report differs')
        print('PASS: wire profile, real Ed25519, Python/Node adversaries')
if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,TypeError,OSError,RuntimeError) as e:
        sys.exit('REJECTED: '+str(e))
