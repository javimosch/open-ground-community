# Open Ground modkit

Make your own missions, factions and props for **Open Ground**. A mod is a folder of JSON and art: no code, nothing runs on your machine but the game.

## Install a mod (players)

1. In the game: **Expansions > MODS > Open mods folder**.
2. Drop the mod's folder there. Its name is `<author>.<name>` and it holds a `pack.json`.
3. Back in the game press **Apply & restart**. Its missions appear on the Missions page, tagged "Mod:".

Expansions (DLC) work alike: **Expansions > EXPANSIONS > Open expansions folder**, drop the folder in, restart. One expansion is active at a time; mods can run beside it.

Disable a mod the same way: MODS > Disable > Apply & restart.

## Make a mod (authors)

1. Copy `example-mod/example.hello_ground/` and rename the folder `<yourname>.<yourmod>` (a-z, 0-9, `_`). Set the same `id` in `pack.json`.
2. Edit `scenarios/hello_ground.json`. The formats are in `docs/packs.md` (the pack: ids, files, art budgets) and `docs/scenarios.md` (maps, forces, missions, triggers).
`example-dlc/example_dlc/` is the same as an expansion (id `a-z0-9_`, `"kind": "dlc"`).
3. Everything your mod adds is named `<yourname>.<yourmod>.<thing>`: this keeps mods from clashing.
4. Check it: download the validator for your system from the Releases page (`og-validators-windows.zip` or `og-validators-linux.tar.gz`), put your mod in a folder `mods/` (an expansion in `dlc/`), and run `defil_content_check <that folder>` (`defil_scenario check <file>` checks one scenario file). It says what is wrong, with a "did you mean" for typos. Or load it in the game.

Rules in one line each: data only (`.json`, `.glb`, `.png`, `.jpg`, `.wav`, `.ogg`), nothing outside the folder, a mod adds and never replaces the game's content, unknown keys are errors (with a "did you mean").

## Share

Zip the mod folder and post it. Please keep to the playtest rules: no real people, slogans or logos.

This repository is a one-way copy of files from the game's source; send fixes as issues.
