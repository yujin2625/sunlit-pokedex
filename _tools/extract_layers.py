# Extracts the Cobblemon-related game files of the Society Sunlit Cobblemon instance into guides/layers/.
# Each source becomes one layer folder; build_data.py / build_jobs.py stack them in load order.
import os, re, glob, zipfile, json, shutil

S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INST = os.path.dirname(S)
L = os.path.join(S, 'layers')

KEEP = re.compile(
    r'^(data/[^/]+/(species|species_additions|spawn_pool_world|spawn_detail_presets|species_features|species_feature_assignments|cosmetic_items)/'
    r'|data/[^/]+/tags/worldgen/biome/'
    r'|data/[^/]+/worldgen/biome/'
    r'|assets/[^/]+/lang/(en_us|ko_kr)\.json$'
    r'|assets/[^/]+/bedrock/(pokemon|species)/'
    r'|assets/[^/]+/textures/pokemon/)')

LAYERS = [
    ('00_cobblemon', 'mods/Sunlit_Cobblebackported-forge-*.jar'),
    ('01_integrations', 'mods/cobblemonintegrations-*.jar'),
    ('02_rocket', 'mods/rocket_mons-*.jar'),
    ('10_moveeffects', 'datapacks/Cobblemon Move Effects Backport*.zip'),
    ('11_celesteela', 'datapacks/literally_just_celesteela.zip'),
    ('12_sunlitmons', 'datapacks/sunlit-mons-*.zip'),
    ('13_bcg', 'resourcepacks/BCG x AllTheMons*.zip'),
]


def extract(name, src, keep=KEEP):
    out = os.path.join(L, name)
    shutil.rmtree(out, ignore_errors=True)
    z = zipfile.ZipFile(src)
    n = 0
    for f in z.namelist():
        if f.endswith('/') or not keep.match(f):
            continue
        dst = os.path.join(out, f)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, 'wb') as w:
            w.write(z.read(f))
        n += 1
    print(name, os.path.basename(src), n)


if __name__ == '__main__':
    os.makedirs(L, exist_ok=True)
    for name, pat in LAYERS:
        hits = glob.glob(os.path.join(INST, pat))
        if hits:
            extract(name, hits[0])
        else:
            print('missing', pat)
    # every other mod: lang files, biome tags and biome registry only (item names, biome names, tag resolution)
    other = re.compile(r'^(assets/[^/]+/lang/(en_us|ko_kr)\.json$|data/[^/]+/tags/worldgen/biome/|data/[^/]+/worldgen/biome/)')
    out = os.path.join(L, '30_modtags')
    shutil.rmtree(out, ignore_errors=True)
    ids = set()
    for jar in sorted(glob.glob(os.path.join(INST, 'mods', '*.jar'))):
        try:
            z = zipfile.ZipFile(jar)
        except Exception:
            continue
        try:
            ids |= set(re.findall(r'modId\s*=\s*"([^"]+)"', z.read('META-INF/mods.toml').decode('utf8', 'ignore')))
        except KeyError:
            pass
        sub = os.path.join(out, os.path.basename(jar)[:-4])
        for f in z.namelist():
            if f.endswith('/') or not other.match(f):
                continue
            dst = os.path.join(sub, f)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, 'wb') as w:
                w.write(z.read(f))
    open(os.path.join(S, '_tools', 'modids.txt'), 'w').write('\n'.join(sorted(ids)))
    print('mod ids', len(ids))
    # vanilla: en_us from the client jar, ko_kr from the asset index, biome tags from the jar
    vj = r'C:/Users/Dumaru/curseforge/minecraft/Install/versions/1.20.1/1.20.1.jar'
    extract('32_vanilla', vj, re.compile(r'^(assets/minecraft/lang/en_us\.json$|data/minecraft/tags/worldgen/biome/)'))
    idx = json.load(open(r'C:/Users/Dumaru/curseforge/minecraft/Install/assets/indexes/5.json'))['objects']
    h = idx['minecraft/lang/ko_kr.json']['hash']
    dst = os.path.join(L, '32_vanilla', 'assets', 'minecraft', 'lang', 'ko_kr.json')
    shutil.copy(os.path.join(r'C:/Users/Dumaru/curseforge/minecraft/Install/assets/objects', h[:2], h), dst)
    # kubejs (pack overrides: data + lang + textures)
    out = os.path.join(L, '40_kubejs')
    shutil.rmtree(out, ignore_errors=True)
    for sub in ('data', 'assets'):
        base = os.path.join(INST, 'kubejs', sub)
        for f in glob.glob(os.path.join(base, '**', '*'), recursive=True):
            rel = sub + '/' + os.path.relpath(f, base).replace('\\', '/')
            if os.path.isfile(f) and KEEP.match(rel):
                dst = os.path.join(out, rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy(f, dst)
    print('done')
