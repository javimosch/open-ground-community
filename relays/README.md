# Community relays

Relays run by players for Open Ground co-op. The official relays read this file every hour, probe each entry and hand the live ones to
every game, where they show as **community relay**.

## Add yours

1. Run a relay: see [open-ground-relay](https://github.com/javimosch/open-ground-relay), `sudo ./install.sh XFR1`.
2. Add an entry to `relays.json` and open a pull request:

```json
{ "id": "XFR1", "host": "relay.example.org", "port": 47160, "owner": "your GitHub name", "contact": "how to reach you", "added": "2026-11-07" }
```

- `id`: 2-6 capital letters or digits, a letter first, not already in the file and not an official id (`EU`, `US`, ...). It starts every
  join code made on your relay, so pick something short (a country and a number works: `XFR1`, `PL2`).
- The relay must answer `OGR1 PROBE` with `PROBE <id>`: the check on your pull request tries it.

## Rules

Read the relay README's rules. Entries that stop answering are marked `"status": "down"` by the nightly check and removed after a month;
an owner can set `"status": "disabled"` to leave the list without losing the id.
