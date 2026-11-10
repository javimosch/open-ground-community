# Content packs (DLCs and community mods)

A content pack adds factions, catalogue types, scenarios, campaigns and briefings to the game without touching its
code or its own files. Official packs are DLCs (`dlc/<id>/`); community packs are mods (`mods/<author>.<name>/`, sim
ABI 92). Both use the same format. The first DLC is `dlc/malvinas` (Las Malvinas, a draft). Sim ABI 60.

## Format rules (the modding contract, ABI 92)

These rules are the public modding surface. Keep them stable: a change that breaks existing packs bumps
`format_version`.

1. **Two kinds.** `"kind": "dlc"` (the default: official, shipped by us, in `dlc/<id>/`) or `"kind": "mod"` (community,
   in `mods/<id>/`). The folder name is the pack id.
2. **Ids and namespaces.**
   - A DLC id is 1-40 characters of `a-z`, `0-9` and `_` (`malvinas`). Its factions and types use a short prefix
     by convention (`mal_uk`, `mal_church`).
   - A mod id is `<author>.<name>`, each part of `a-z`, `0-9` and `_`, 64 characters at most (`jdoe.desert_ops`).
   - Everything a mod adds is named `<id>.<name>`: factions `jdoe.desert_ops.raiders`, catalogue types
     `jdoe.desert_ops.barrels`. Anything else refuses the whole mod. So mods never clash with the game, with the
     DLCs or with each other.
   - Nothing may reuse an id that is already loaded (built-in, a DLC's or a mod's): the pack is refused whole.
3. **Data only.** A pack is JSON and assets. There is no code, no script and no path outside its folder (`..`,
   absolute paths and drive letters are refused).
4. **No overrides (format 1).** A pack adds; it never replaces or edits the game's factions, types or scenarios.
   To change a base scenario, copy it into the pack under a new name.
5. **Versions.**
   - `"format_version": 1`: the pack layout. A sim refuses a format it doesn't know.
   - `"requires": {"sim_abi": N}`: the oldest sim it works with. A pack using keys added in a later ABI must say so;
     an older sim then refuses it with a clear message instead of failing on an unknown key.
   - `"version": "1.2"`: the pack's own version, free text, shown in menus and saves.
6. **Dependencies.** `"requires": {"packs": ["malvinas", "jdoe.uniforms"]}`: packs that must be loaded first (a
   mod using a DLC's faction, or another mod's types). A missing one refuses the pack, naming it.
7. **Load order** (the game at start-up): every `dlc/*` first, then every `mods/*`, sorted by id. A mod refused only
   because a dependency isn't loaded yet is retried after the others (until nothing new loads).
8. **Scenarios** list every pack they use: `"packs": ["jdoe.desert_ops"]`. A save records the packs its battle used;
   a load menu says which are missing.
9. **Strict keys.** Unknown keys are errors with a did-you-mean hint, in every file. That keeps typos out of shipped
   packs.
10. **Allowed files** (renderer 2 refuses anything else under a pack): `.json`, `.glb`, `.png`, `.jpg`, `.wav`,
    `.ogg`. No scripts of any kind.
11. **Art budget** per pack item, so one mod can't sink the frame rate: 20 000 triangles per object or building
    type, textures 2048 x 2048 at most.
