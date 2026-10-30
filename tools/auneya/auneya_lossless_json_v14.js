'use strict';
const { TextDecoder } = require('node:util');
const SAFE = BigInt(Number.MAX_SAFE_INTEGER);
const MAX_DEPTH = 64;
const MAX_TOKENS = 250000;

function parseLossless(raw) {
  if (!Buffer.isBuffer(raw) || raw.length > 3 * 1024 * 1024)
    throw Error('expected bounded bytes');
  const s = new TextDecoder('utf-8', {fatal: true}).decode(raw);
  let i = 0, tokens = 0;
  const fail = why => { throw Error('JSON rejected: ' + why + ' at ' + i); };
  const ws = () => { while (i < s.length && /[\x20\x09\x0a\x0d]/.test(s[i])) i++; };
  function string() {
    if (s[i] !== '"') fail('string expected');
    const start = i++;
    let closed = false;
    while (i < s.length) {
      const c = s.charCodeAt(i++);
      if (c === 34) {closed = true; break;}
      if (c < 32) fail('control character');
      if (c === 92) {
        if (i >= s.length) fail('unterminated escape');
        i++;
      }
    }
    if (!closed) fail('unterminated string');
    try {return JSON.parse(s.slice(start, i));}
    catch (_) {return fail('invalid string');}
  }
  function value(depth) {
    if (++tokens > MAX_TOKENS || depth > MAX_DEPTH) fail('resource budget');
    ws();
    if (s[i] === '"') return string();
    if (s[i] === '[') {
      i++; const a=[]; ws();
      if (s[i] === ']') {i++; return a;}
      while (true) {
        a.push(value(depth+1)); ws();
        if (s[i] === ']') {i++; return a;}
        if (s[i++] !== ',') fail('array separator');
      }
    }
    if (s[i] === '{') {
      i++; const o=Object.create(null); ws();
      if (s[i] === '}') {i++; return o;}
      while (true) {
        ws(); const key=string(); ws();
        if (s[i++] !== ':') fail('object separator');
        if (Object.hasOwn(o,key)) fail('duplicate JSON key');
        o[key]=value(depth+1); ws();
        if (s[i] === '}') {i++; return o;}
        if (s[i++] !== ',') fail('object delimiter');
      }
    }
    for (const [word, v] of [['true',true],['false',false],['null',null]]) {
      if (s.startsWith(word,i)) {i += word.length; return v;}
    }
    const match = /^-?(?:0|[1-9][0-9]*)/.exec(s.slice(i));
    if (!match) fail('unexpected token');
    i += match[0].length;
    if (match[0].length > 8192 || /[.eE0-9]/.test(s[i] || '')) fail('number syntax or size');
    const n = BigInt(match[0]);
    return n >= -SAFE && n <= SAFE ? Number(n) : n;
  }
  const result=value(0); ws();
  if (i !== s.length) fail('trailing data');
  return result;
}
module.exports={parseLossless};
