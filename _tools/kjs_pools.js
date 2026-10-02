// Pulls the Pokémon fishing and Gachamon capsule pools out of the pack's KubeJS scripts as JSON.
// usage: node kjs_pools.js <instance dir>  -> prints {fish, netherFish, gachaBase, gachaSpecial}
const fs = require('fs'), path = require('path');
const inst = process.argv[2];
const read = p => fs.readFileSync(path.join(inst, 'kubejs', p), 'utf8');

// returns the source text of the bracketed literal that starts right after `marker`
function literal(src, marker) {
  const i = src.indexOf(marker);
  if (i < 0) throw new Error('marker not found: ' + marker);
  let j = i + marker.length;
  while (src[j] !== '[' && src[j] !== '(') j++;
  const open = src[j], close = open === '[' ? ']' : ')';
  let depth = 0, k = j, str = null;
  for (; k < src.length; k++) {
    const c = src[k];
    if (str) { if (c === '\\') { k++; continue; } if (c === str) str = null; continue; }
    if (c === '"' || c === "'" || c === '`') { str = c; continue; }
    if (c === '/' && src[k + 1] === '/') { k = src.indexOf('\n', k); continue; }
    if (c === open) depth++;
    else if (c === close && --depth === 0) break;
  }
  return src.slice(j, k + 1);
}
const ev = s => Function('"use strict";return (' + s + ');')();

const fishSrc = read('startup_scripts/cobblemon/cobblemonFishingPool.js');
const gachaSrc = read('server_scripts/cobblemon/cobblemonGachaPools.js');
const out = {
  fish: ev(literal(fishSrc, 'global.cobblemonFishPool =')),
  netherFish: ev(literal(fishSrc, 'global.cobblemonNetherFishPool =')),
  gachaBase: ev(literal(gachaSrc, 'let baseGachaSpawns =')),
  gachaSpecial: ev('new Map' + literal(gachaSrc, 'const specialGachaSpawns = new Map')),
};
out.gachaSpecial = Object.fromEntries(out.gachaSpecial);
process.stdout.write(JSON.stringify(out));
