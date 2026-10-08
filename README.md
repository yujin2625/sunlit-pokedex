# Sunlit Guides

Static guide pages for the **Society Sunlit Cobblemon** Minecraft modpack (1.1.4, Forge 1.20.1, Cobblemon 1.5.2 backport).

- **Main page:** `index.html`. Pick a guide; EN/KO toggle (shared with the Pokédex).
- **Pokédex:** `pokedex/index.html`. 1,000 Pokémon, bilingual (EN default, KO switch), with in-game model renders, wild spawns, Poké fishing pools, Gachamon Capsule sets, pack-specific legendary methods, evolutions, breeding partners, shiny odds, stars and custom lists (saved in the browser).

Published with GitHub Pages from the `main` branch root.

## Rebuilding

All scripts live in `_tools/` and expect this folder to sit inside the instance as `guides/`.

```
python _tools/extract_layers.py   # game files -> layers/ (mod jars, datapacks/, resourcepacks/, kubejs/)
python _tools/build_data.py       # -> pokedex/data/pokedex.json (needs node for the KubeJS fishing/gacha pools)
python _tools/build_jobs.py       # -> _tools/jobs.json (model/texture/pose per species, form, shiny)
python _tools/server.py 8765      # then open http://localhost:8765/render.html?skipdone=1 (add &of=3&shard=0..2 for parallel tabs)
python _tools/build_atlas.py      # _tools/out/*.png -> pokedex/sprites/*.webp + data/sprites.json + data/thumbs.json
python _tools/build_page.py       # template.html + data -> pokedex/index.html
```

Edit `pokedex/template.html`, never `pokedex/index.html`.

Load order used for data: Cobblemon backport jar < integrations < rocket_mons < datapacks/ (Move Effects, Celesteela, sunlit-mons) < BCG x AllTheMons < kubejs/data. Assets follow `config/resourcepackoverrides.json`. `_tools/special_methods.json` holds the KubeJS legendary/event methods shown under "Special ways to get it".

## Credits

- Pokémon and Pokémon names © Nintendo / Creatures Inc. / GAME FREAK inc. This is an unofficial fan project, not affiliated with or endorsed by Nintendo, The Pokémon Company, GAME FREAK or the Cobblemon team.
- Models, textures and data come from Cobblemon and the mods, datapacks and resource packs bundled in the modpack, rendered for reference. All game assets (sprites in `pokedex/sprites`, `pokedex/data/thumbs.json`) remain the property of their respective owners and will be removed on request.
- Font: [Galmuri](https://github.com/quiple/galmuri) by Lee Minseo, SIL Open Font License 1.1 (`pokedex/fonts/OFL.md`). DotGothic16 and Silkscreen are loaded from Google Fonts.
- Page design follows [mayview-pokedex](https://github.com/yujin2625/mayview-pokedex).

## License

The code in this repository is licensed under [PolyForm Noncommercial 1.0.0](LICENSE.md): noncommercial use, modification and redistribution are allowed, commercial use is not, and redistributions must keep the `Required Notice` line and the license terms. Game assets (Pokémon sprites, models, textures and data) are not covered by this license; see Credits above.
