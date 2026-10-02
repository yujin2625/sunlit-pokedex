# Resolves render jobs (model/texture/layers/pose) for every species/form, normal and shiny -> _tools/jobs.json
import json, os, re, glob, collections

T = os.path.dirname(os.path.abspath(__file__))
S = os.path.dirname(T)
L = os.path.join(S, 'layers')
DEX = json.load(open(os.path.join(S, 'pokedex', 'data', 'pokedex.json'), encoding='utf8'))

# asset roots, low -> high priority (mod jars, then resourcepackoverrides.json order, then KubeJS)
ROOTS = ['00_cobblemon', '01_integrations', '02_rocket', '13_bcg', '11_celesteela', '10_moveeffects', '12_sunlitmons', '40_kubejs']
ASSET = {}
for r in ROOTS:
    base = os.path.join(L, r, 'assets')
    for f in glob.glob(os.path.join(base, '*', '**', '*'), recursive=True):
        if os.path.isfile(f):
            ASSET[os.path.relpath(f, base).replace('\\', '/')] = os.path.relpath(f, L).replace('\\', '/')
print('assets', len(ASSET))


def loc(rid):
    ns, _, p = rid.partition(':')
    if not p:
        ns, p = 'cobblemon', ns
    return ns + '/' + p


def jread(full):
    t = open(os.path.join(L, full), encoding='utf-8-sig').read()
    try:
        return json.loads(t)
    except Exception:
        t = re.sub(r'(?<![:"])//.*$', '', t, flags=re.M)
        t = re.sub(r',(\s*[}\]])', r'\1', t)
        return json.loads(t)

MODELS, POSERS, RESOLVERS = {}, {}, collections.defaultdict(list)
for rel, full in ASSET.items():
    m = re.match(r'^([^/]+)/bedrock/pokemon/models/(?:.+/)?([^/]+)\.json$', rel)
    if m:
        MODELS[m.group(1) + ':' + m.group(2)] = full
        continue
    m = re.match(r'^([^/]+)/bedrock/pokemon/posers/(?:.+/)?([^/]+)\.json$', rel)
    if m:
        POSERS[m.group(1) + ':' + m.group(2)] = full
        continue
    if re.match(r'^[^/]+/bedrock/(pokemon/resolvers|species)/.+\.json$', rel):
        try:
            j = jread(full)
        except Exception as e:
            print('bad resolver', full, e); continue
        RESOLVERS[j.get('species', '').split(':')[-1]].append(j)

ANIMS = {}
for rel, full in ASSET.items():
    if re.match(r'^[^/]+/bedrock/pokemon/animations/.+\.json$', rel):
        try:
            j = jread(full)
        except Exception:
            continue
        for k in (j.get('animations') or {}):
            ANIMS[k] = full
print('models', len(MODELS), 'posers', len(POSERS), 'resolver species', len(RESOLVERS), 'anims', len(ANIMS))


def tex_first(t):
    if isinstance(t, dict):
        fr = t.get('frames') or []
        return fr[0] if fr else None
    return t


def resolve(sp, aspects):
    A = set(aspects)
    res = {'poser': None, 'model': None, 'texture': None, 'layers': []}
    for r in sorted(RESOLVERS.get(sp, []), key=lambda r: r.get('order', 0)):
        for v in r.get('variations', []):
            if set(v.get('aspects', [])) <= A:
                for k in ('poser', 'model', 'texture'):
                    if v.get(k):
                        res[k] = v[k]
                if 'layers' in v:
                    res['layers'] = v['layers']
    return res


def idle_anims(name):
    """Cobblemon 1.5 keeps most posers in code; they stand in animation.<name>.ground_idle."""
    for suf in ('ground_idle', 'idle', 'ground_walk', 'water_idle', 'air_idle', 'hover', 'float'):
        aid = 'animation.%s.%s' % (name, suf)
        if aid in ANIMS:
            return [{'id': aid, 'f': ANIMS[aid]}]
    return []


def pose_for(poser_id):
    pid = poser_id if ':' in poser_id else 'cobblemon:' + poser_id
    f = POSERS.get(pid)
    name = pid.split(':')[-1]
    if not f:
        return idle_anims(name), []
    try:
        j = jread(f)
    except Exception as e:
        print('bad poser', f, e)
        return idle_anims(name), []
    poses = j.get('poses') or {}
    pick = None
    for want in ('PROFILE', 'PORTRAIT', 'STAND', 'NONE'):
        for pn, p in poses.items():
            if want in (p.get('poseTypes') or []) and not p.get('isBattle') and not p.get('isTouchingWater'):
                pick = p; break
        if pick:
            break
    if not pick and poses:
        pick = list(poses.values())[0]
    anims = []
    al = (pick or {}).get('animations', []) or []
    if isinstance(al, dict):
        al = list(al.values())
    for a in al:
        a = a if isinstance(a, str) else json.dumps(a)
        m = re.search(r"bedrock\(\s*'?\"?([\w\-]+)'?\"?\s*,\s*'?\"?([\w\-\.]+)'?\"?", a)
        if m:
            aid = 'animation.%s.%s' % (m.group(1), m.group(2))
            if aid in ANIMS:
                anims.append({'id': aid, 'f': ANIMS[aid]})
    return anims or idle_anims(name), (pick or {}).get('transformedParts', [])


def job(sp, name, aspects):
    r = resolve(sp, aspects)
    if not r['model']:
        return None
    mid = r['model'] if ':' in r['model'] else 'cobblemon:' + r['model']
    mfile = MODELS.get(mid) or MODELS.get(mid.replace('.geo', '') + '.geo') or MODELS.get(mid + '.geo')
    tex = ASSET.get(loc(tex_first(r['texture']))) if r['texture'] else None
    if not mfile or not tex:
        return None
    layers = []
    for ly in r['layers'] or []:
        t = ly.get('texture') and ASSET.get(loc(tex_first(ly.get('texture'))))
        if t:
            layers.append({'t': t, 'e': 1 if ly.get('emissive') else 0, 'tr': 1 if ly.get('translucent') else 0})
    anims, tparts = pose_for(r['poser'] or sp)
    return {'id': name, 'model': mfile, 'tex': tex, 'layers': layers, 'anims': anims or [], 'tparts': tparts or [], 'key': (mfile, tex, tuple(l['t'] for l in layers))}

jobs, missing = [], []
for p in DEX['pokemon']:
    sp = p['id']
    g = [] if p.get('mr') == -1 else (['female'] if p.get('mr') == 0 else ['male'])
    variants = [('', [])] + [('__' + fo['slug'], list(fo['asp'])) for fo in p.get('forms', [])]
    base_key = None
    for suffix, asp in variants:
        for shiny in (False, True):
            name = sp + suffix + ('__shiny' if shiny else '')
            j = job(sp, name, g + asp + (['shiny'] if shiny else []))
            if not j:
                missing.append(name); continue
            if suffix and not shiny and base_key and j['key'] == base_key:
                break  # form looks identical to base
            if not suffix and not shiny:
                base_key = j['key']
            jobs.append(j)
for j in jobs:
    del j['key']
json.dump(jobs, open(os.path.join(T, 'jobs.json'), 'w'), separators=(',', ':'))
print('jobs', len(jobs), 'missing', len(missing), 'base missing', [m for m in missing if '__' not in m])
