# Scenarios (JSON)

A scenario file describes a map and the forces on it. The sim loads it with
`defil_create_json`, and the `defil_scenario` tool checks, runs, draws and
re-saves it without a renderer.

`scenarios/` holds what is worth playing (the renderers' menus list it): the
missions (`silent_harvest`, `long_shot`), the village battles
(`woodland_farm`, `desert_village`) and two stealth demos
(`stealth_actions_test`, `stealth_pair_test`). Fixtures that only the tests
use live in `tests/scenarios/`.

Work in progress uses a `draft_` filename prefix (`scenarios/draft_x.json`,
`campaigns/draft_y.json`, likewise inside `dlc/<pack>/`): draft content is
hidden from the menus unless `DEFIL_DEV` is set, and `draft_*.json
export-ignore` in `.gitattributes` keeps it out of `tools/package.sh`
archives entirely.

```sh
build/defil_scenario check scenarios/woodland_farm.json   # validate + summary
build/defil_scenario run   scenarios/woodland_farm.json --ticks 5400   # JSON result
build/defil_scenario map   scenarios/woodland_farm.json   # ASCII map (legend on stderr)
build/defil_scenario save  scenarios/woodland_farm.json --ticks 900 > later.json
```

Mistakes are reported with where they are and, for typos, a suggestion, for
example `map.ops[3].type: unknown object type "cotage" (did you mean
"cottage"?)`. Unknown keys are errors, so a misspelt key never passes silently.

Coordinates are metres, and so are cells (1 m each): x grows east, y grows
south, and (0, 0) is the north-west corner. Ticks are 1/30 s.

**The format as data** (ABI v158): `defil_scenario_schema()` returns this format as JSON - every object the loader
reads (scenario, map, force, squad, mission, cue, objective, trigger, each condition and action), its keys with a type,
range or options, label, one line of doc and the ABI that added it. The loader takes its key lists from the same table
(`sim/src/scenario_schema.cpp`), and the in-game editor builds its forms from it: add a key there and both see it.

## Top level

| Key | | |
|---|---|---|
| `format` | `"defil-scenario"` | optional |
| `version` | `1` | optional |
| `name`, `description` | text | kept when the scene is saved |
| `seed` | integer | everything random (generators, `scatter`, soldiers' traits) follows it; default 1 |
| `map` | object | default: a 112x72 kit town (`"generator": "town"`; the classic bare-cell town was retired in v235) |
| `forces` | array | required: a `blue` and a `red` team |
| `mission` | object | optional: objectives, triggers, cues (see [Missions](#missions)) |
| `env` | `{"time": 23.5, "sun": 120, "moon": 0.35}` | (v57) the hour at the start, 0-24 (the clock runs with the battle); the sun's azimuth in degrees (-1 or omitted: the renderer picks); moonlight 0-1. Default noon. The light scales sight (at night a standing man is made out at ~45 m under a third moon), how fast men spot, and their aim; a firing man's muzzle flash shows him past that, but aimed at a flash he is hard to hit and he drops out of sight 5 s after his last shot (a suppressed weapon shows no flash). `defil_env` / `defil_set_env`. Also (renderer): `"weather": {"kind": "clear"|"dust"|"snow"|"flood"|"rain" (v157), "strength": 0-1.5, "wind": degrees}` and `"look": {"gamma": 0.5-2.5, "brightness": 0.5-1.5, "saturation": 0.2-2}` (v160: the scene's picture, saved by the dev look tool - `DEFIL_DEV=1` on any scenario run from a JSON file (tests, missions, campaigns, skirmish scenarios) shows a panel with gamma / brightness / saturation / time / sun sliders and a SAVE button that rewrites the file's env block), `"region": "<name>"` and `"regional_looks": true` (v356: the mission's region, the `map.region` names - a kit town's `map.region` sets it too - and the opt-in, default off: a faction then wears `art/factions/<id>.<region>.json` where that file exists, else `<id>.json`; `defil_env_region`, `defil_env_regional_looks`), `"backdrop": "<name>"` (v154: the far landscape painted round the map: `alpine_snow`, `alpine_forest`, `desert_mesa`, `tropical_hills`, `woodland_hills`) |
| `vehicles` | array | the vehicles on the map at the start (see [Vehicles](#vehicles)) |
| `next` | `"file.json"` | (v132) the scenario that follows, beside this one in its `scenarios/` folder: a scene (the `cinematic` flag) plays it when it ends; a mission won offers it as NEXT on the end panel (a campaign's own order comes first). Chains: mission -> scene -> mission, scene -> scene -> mission |
| `hidden` | `true` | not listed in the menus (a dev build still lists it, tagged `[hidden]`): a scene or mission reached only through a `next` chain, a campaign or `--scenario`. The sim ignores it |
| `stream` | `true` | (docs/SEAMLESS-WORLD.md) on a map over 4 km a side the renderer builds the objects and kit buildings only in the 256 m pages round the camera and unloads the rest. Generated worlds too big for git live in `library/worlds/scenarios/` (listed on the Tests page through `DEFIL_WORLDS`, set by `tools/play.sh`). The sim ignores it |
| `weapons` | array | (v99) the scenario's own weapons, `based_on` a catalogue one, with `parts` (see `sim/data/weapons.json`'s doc) |
| `jams`, `hearing`, `chatter`, `share_ammo`, `charisma`, `order_acks`, `ammo_walk`, `order_errors` | `true` / `false`, each default `true` | switch one battle behaviour off for a test ground or a scene; `false` is exactly the behaviour before it existed. See [Soldiers' voices, comms and ammunition](#soldiers-voices-comms-and-ammunition) |
| `caches` | array | ammunition caches `[{"at": [x, y], "team": "blue", "rounds": 600}]`; see the same section |
| `packs` | `["malvinas"]` | (v60) the content packs (DLCs) it needs; refused, naming the pack, when one isn't loaded. See [packs.md](packs.md) |

## map

| Key | | |
|---|---|---|
| `width`, `height` | 32..9216 each, at most 9216 x 9216 cells (v221: a 9 x 9 km region; was 2048 / ~2 km^2 since v119) | default 112 x 72 |
| `generator` | `"town"` (default), `"open"`, `"woodland"`, `"desert"`, `"moor"`, `"kit_town"` (v233), `"none"` | `none` is bare grass; all scale with the map (see below) |
| `region`, `era` | `kit_town` only: `"e_europe"`, `"w_europe"`, `"mideast"`, `"africa_sahel"`, `"africa_coastal"`, `"n_america"`, `"s_america"`, `"asia_south"`; a year (1950-2010 sets, the nearest) | (v233) whose buildings and when; default the European street, 1990 |
| `cover_pieces` | `open` only: pieces of cover per 112x72 of area (default 12) | |
| `materials` | `open` only: e.g. `["wood", "sandbag"]` | default wood, sandbag, stone |
| `spawn_gap` | metres between the two teams' start lines (`soldiers` spawning); default the map edges | |
| `ops` | painting operations, applied in order after the generator | see below |
| `objects` | object placements (saved scenes use this with `record_only`) | |
| `layers` | saved cell layers, run-length encoded | written by `save` |
| `heightmap` | (2026-10-14, after v246) a big map's relief, coarse: `{"step": 8, "heights": "<run-length dm>"}` - posts every `step` m (1-64), ((width + step - 1) / step + 1) x ((height + step - 1) / step + 1) of them, row-major, decimetres (-300..3000), post (i, j) at (i x step, j x step); every cell is interpolated bilinearly between the four round it | applied after the generator and before `layers` / `ops` (roads, hills, craters paint over it). 1 m `layers.heights` for 5 x 5 km would be ~100 MB of JSON; 8 m posts are ~1.5 MB. Written by `tools/map_gen/region_steppe.py` |

### Generators

(v120) A generated map's ground isn't flat: each generator adds light bumps (town 0.15 m, open 0.3, woodland
0.25, desert 0.2, moor 0.4 at most, about 8 m apart). `"map": {"rough": 0}` keeps it flat, `"rough": 0.5` bumpier,
`"rough": {"amp": 0.5, "scale": 4}` also tighter. Hand-made maps (`"generator": "none"`) use the op `rough` instead.

- `town` (= `kit_town`, v235): streets of kit buildings by region and era (`"region"`, `"era"`), a square, a park, three
  sectors, stone garden walls, sandbag positions and crates; counts scale with the area. Also the town of `defil_create` /
  the sim tests / the goldens. (Until v233 `town` was the classic map of bare-cell brick boxes; it is retired.) See `docs/MAP-GENERATION.md`.
- `open`: an open field with `cover_pieces` scattered pieces of low cover.
- `woodland`: farming villages, one per ~320x320 m. Each has a road with a lane
  through the village, and brick cottages facing the road in hedged or fenced
  gardens with a gate and a yard prop (well, cart, hay). Around them: crop
  fields and meadows behind hedgerows or stone walls, orchards, and woods of
  undergrowth and trees.
- `desert`: villages on sand, one per ~320x320 m. Each has a dirt road and lane,
  mud-brick houses and walled compounds, a market square with stalls and a
  well, and low walls and palms. There is a dry riverbed (gravel, scrub,
  palms) and there are palm groves, scrub and wrecks by the roads.
- `moor` (v60): open, treeless moorland (the Falklands' camp). Wet peat in the
  hollows, grass on the drained slopes, and a long ridge across the middle third
  (15-26 m high) crowned with rock: tors (high rock that hides and stops, ringed
  by boulders that give crouch cover) and stone runs spilling down its flanks.
  Tussock clumps hide a man, a stream runs down one flank, and a sheep fence
  crosses the map. No buildings: place them with `ops`.

The 12 m strips on the west and east edges stay clear for the start lines.
`ops` run after the generator, so a generated village can be edited. All the ways a map is made (the region / era generator
`tools/map_gen/mapgen.py`, mission scripts, OpenStreetMap, the editor): `docs/MAP-GENERATION.md`; how buildings break:
`docs/BUILDINGS.md`.

### ops

Cell fields used by `rect` and `line` (give at least one):
`kind` (`empty`, `low`, `high`, `rubble`, `floor`, `fence`), `material`
(`wood`, `sandbag`, `stone`, `brick`, `metal`, `adobe`, `straw`, `timber`),
`ground` (`grass`, `dirt`, `road`, `gravel`, `sand`, `mud`, `water`, and (v60) `peat`: soft going x0.8, quiet x0.8,
smears camo like mud; `rock`: a stone run or scree, slow x0.7, loud x1.3; both slow vehicles; (v148) `snow`: ankle-deep,
men x0.75 (~60% of a grass walk), steps muffled x0.75, wheeled vehicles ~15% slower without bogging, shallow ruts;
(v241) `soft_sand`: loose dune sand, men x0.7, quiet x0.8, dirties weapons like sand, wheels ~30% slower and tracks ~10%
without bogging, shallow ruts; the renderer sinks boots up to the ankles on the loose faces and keeps footprints and tyre
tracks; packed `sand` is unchanged; (v246) `deep_snow`: knee-deep snow, men x0.5 (about half a grass walk, two thirds of
`snow`), steps muffled x0.7, wheels grip 0.4 / tracks 0.75, no bogging, deep ruts; drawn as snow, the renderer sinks a man to the knee
(0.34 m standing) and leaves a trench behind him; a road through it is packed snow; (v301) `paving`: concrete / cement - plazas, decks, city streets: firm and
level like a road (pace x1.0, ordinary noise, full vehicle grip), drawn as grey cement),
`conceal` (density, hundredths per metre: 40 sparse, 100 thick, 200+ a wall
of foliage) with `conceal_height` (metres).

| op | keys | |
|---|---|---|
| `rect` | `x, y, w, h` + cell fields | fill a rectangle |
| `line` | `from: [x, y], to: [x, y], width` + cell fields | roads, hedgerows, walls |
| `object` | `type, x, y, rot`, optional `name` (for missions) | one object from the catalogue (`sim/data/objects.json`); `x, y` is the top-left of the rotated footprint, `rot` quarter turns clockwise (the catalogue drawing's bottom row is the front: doors, gates) |
| `scatter` | `type, count, area: [x, y, w, h], rot, spacing, clear` | many objects at random spots (from `seed`); `rot` omitted = random; `spacing` = minimum metres apart; `clear` (v156, 0-12) = keep this many metres from roads, tracks, water, buildings and tall objects (no crowns over a roof, no trees in a stream) |
| `destroyed` | `area: [x, y, w, h], craters, crater_radius: [min, max], fell: 0-1, damage: 0-1, mud: 0-1` | (v163) a battered landscape at load: `craters` shell craters (many small, few big; the ground goes down, the rim up, a ring of churned mud), `fell` = the share of tall vegetation / poles in the area that falls, `damage` = the share of building wall cells shot down to 15-65% of their hit points. Put it LAST in the ops. Maps up to ~4 km^2 (v162: 4096 m a side, 4 194 304 cells) |
| `hill` | `at: [x, y], radius, height` | (v41) a rounded rise, or with a negative `height` a hollow (metres, -30..300). Heights add up: hills on hills, a hollow in a rise. Sight lines, cover and vehicles follow them |
| `power_line` | `from: [x, y], to: [x, y], spacing` | (v46) poles every `spacing` m (default 25) strung with wires |
| `rough` | `amp, scale, seed, area: [x, y, w, h]` | (v117) bumpy, imperfect ground: layered noise added to the heights. `amp` m = the biggest bumps (0.05-3, default 0.4), `scale` m = their spacing (2-60, default 8), `area` default the whole map (its edge feathered over 4 m). Roads get a quarter of it; walls, floors and buildings are left flat. Put it after the `rect`s that paint the ground and before the objects |

Finding an object type: the catalogue self-describes — every row has a one-sentence `desc`, `tags`
(`region:*` one of e_europe / w_europe / n_america / s_america / asia_east / asia_south / mideast /
africa_sahel / africa_coastal, `role:*` what it is for - dwelling / shop / religious / civic / barn /
landmark / parked..., `era:*`), the `footprint` drawing and (newer rows) `height` in metres. `kit`-tagged
rows are the procedurally-built buildings; a footprint with `.` or `d` cells is enterable. To browse:
`renderer/godot/project/art/buildings/buildings_index.json` is a per-kit sheet (pieces, mass, height,
materials, footprint) and `tools/object_browser/run.sh --type NAME --shot /tmp/x.png` renders any type
off-screen.

Terrain recipes (from `scenarios/test_mud_tank.json`):
- a field that isn't a billiard table: `{"op": "rough", "amp": 0.35, "scale": 7}` over the whole map;
- churned, lumpy mud: a `mud` `rect`, then a `rough` on the same area with `"amp": 0.6, "scale": 4`;
- puddles: small hollows in mud (`{"op": "hill", "at": [108, 61], "radius": 5, "height": -0.45}`) - the renderer
  fills the hollows of mud with standing water by itself (no `water` cells: they draw as flat rectangles);
- a wide, shallow dip: a `hill` with `radius` 20-40 and `height` -0.5..-1.

Order matters: ops run top to bottom, so paint the ground (`rect` / `line`), then shape it (`hill`, `rough`), then
place objects.

A hedge is `"kind": "fence"` plus `"conceal": 220, "conceal_height": 2.0`
(climbable, see-through for bullets, blocks sight). Crops are `"conceal": 80,
"conceal_height": 1.0`, which hides a prone or crouched man but not a
standing one. The catalogue has ready-made `hedge`, `crop_field`, `bush`,
`thicket`, and so on.

## forces

An array with one entry per team, `"team": "blue"` and `"team": "red"`.

| Key | | |
|---|---|---|
| `soldiers` | 1..4000: squads of 8 on the team's start line (map edge or `spawn_gap`; past 400, more columns further back) | like `defil_create` |
| `squads` | array of squads placed by hand | below |
| `experience` | 0 (green) .. 100 (veteran), default 50 | |
| `mode` | `aware`, `combat`, `hold`, `stealth` | for all the team's squads |
| `roe` | `fire_at_will`, `return_fire`, `hold_fire` | |
| `ai` | `true` (default): the squad's AI picks its own objective; `false`: it waits for orders | |
| `travel` | `"step"` / `"flow"` | (v151) `flow`: calm travel without bounds or halts - the squad's anchor slides toward the objective, each man keeps his slot and sets his own speed from it (slower when ahead, quicker when behind), the squad waits for a straggler by slowing. Default `step` (bounds). Ends at first contact |
| `skis` | `auto` \| `on` \| `off` (or `true` = auto) | (v249) ski troops (docs/SKIS.md): AUTO - the men put skis on for a long move over snow (a road through snow counts) and take them off to fight, on bare ground, for a building, a wall or a steep face; `on` / `off` force it (BEHAVIOUR > SKIS in game). No key: no skis |
| `speed` | 0.3 - 1.5 | (v150) a fraction of the usual pace for the whole squad (the sim's walk is 1.5 m/s; formation catch-up pushes a column's mean higher). 0.7 for a calm patrol |
| `formation` | `"line"` / `"file"` / `"wedge"` / `"dispersed"` | (v149) how the squad spreads while it moves: `file` = single file, point first. Default: the mode's own |
| `suppressed` | `true`: suppressed weapons (shots heard ~20 m instead of 150, no muzzle flash, only a rough position given away) | also per squad |
| `camo` | `"none"`, `"paint"`, `"ghillie"`, `"mud"` (mud: x0.15 detection still or crawling, x0.3 crouch-walking, x0.6 walking, x1 running or firing; wears off moving, washes off in water) | also per squad |
| `charges` | explosive charges each man carries (planted by order on an object; 30 s fuse) | also per squad |
| `smokes` | smoke grenades each man carries, 0-9 (default 1; thrown by the squad AI to screen a move to cover) | also per squad |
| `faction` | a faction id (`regular`, `militia`, a pack's, the scenario's own) | also per squad |
| `nv` | (v113) night-vision goggles: `all`, `leaders`, `none` — overrides the faction's kit for the squad (or the whole team) | also per squad |
| `side` | (v60) how the side is presented: `"United Kingdom"`, or `{"name": "United Kingdom", "short": "UK", "assets": {"flag": "uk"}}` | default `Blue` / `BLUE`, `Red` / `RED`; the renderers show it (`defil_side_name`) |

A squad in `squads`:

| Key | | |
|---|---|---|
| `at` | `[x, y]`: centre of the squad's line | required |
| `size` | 1..40, default 8 | |
| `facing` | `"east"`, `"south"`, `"west"`, `"north"` or degrees (0 = east, 90 = south); default toward the enemy side | |
| `experience`, `mode`, `roe`, `ai` | as for the team, per squad | |
| `move_to` | `[x, y]`: a move order given at the start | |
| `hold_at` | `[x, y]`: a hold order given at the start: they go there and settle behind the best cover within 10 m of it, toward the enemy (v241) | not with `move_to` |
| `routine` | `"sentry"`, `"patrol"`, `"garrison"`: the squad is going about its business, not expecting anyone (see below) | no `mode` / `move_to` / `hold_at` with a routine |
| `route` | patrol only: `[[x, y], ...]`, at least 2 points, walked in a loop | |
| `name` | a mission name for the squad (`"alpha"`) | unique across units, squads, objects, areas |
| `names` | mission names for its men, in order (`["lead", "gunner"]`) | |
| `captured` | `true`: the squad starts as prisoners of the other side (disarmed, lying down, unguarded) | a hostage to free |
| `state` | `"dead"`: its men lie dead where they spawn (an aftermath) | scenes, test grounds |
| `gore` | (v134) 0..1, with `"state": "dead"`: the bodies start torn up - wounds, and at 1 about half have lost a limb; the renderer lays the limbs and old blood out by them (no blast needed) | aftermath scenes |
| `snipers` | names (from `names`) of men with a scoped rifle: lying still they see ~350 m in a narrow cone (the man next to one spots with binoculars, a wider cone); `DEFIL_ORDER_SHOOT` then reaches that far (a hit is a heavy wound: head nearly always fatal) | |
| `unarmed` | names of men who carry no weapon (a VIP, an official) | |
| `look` | (v190) a soldier-variant id (`art/units/soldiers/<id>`, e.g. `us_1982_rifleman`), same form as `model`; also a force key (all its squads; a squad's own wins) | the renderer dresses the squad's men in that variant when it is loaded, else its automatic pick by faction, era and role (an unknown id warns once). Kept as `defil_squad_look`, saved |
| `weapon` | (v114) a weapon id every man of the squad carries (a catalogue one or the scenario's own `weapons`), instead of the faction kit's | e.g. a suppressed sniper rifle with a 16x scope, `scenarios/test_sniper_bipod.json` |
| `man_weapons` | (v194) `{"Name": "weapon id"}`: one man's own weapon (names from `names`), over the squad's `weapon` and the kit's | one suppressed rifle and one plain in the same squad: `scenarios/test_silencers.json` |

A squad on a **routine** starts UNAWARE: sentries stand at their posts and
watch their sector (around the squad's `facing`, one direction at a time); a patrol walks its route in file;
a garrison idles where it stands, noticing little. They notice slowly: a
detection meter builds up on each enemy they can see. At 30 the man becomes
suspicious (stops, looks, and whispers to his mates within 15 m); that fades,
or two of them go and search the spot (team alarm 1, caution); at 100 he has
spotted someone and the squad is alerted (team alarm 2). Being shot at, or
hearing unsuppressed gunfire within 150 m, alerts them too. At alarm 2 the
word goes round by radio (the squad leader) or, without one, to squads
within 80 m: sentries and garrisons hold where they are, and patrols head for
the spot.

## Vehicles

`"vehicles": [ ... ]`, one object each:

| Key | | |
|---|---|---|
| `type` | `apc`, `moto`, `troop_truck`, `militia_truck`, `technical`, `mbt`, `militia_tank`, `qugv`, `m113`, `stryker`, `bradley`, `humvee`, `bm21`, `sedan`, `tigr`, `quad`, `bmp1`, `bmp2`, `btr80`, `uaz`, `zamyad`, `mi8`, and the civil `car`, `van`, `truck`, `tractor`, `cart`, `bus` (v191: car / van / truck / bus have passenger seats and a squad can commandeer a parked one; the list is `vehicle_type_names()` in `scenario_schema.cpp`: the loader and the editor's picker read it) | `militia_tank` draws as a T-72; `qugv` (v131) is the crewless quadruped robot: it drives itself (no driver), walk / run / turn clips follow its motion. (v137) With `"crew": true` (the default) it carries a 7.62 mm MG worked by a body-less proxy (`DEFIL_FLAG_MACHINE`, never drawn): it fires per the vehicle's `roe` and, with an `operator`, only while the link holds; what it sees goes into the operator's squad's picture. `"crew": false` keeps it weaponless (scenes); (2026-10-14) its sensor proxy is always there, so it still sees. A device's camera (a drone) is never dropped by `"crew"` either (it used to be: blind, and nothing to shoot at). A robot's weapon station sees with its sight's optics (x2 a man's eye) |
| `team` | `blue` / `red` | |
| `operator` | a soldier's name (from the forces, same side) | (v137) makes the vehicle a **device** a soldier controls from where he stands. The link is LINKED while he is up, in range and not under fire; DEGRADED under fire (he is not flying it); LOST when he is down or out of range. A device takes no new orders unless LINKED, carries on with the one it has, and `lost_wait` seconds after the link was lost does `on_lost_link`. While it moves or aims he kneels, head down, doing nothing else. With no `operator` it is scripted / autonomous (scenes) and takes orders as before |
| `type` (devices, v139) | a device id from `sim/data/devices.json` (or a loaded pack's), e.g. `quad_recon` | an air body: no footprint, flies straight at its goal at a cruise altitude, hovers when it has none; a battery (it heads home by itself when what is left is just enough, comes down where it is when it runs out); its camera feeds its operator's picture and is also its target (small, seen inside ~120 m; a rifle round does 30-60 against the catalogue's `hull`). Orders as for any vehicle (`defil_cmd_vehicle_move`; `defil_cmd_device_land`). `on_lost_link` may be `land` for air bodies. `link_range` / `on_lost_link` / `lost_wait` default to the catalogue row's |
| `link_range` | metres, default 400; 0 = unlimited (a tether) | needs `operator` |
| `on_lost_link` | `hold` (default) / `home` | stop where it is, or drive back to where it was set up; needs `operator` |
| `lost_wait` | seconds, default 15 | how long it carries on with its order before `on_lost_link` |
| `stowed_in` | a soldier's name, or an earlier vehicle's name | (v138) the device starts packed: in that man's pack (a robot dog is a heavy load) or that vehicle's cargo bay (moto 1, APC / M113 / Stryker / technical 2, trucks 4); no `at` needed. A man near the carrier sets it out with a drill (kneeling, ~6 s) and controls it from then on; the same to take it back (it drives to him first). A carrier who goes down, or a vehicle that burns, drops it (link LOST). Triggers: `{"vehicle": name, "deploy": [x, y]}` / `{"vehicle": name, "recover": true}` (by its `operator`) |
| `at` | `[x, y]`: its centre | required |
| `heading` | degrees, 0 = east, 90 = south | |
| `crew` | `true` (default): it starts crewed; `false`: empty, for a squad to board |
| `experience`, `roe` | as for squads | |
| `name` | a mission name | |
| `model` | (v190) a model id of the renderer's registry (`art/units/vehicles/<id>` or `air/<id>`, e.g. `bradley_fal`), `[a-z0-9_]`, up to 48 characters | draws this one vehicle with that model instead of its type's default; an id the renderer does not know draws the default (one warning); the dev `--vehicle-model` flag of its type wins. The sim only checks the form and keeps the id (`defil_vehicle_model`), saved with the game |
| `hatches` | `"closed"`, `"open"`, `"auto"` (the crew's call) | tanks only |
| `ammo` | integer rounds, default 0 | small-arms rounds its side's infantry can refill from it while it is stopped (speed < 1 m/s, not a wreck); see [Soldiers' voices, comms and ammunition](#soldiers-voices-comms-and-ammunition) |
| `rounds` | `[he, ap]` main-gun rounds | tanks only |
| `move_to` | `[x, y]`: a drive order at the start | |
| `speed` | (v129) m/s, 1-40: a scripted top speed on a road (off road the same share of it), whatever the pace: a bike at 70 km/h is `19.4` | scenes |

**Electronic warfare** (v140): top-level `"ew": [{"team": "red", "at": [x, y], "jam_radius": 150, "df_range": 600}]` (give either or both).
A post JAMS the other side's radio-linked devices inside `jam_radius` of the device or of its operator (the link is lost; a hand-flown
strike drone with no link crashes, other devices do their `on_lost_link`), and its direction finders FIX the other side's operator of a
radio device that is transmitting (flying, or moving) inside `df_range` of the operator: one post gives a rough fix (~50 m), two a good one
(~8 m); the fix enters that whole side's picture as a heard contact (`DEFIL_VEHEV_FIXED`, `DefilVehicleLink.fixed`). A device whose catalogue row
says `"emits": "fiber"` is deaf to both. Strike drones: `defil_cmd_device_attack` (an FPV flies into a man or a spot and goes off, single use),
`defil_cmd_device_drop` (a bomber drops its grenades on a spot); catalogue rows `fpv_strike`, `fpv_fiber`, `quad_bomber`.

**Mines** (v129): top-level `"mines": [{"at": [x, y], "kind": "at" | "ap", "team": "red"}]`. An anti-tank mine (`at`, default)
goes off under a vehicle of the other side (a bike's rider is thrown off first, then the blast - a mortar-sized one);
an anti-personnel mine (`ap`) under a man. The mine's own side knows where it is and doesn't set it off.

Soft ground (v118). Mud, water and peat grip less (mud: tracks ~0.55, wheels ~0.35); climbs slow a vehicle. What it
can't put down spins (slip) and digs it in (sink, heavier faster); dug in and down to a crawl, it is stuck
(`DEFIL_VEHEV_STUCK`), and the driver rocks it back in its ruts every few seconds until it lifts out
(`DEFIL_VEHEV_FREED`). The renderer sinks the hull and throws mud off the tracks. Two things to know when you make a
mission of it:
- the route planner goes round mud when it can: a mud band that must be crossed has to run across the whole map
  (or between impassable things);
- a T-72 crossing ~60-80 m of rough mud bogs down about half way and takes 10-25 s to rock free (probe:
  `tools/sim_probes/mud.cpp scenarios/your.json 6`). A shorter or flatter field (no `rough`) it usually crosses.

Ruts (v121): each vehicle presses ruts into soft ground under its tracks / wheels (a tank ~0.4 m in mud, a truck ~0.1 m;
dirt, sand and water less, grass only under 30 t and up). They fill with water in the renderer and change the next
vehicle's grip: a tracked one runs on the packed bottom, a wheeled one drags and sinks faster - a truck following a
tank through mud bogs down in its ruts (try two vehicles with the same `move_to`).

Towing (v123): a friendly vehicle stuck 8 s gets the nearest free tower within 150 m (crewed, mobile, at least 60%
of its weight): it drives to the stuck one's nose, hooks a cable, pulls it forward until it is out and on firm ground
(or 40 m on), and both go back to their own orders. A tower can bog down too while it pulls. A truck high-centred in a
tank's ruts (deeper than 25 cm) can hardly rock itself out: it waits for a tow. The C API: `defil_cmd_vehicle_tow`.

Templates: `scenarios/mission_mud_season.json` (the showcase: a column across a flooded bottom, cues on `{"stuck": ...}`), `scenarios/test_mud_tank.json` (rough ground, a mud band, puddle hollows, a dressed farm, a T-72 and an
escort), `scenarios/test_sniper_bipod.json` (a lone sniper at dusk with a squad `weapon`).

## Soldiers' voices, comms and ammunition

Behaviours added around speech, radio orders and ammunition. Each is a switch at the top level of the scenario (and a C call,
`defil_set_<name>(sim, 0 | 1)`); all default **on**, and off restores the old behaviour exactly. Anything that only ever *talks* (the
voice events) has no switch: it changes nothing in the battle. The event formats are in [sounds.md](sounds.md#speech-events).

| Key / call | What it does when on |
|---|---|
| `jams` / `defil_set_jams` | a weapon can jam after a shot (about 0.5% a shot for a rifle, 1% a machine gun, 0.2% a sniper rifle; worse in sand, mud, water, snow and dust storms, with fouling from rounds fired, tracer ammunition and a careless or unskilled man). The man stops firing for 1.5-4 s (a double feed, 1 in 10, takes 2.5x as long) and says `SAY_JAM` |
| `hearing` / `defil_set_hearing` | every spoken line carries by its loudness (a whisper 5 m, speech about 15, a call 30, a shout 40, a scream 60; a heated man x1.15, a calm one x0.85) and the **enemy hears it**: they get a rough fix on the speaker. A wall cuts a voice to 0.4, wind (in a storm) carries it further downwind, a firefight masks whispers and footsteps (not shouts). Off: the old flat 25 m for a second after any call |
| `chatter` / `defil_set_chatter` | calls are answered: "Cover me!" waits for the covering man's answer (0.2-1 s, and if he cannot cover, nobody answers and the caller stays put and tries another), the covering fireteam answers a bound, a rescuer says he is coming, a second man who sees what the first called says so, a buddy answers a reload. Whether a man *voices* his answer depends on how talkative he is; what he *does* never does |
| `share_ammo` / `defil_set_share_ammo` | a man with less than a magazine in all is handed one by a squadmate within 12 m (6 m in a fight) who keeps a spare for himself and has a line to him; the giver stops firing for a second |
| `ammo_walk` / `defil_set_ammo_walk` | when nobody is that close, the nearest squadmate with a spare magazine runs it over (40 m, 20 m in a fight and only where no known enemy sees the way); the asker waits for him instead of stripping the dead. Off: only the nearby help |
| `charisma` / `defil_set_charisma` | a charismatic leader close by steadies a man's stress faster, his calls (stay low, on me, hold...) ease the men within earshot, and a heated man's scream of pain or loss shakes the men beside him (less so with a steady leader near) |
| `order_acks` / `defil_set_order_acks` | an order given **between steps** (a player's; not an AI's, a mission action's or one inside the step) to a squad with an active leader waits 0.2-1.5 s while the leader takes it down (state `WAITING`, reason `RECEIVING`); then it starts and he answers over the radio, passes it on, two men answer, and he later reports "in position" or "can't do it" once. If he fell before answering the order is cancelled (reason `NOT_RECEIVED`) |
| `order_errors` / `defil_set_order_errors` | an order the leader takes down can be **misheard**: probability about 2% calm, 15% with him under fire, 40% under an enemy jammer (an `ew` post whose `jam_radius` covers him), less for an experienced, disciplined man. Of the misses 40% are "say again" (nothing starts, reason `SAY_AGAIN`, the player re-issues) and the rest, for an order that points at a spot, a wrong place 25-100 m off: the squad acts on it, the leader's radio answer reads back the place he heard, `defil_order_heard` tells the UI it differs from what was asked, and re-issuing draws a "correction" answer. Needs `order_acks` |

A save made at any moment replays identically after a load (the fan cache that decides what a man knows of the enemy goes into the
save), including while an order is being taken down, a giver is walking or a man is on a refill trip.

### Ammunition caches and supply vehicles

```json
"caches": [ {"at": [185, 55], "team": "blue", "rounds": 900}, {"at": [90, 70], "rounds": 400} ],
"vehicles": [ {"type": "troop_truck", "team": "blue", "at": [60, 25], "crew": false, "ammo": 300} ]
```

| Key | | |
|---|---|---|
| `at` | `[x, y]` | required: where the cache is |
| `team` | `blue` / `red`, or omitted | whose men may refill here; omitted: either side |
| `rounds` | 1-99999, default 600 | small-arms rounds it holds; an empty cache stays on the map at 0 |

A man who is nearly out of ammunition (less than one magazine in all) and whom no squadmate helps within 2 s walks to the nearest
cache of his side, or to a stopped supply vehicle of his side that carries `ammo`: within 60 m (25 m in a fight, and only where no
known enemy sees the way), two men at most to one source, and none for a few rounds. He crouches there for 2 seconds and refills to
four magazines' worth in reserve (three for 100-round belts), never more than the source holds. The trip ends if the source runs dry,
is wrecked or drives off (a vehicle must be below 1 m/s), he is pinned or panicked, or 25 seconds pass. Scenarios that declare no
caches and no vehicle `ammo` behave exactly as before. Read the stock back with `defil_cache_count` / `defil_cache` (x, y, team,
rounds, rounds_max) and `defil_vehicle_ammo`.

## Civilians

A `forces` entry with `"team": "civilian"` adds people who aren't soldiers
(C API: `defil_civilians`, EV_CIVILIAN). Nobody aims at them. They go about
their routine, panic at gunfire and blasts (run for a building, hide, and
calm down 90 s after the last shot), cower when rounds land close or an
armed man is on top of them, and can be hit by stray rounds and blasts.
A civilian who `informs` a side and makes out a soldier of the other side
runs to the nearest soldier of his side and tells him: that side learns the
position and its alarm goes up. A dead man close by in view sends him off
screaming (the alarm goes up if his side is within 40 m). Disciplined
soldiers don't put rounds into a spot with a bystander.

| Key | | |
|---|---|---|
| `informs` | `"red"`, `"blue"` or `"none"` (default): the side they report to | also per group |
| `groups` | array of groups | required |

A group:

| Key | | |
|---|---|---|
| `at` | `[x, y]`: where they live / work | required |
| `size` | 1..30, default 1 | |
| `routine` | `"wander"` (walk about home within `radius`), `"work"` (a few steps about one spot), `"home"` (stay there; put it inside a building) | default wander |
| `radius` | metres, default 20 | |
| `name`, `names` | mission names for the group and its people; `"civilians"` means all of them | |

## Missions

A `mission` block turns a scenario into a mission: things get names,
objectives say what to do, triggers make things happen, and cues tell the
renderer what to play. The sim runs it on its own (C API: `defil_mission`,
`defil_objectives`, `defil_cues`, `defil_cue_done`, flags; events EV_CUE,
EV_OBJECTIVE, EV_MISSION_END, EV_TRIGGER). `defil_scenario run` plays a
mission headless, finishing each cue at once, and prints the result with a
timed log. Examples: the missions `scenarios/silent_harvest.json` and `scenarios/long_shot.json`; a small one for tests in `tests/scenarios/mission_test.json`.

| Key | | |
|---|---|---|
| `name`, `briefing` | text | `defil_mission_text(sim, 0 / 1)` |
| `player` | `"blue"` (default) or `"red"` | whose objectives these are, and whose music mood |
| `areas` | `{"name": {"rect": [x, y, w, h]}}` or `{"name": {"circle": [x, y, r]}}` | |
| `cues` | array of cues | |
| `objectives` | array of objectives | |
| `triggers` | array of triggers | |

**Names.** Squads (`name`), their men (`names`), objects (`name` on an
`object` op) and areas are referred to by name; `"blue"` and `"red"` mean a
whole side. A name that doesn't exist is an error, with a suggestion. A squad
a trigger spawns can be named, and referred to before it exists. A named
squad keeps its men as spawned, even if a freed prisoner later joins another
squad.

**Cues** are for the renderer: `id`, `kind` (`dialog`, `radio`, `cutscene`,
`sound`, `music`, `camera`, `text`), `text`, `speaker` (the name of a man,
who is then the speaker unit, or any label like `"HQ"`), `asset` (the
sound, track or cutscene to play), `at` `[x, y]`, `duration` in seconds. A
dialog, radio or text cue lasts 1 s plus 0.06 s per character (2 s at
least) unless told otherwise; the other kinds last until the renderer calls
`defil_cue_done`. Triggers can wait for a cue with `{"cue_done": id}`.

**Scenes** (v129). A camera cue also takes `follow` (a unit, squad or vehicle name: the camera stays on it until the
next camera cue), `zoom` (metres in view), `pitch` (degrees over the ground; under 25 a low, near-ground view) and
`yaw` (degrees); the framing eases in. A text cue with `"style": "title"` is a centred title card (the first line big,
the rest under a red rule), fading in and out over its `duration`. (v133) `"style": "blackout"` cuts to black at once with a blood-red
blink, black until the scene ends (a shot at the camera that ends the scene). The flag `cinematic` (`{"flag": "cinematic"}`)
turns the renderer into a player: no HUD, letterbox bars, no orders. Esc or Space shows "Press again to skip";
pressed again within 3 s, the scene runs on undrawn until it hands over (the flag cleared: play starts; the mission
over: its `next`, else the menu). The flag `muddy_roads` draws the
roads as mud (wet, water in the hollows) and vehicles driving fast on them throw clods and spray - the look only:
in the sim they stay roads (no bogging). Example:
`scenarios/test_scene_bike_mine.json` - two bikes at 70 km/h, a mine, an ambush, the title.
`scenarios/test_scene_robots.json` - a mortar barrage on a field of dead, five robots walk past (side camera), the title.

**Comic cutscenes.** A cue `{"kind": "cutscene", "asset": "x.json"}` opens `art/cutscenes/x.json` full screen; the
world holds until the last beat ends or the player skips (Esc), Space steps a beat. The file is a list of pages:
`[{"page": "x.jpg", "beats": [{"who": "HQ", "avatar": "pt_cmd_1", "text": "...", "voice": "cue_xx_id", "focus": [x, y, w, h]}]}]`.
`page` is an image in `art/cutscenes/` (jpg/png, about 1920 px wide; no text on it, the dialog box carries it);
`avatar` a portrait in `art/portraits/` (no extension); `voice` a voice group (`tools/voice_lines.json`); `focus`
an optional crop of the page (fractions 0-1) the view zooms to for that beat. The letterbox of a cinematic scene
hides while a page is up. Examples: `art/cutscenes/cmp_*.json` (one per campaign mission); a screenshot of one:
`DEFIL_CS_SHOT=1 renderer/godot/offscreen.sh run.sh --scenario scenarios/mission_highground.json --at 2 --shot out.png`.

**Objectives**: `id`, `kind`, `text` (shown to the player), `optional`
(a bonus: never decides the mission), `state` `"active"` (default) or
`"hidden"` (a trigger reveals it later).

| kind | keys | done when | fails when |
|---|---|---|---|
| `reach` | `area`, `who` (default the player's side), `count` (default 1, or `"all"`) | that many of `who`'s fighting men are in the area | |
| `free` | `target` (a prisoner) | every target is back in the fight | a target dies |
| `destroy` | `target` (an object) | the object is destroyed | |
| `eliminate` | `target` (men, a squad, a side) | every target is down, dead or captured | |
| `hold` | `area`, `who`, `seconds` | `who` has held the area, with no enemy in it, that long in one go | |
| `extract` | `area`, `who`, `with` (optional: must come too), `aboard` (v191, optional) | every fighting man of `who`, and all of `with`, are in the area; with `"aboard": true` each `with` man must instead be alive (down or surrendered counts) and seated in one of the player's vehicles that is inside the area | someone in `with` dies |
| `survive` | `target`, optional `seconds` | at the end (or after `seconds`) | a target dies |
| `undetected` | | at the end | the enemy spots one of the player's men |
| `time_limit` | `seconds` | at the end | time runs out (counted from when it became active) |
| `spare_civilians` | `count` (default 0) | at the end | the player's side kills more than `count` civilians |

`survive` also takes a civilian, a civilian group or `"civilians"` as its target.

**A snatch (v191)**: a captive carried out in a vehicle is `{"id": "snatch", "kind": "extract", "who": "Team", "with": "Boss", "area": "safehouse", "aboard": true, "text": "..."}`.
"the vehicle with the captive reached Y" as a trigger condition is the vehicle-in-area condition (`{"area": "safehouse", "who": "<vehicle name>"}`).
Civil `car` (driver + 3 passengers), `van` (+5), `truck` (+2 in the cab, +6 on the bed) and `bus` (+10) have passenger seats (positions approximate);
a squad's mount order on a neutral one commandeers it (it becomes the squad's team's, the first man in drives; `tractor` and `cart` can't be boarded).
A man carrying or dragging a captive (dead, down or surrendered) loads him with `DEFIL_ORDER_LOAD_BODY` and takes him out with `DEFIL_ORDER_UNLOAD_BODY`.

The mission is **won** when every primary objective (not `optional`) is
completed; `survive`, `undetected` and `time_limit` are conditions on the
way and don't need to finish before that, except a `survive` with `seconds`.
It is **lost** when a primary objective fails, or none of the player's men
is still fighting. A hidden primary objective has to be revealed and done.
Squads spread about 10 m around the point they are sent to, so make `reach`
and `extract` areas at least ~24 m across, or use `count`.

**Triggers**: `id`, `when` (a condition; none = at the start), `do` (a list
of actions), `delay` (seconds from when the condition first holds to the
actions), `repeat` (fire again each time the condition becomes true again;
default once), `enabled` (default true).

Conditions (one key each, plus its options):

| | |
|---|---|
| `{"all": [...]}`, `{"any": [...]}`, `{"not": {...}}` | combine |
| `{"time": s}` | seconds since the start |
| `{"every": s}` | true for one tick every s seconds — the metronome for a `repeat` trigger; window it inside `{"all": [{"time": a}, {"not": {"time": b}}, {"every": s}]}` |
| `{"area": name, "who": name, "count": n or "all"}` | that many fighting men of `who` (default the player's side) in the area |
| `{"unit": name, "state": s}` | every man named is `active`, `down`, `dead`, `captured`, `out` (not fighting) or `alive` |
| `{"objective": id, "state": s}` | the objective is in that state (default `completed`) |
| `{"alarm": 0-2, "team": side}` | that side's alarm (default the enemy's) is at least this |
| `{"flag": name, "value": v}` | the flag equals v (no value: is not 0) |
| `{"alive": name, "below": n}` | fewer than n of them are still fighting |
| `{"body_found": n, "team": side}` | that side (default the enemy) has found n bodies (`true` = 1) |
| `{"cue_done": id}` | the cue has finished |
| `{"detected": true}` | the enemy has spotted one of the player's men |
| `{"destroyed": name}` | the object is destroyed |
| `{"charged": name}` | (v193) a charge is planted on the object and has not blown yet (fuse running, or waiting for the go) |
| `{"mobile": vehicle}` | (2026-10-14, after v246) the vehicle can drive under its own power: its tracks / wheels and engine work (repaired, see docs/BAIL-AND-REPAIR.md) and it is not a wreck. "Repair the tank" objectives: set them completed from a trigger on it |
| `{"stuck": name}` | (v122) the named vehicle is bogged down in soft ground (true until it rocks free) |
| `{"mission": "won" / "lost"}` | the mission ended so |
| `{"civilians_killed": n, "by": side}` | at least n civilians dead (killed by that side; no `by`: anyone) |

Actions:

| | |
|---|---|
| `{"objective": id, "state": s}` | show / complete / fail / hide an objective |
| `{"spawn": {squad}}` | a squad as in `forces` plus `"team"`; its `move_to` is where it heads (EV_REINFORCEMENTS) |
| `{"order": name, "move_to": [x, y], "mode": m, "roe": r, "ai": bool}` | orders to a squad or a side (a single man: `move_to` only) |
| `{"alarm": 1-2, "team": side}` | raise a side's alarm (default the enemy's) |
| `{"flag": name, "value": v}` | set a flag (default 1) |
| `{"cue": id}` | play a cue |
| `{"end": "won" / "lost", "text": "..."}` | end the mission now |
| `{"radio": "chatter" / "contact" / "alarm" / "reinforcements", "team": side}` | radio traffic for the renderer (EV_RADIO) |
| `{"enable": id}`, `{"disable": id}` | switch another trigger on or off |
| `{"surrender": unit / squad / side}` | (v62) they lay down their arms, as a capitulation; men aboard a vehicle hold fire instead |
| `{"vehicle": name, "speed": m/s, "move_to": [x, y], "halt": true, "dismount": true, "aim_at": [x, y], "deploy": [x, y], "recover": true, "attack": name|[x, y], "drop": [x, y]}` | (v129) a named vehicle: a top speed, a drive, a hard stop (the squad riding it stays with the stop), everyone out (its crew and a squad riding it); (v133) `aim_at` slews its turret there, gunner or not (a robot, an empty tank); (v138) `deploy`/`recover` set a stowed device out / take it back (by its `operator`); (v155) `attack` sends a strike drone diving on a man (a name) or a spot, `drop` releases a bomber's round on a spot |
| `{"sup": n, "at": [x, y], "heading": deg}` | a scripted fire-support strike on `at`: `n` indexes the top-level `support` array; `heading` (degrees, optional) aims `gun_run` / `air_bomb` runs. Always lands — ignores the entry's `uses` / `available` / `busy` and spends nothing; `delay` / `rounds` / `spread` still shape it. Pair with `{"every": s}` on a `repeat` trigger for ambient bombardment |

Example:

```json
"mission": {
  "name": "Silent Harvest",
  "areas": {"yard": {"circle": [66, 50, 10]}, "ford": {"rect": [2, 32, 26, 36]}},
  "cues": [{"id": "intro", "kind": "radio", "speaker": "HQ", "text": "The pilot is in the barn."}],
  "objectives": [
    {"id": "free", "kind": "free", "text": "Free the pilot", "target": "pilot"},
    {"id": "out", "kind": "extract", "text": "Get to the ford", "area": "ford", "with": "pilot", "state": "hidden"},
    {"id": "ghost", "kind": "undetected", "text": "Stay unseen", "optional": true}
  ],
  "triggers": [
    {"do": [{"cue": "intro"}]},
    {"when": {"objective": "free"}, "do": [{"objective": "out", "state": "active"}]},
    {"when": {"alarm": 2}, "delay": 90, "do": [{"spawn": {"team": "red", "size": 6, "at": [150, 10], "move_to": [66, 50]}}]}
  ]
}
```

**Music.** Every battle, mission or not, has a mood for the player's side
(`defil_mission(sim)->mood` and `->intensity`, EV_MOOD): `calm`, `stealth`
(sneaking, enemies near and unaware), `suspense` (enemies suspicious or
searching near us, or a detection meter past half), `combat_low`,
`combat_high` (pinned, outnumbered, men going down), `aftermath`, `victory`,
`defeat`. A tenser mood comes at once; a calmer one after it has held for
8 s. Intensity 0-100 moves smoothly, for layering stems.

## Saving

`defil_scenario_json(sim)` (or `defil_scenario save`) writes the scene as it
is now: the map's layers (`generator: none` plus `layers`), its objects as
`record_only` placements (with their names), and each surviving squad at
its centre (a squad of prisoners stays `captured`), with its names,
strength, experience, mode, fire rules and orders. Loading it rebuilds the
scene. It is not a full save game: wounds, ammunition, minds, the battle's
memory, and the wear and damage on cells are not kept (cells come back
intact, and rubble stays rubble). A building the town generator made (not an
object) no longer collapses after a reload. The `mission` block is written
back as it was loaded, without its progress: save a mission scene before it
starts (a squad a trigger already spawned would be there twice).

## Checking against the C API

`tests/scenarios/classic_town.json` gives the same battle as `defil_create(3, 24)`, and
`tests/scenarios/duel_open.json` the same as `defil_create_scenario(1, 1, 1, open, 8 pieces,
60 m gap)`. The tests check both.