12. **Art layout** (the same in `dlc/<id>/` and `mods/<id>/`; loaded at runtime, no import step):
    - `art/objects/<type>.glb`: one file per catalogue type, the node named `<type>`, plus an optional
      `<type>_down` for its destroyed look.
    - `art/buildings/<type>.json` + `.glb`: the building kit format, with per-cell pieces that break one by one.
    - **Minimum for a building to break visibly:** one intact `.glb` plus a correct cell footprint with a material
      per cell. Once breached, the game draws it by its cells (wall, sill, floor, rubble, debris by material).
    - `art/factions/<faction>.json`: the uniform look as palette parameters (4 camo colours, the pattern, pixel
      scale, gear, webbing, glove and boot colours). The soldier model itself is the game's.
    - `art/portraits/*.png`; `library/sounds/<slot>/*.wav` (+ an optional manifest), resolved like the game's own.
    - `art/menu/*.jpg|png|webp`: menu / loading-screen backgrounds tagged to the pack. The main menu
      crossfades through every loaded pack's art (plus the game's `art/ui/menu/` and the user's own
      drops in `user://menu_bgs/`); a scenario's loading screen prefers its own pack's art.
      A still may have a looping video beside it, `<stem>.ogv` (Theora, muted, about 4 s): the menu plays it in the still's place
      (`DEFIL_NO_MENU_VIDEO` turns them off). Made from the still by `tools/dlc_art/or_video.py` (OpenRouter Veo 3.1 Lite, the still as
      the first and last frame: 0.20 USD a clip) and `tools/dlc_art/menu_video.sh` (Overlord's `bg_flak`; `bg_bridge` with `--model bytedance/seedance-1-5-pro --resolution 720p`: 0.10 USD, calmer). A still without one moves by itself: a slow push-in and drift.
    - `music/menu/*.ogg`: the pack's own main-menu music while it is the active DLC (the first two files by name, crossfaded one into
      the other like the default suspense beds, at the same Music volume); without it the menu plays the default beds. Normalise to about -19 LUFS.
    - `menu.json` (renderer only, beside pack.json): the active DLC's mark at the bottom left of the main menu,
      `{"badge": "art/brand/badge.png", "title": "OVERLORD '44", "tagline": "...", "accent": "#b9a35a"}`, every key optional
      (no file: the pack's name in the menu red). Keep the badge out of `art/menu/` (that folder is backgrounds); a round
      emblem with a transparent outside, about 192 px. Every shipped DLC has one (`tools/dlc_art/badges/`).
13. **Check before you publish:** `defil_content_check [ROOT]` loads the base game alone, then the DLCs, then the
    mods, and checks each pack's scenarios, campaigns and briefings.

## Layout

```
dlc/<id>/
  pack.json          the manifest (below)
  factions.json      its factions, in the format of sim/data/factions.json (optional)
  objects.json       its catalogue types (buildings, props), in the format of sim/data/objects.json (optional, v63)
  weapons.json       its small arms, in the format of sim/data/weapons.json (optional, v99)
  scenarios/         scenario files (docs/scenarios.md), usually with "packs": ["<id>"]
  campaigns/         campaign manifests, as in campaigns/ (missions name files in the pack's scenarios/)
  briefings/         briefings by scenario name, as in briefings/
```

The sim reads `pack.json` and the factions, objects and weapons files it names. The menus list the pack's scenarios, campaigns and briefings the
way they list the game's own.

## Keeping the base game and a DLC apart

The base game ships first and a DLC lands later, but on a development machine everything is installed at once.
These rules keep the two separable, and `defil_content_check` enforces them.

1. Everything a DLC adds lives under `dlc/<id>/`: scenarios, campaigns, briefings, factions, and later its
   assets. Nothing of it goes in the base `scenarios/`, `campaigns/` or `briefings/`.
2. Every DLC scenario lists its pack: `"packs": ["<id>"]`. A base scenario names no packs.
3. A DLC may use base content (factions, catalogue objects, vehicles); the base game never names a pack id or a
   pack's faction id. A DLC campaign plays only its own `scenarios/`: copy a base scenario into the pack if you
   want it there.
4. Engine features a DLC needs (a vehicle type, a material, a generator) go into the sim, which ships with the base
   game or with the free patch that comes out alongside the DLC. The pack's `requires.sim_abi` says which sim.

Checks:
- `build/defil_content_check [ROOT]` (also a ctest) starts with no pack loaded. It loads every base scenario
  alone, then each DLC on top, and checks campaign missions, briefings and cross references. Run it before
  handing over any content.
- `tools/package.sh [OUT]` builds `defil-base-<rev>.tar.gz` (no `dlc/`, no `tools/<id>_kit`) and
  `defil-dlc-<id>-<version>.tar.gz` from HEAD. It runs the check on HEAD, then again on the base archive's
  own files.
- In the game, the renderer's base-game-only switch (renderer 2: `--no-dlc`) plays exactly what the first
  release ships; `--no-mods` (and the menu's "Load mods" box) leaves the community mods out.
  `defil_content_check --no-mods` checks the same way.

## pack.json

```json
{
  "format": "defil-pack",
  "format_version": 1,
  "kind": "dlc",
  "id": "malvinas",
  "name": "Las Malvinas",
  "desc": "one or two sentences for the menu",
  "version": "0.1",
  "requires": { "sim_abi": 60, "packs": [] },
  "factions": "factions.json",
  "objects": "objects.json",
  "weapons": "weapons.json"
}
```

- `id`: 1-40 characters of a-z, 0-9 and `_`. A pack loads once.
- `requires.sim_abi`: a pack made for a newer sim is refused, and the error names the ABI it needs.
- `factions`: a file inside the pack's folder. Each faction id must be new: not a built-in one, and not another
  pack's. A faction may itself require behaviour modules (`requires.modules`, see sim/data/factions.json). One bad
  faction refuses the whole pack, and none of its factions are registered.
- `objects` (v63): a file inside the pack's folder with `"types": [...]`, each in the format of
  sim/data/objects.json. They are appended after the built-in types in every sim made after. Name them with the
  pack's prefix (`mal_church`): a name that clashes refuses the whole pack. The renderers map a type's name to its
  model. With no pack loaded, the catalogue is exactly the game's own.
- `weapons` (v99): a file inside the pack's folder with `"weapons": [...]`, in the format of sim/data/weapons.json.
  (v136) It may also carry `"parts": [...]`, weapon parts in the same format as that file's `parts` (`id`, `name`,
  `slot`, `sight`, `zoom`, `accuracy`, `range`, `velocity`, `rate`, `weight`, `mag`, `suppressed`, `bipod`). A mod's
  parts are named `<pack>.<name>`; an id that clashes with a built-in or another pack's part refuses the pack. The
  pack's own weapons, later packs' and scenarios' `weapons` may fit them in their `parts` lists. One part per slot
  per weapon, as with the built-in ones. Factors are kept in a sane band (accuracy / velocity / rate 0.5-1.5, range
  0.5-2).
- `devices` (v139): a file inside the pack's folder with `"devices": [...]`, in the format of sim/data/devices.json (read its
  `doc` for the fields): robots and drones, carried in a pack or a vehicle's bay, set out and controlled by a soldier. A mod's ids are
  `<pack>.<name>`; a clashing id refuses the pack. A scenario vehicle's `type` may then name one.
