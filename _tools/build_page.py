# Inlines data/pokedex.json + data/sprites.json into pokedex/index.html (the published page) from template.html.
import os
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'pokedex')
src = open(os.path.join(D, 'template.html'), encoding='utf8').read()
def blob(name):
    return open(os.path.join(D, 'data', name), encoding='utf8').read().replace('</', '<\/')
tags = ('<script id="dexdata" type="application/json">%s</script>\n<script id="sprdata" type="application/json">%s</script>\n'
        '<script id="thumbdata" type="application/json">%s</script>\n') % (blob('pokedex.json'), blob('sprites.json'), blob('thumbs.json'))
import base64
font = base64.b64encode(open(os.path.join(D, 'fonts', 'Galmuri11.woff2'), 'rb').read()).decode()
face = ('<style>/* Galmuri11 by Minseo Lee, SIL Open Font License 1.1 */'
        '@font-face{font-family:"Galmuri11";src:url(data:font/woff2;base64,%s) format("woff2");font-display:swap}</style>\n' % font)
j = src.index('<style>')
src = src[:j] + face + src[j:]
i = src.index('<script>\n(function(){')
out = src[:i] + tags + src[i:]
open(os.path.join(D, 'index.html'), 'w', encoding='utf8').write(out)
print('pokedex/index.html', round(len(out.encode('utf8')) / 1e6, 2), 'MB')