- `doc`: free text for authors.
- `kind`, `format_version`, `requires.packs` (v92): see the format rules above. A community mod, in full:

```json
{
  "format": "defil-pack", "format_version": 1, "kind": "mod",
  "id": "jdoe.desert_ops", "name": "Desert Ops", "desc": "raiders, oil drums and two night raids", "version": "1.0",
  "requires": { "sim_abi": 92, "packs": [] },
  "factions": "factions.json", "objects": "objects.json"
}
```

Its factions are `jdoe.desert_ops.<name>`, its types `jdoe.desert_ops.<name>`. Examples: `tests/packs/mod_good/`, and
`mods/defil.eras/`: our own mod, 13 era / theatre factions (`defil.eras.us_vietnam`, ...) for the skinned soldier variants
and the test missions that use them. It was the DLC `dlc/eras` until 2026-10-19: one DLC at a time meant turning it on shut the real
expansions off, while mods sit beside any DLC. `mods/` never ships in the base game (tools/package.sh).

`defil_content_check` also checks each pack's files: only the allowed types; every `.glb` within the triangle budget and
every image within 2048 x 2048 (problems); and art for what the pack adds (warnings: a type with no
`art/objects/<type>.glb` or `art/buildings/<type>.json` is drawn by its cells, a faction with no
`art/factions/<id>.json` wears the base look).

## At start-up (renderers)

For each folder in `dlc/` with a `pack.json`, then each in `mods/`, call `defil_load_pack(dir, err, len)` before
making any sim. A refusal comes with a message; log it and skip that pack (retry the mods refused for a missing
dependency once the others have loaded). `defil_pack_kind(i)` says `"dlc"` or `"mod"`.
- `defil_pack_count` / `_id` / `_name` / `_desc` / `_version` / `_dir` list what loaded.
- `defil_faction_pack(sim, f)` says which pack a faction came from (`""` for the game's own or the scenario's).

## In a scenario

- `"packs": ["malvinas"]`: the scenario is refused, naming the pack, when that pack isn't loaded.
- `"faction": "mal_uk"` on a team or a squad picks a pack's faction.
- `forces[].side` names the side for the HUD and logs: `{"name": "United Kingdom", "short": "UK", "assets": {"flag": "uk"}}`.
  The sim still has two teams, `blue` (0) and `red` (1).
- Map generator `moor` and grounds `peat` / `rock` (docs/scenarios.md) for moorland maps.

## Saves

A save's header lists the faction ids and pack ids its battle used: `defil_save_game_factions` and
`defil_save_game_packs`. A load menu can say "needs Las Malvinas" without loading the battle. A save carries its
factions' profiles, so the sim can load it without the pack; whether to allow that is the menu's call (the
renderer may lack the pack's assets).

## Testing a pack

```
build/defil_headless --pack dlc/malvinas --scenario dlc/malvinas/scenarios/malvinas_moor_test.json --ticks 3600
```

The test `dlc_packs` (tests/sim_tests.cpp) checks:
- the Malvinas pack loads;
- refused packs are refused whole;
- the side names show;
- the moor map is deterministic;
- its test scenario fights;
- the built-in factions' fingerprints don't move.
