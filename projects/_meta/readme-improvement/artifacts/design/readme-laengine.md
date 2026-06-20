<!--
  LAENGINE — Game development capability for LAOS
  README.md  |  github.com/laurentaf/laengine
  Brand: Brasfoot-style match simulation, Brazilian football
  Tone: Energetic, confident, playful but precise.
  Adapted from the LAOS README (20/20) inline-HTML pattern.
-->

<div align="center" style="margin-top:48px;margin-bottom:24px;">

<!-- Emblem: football + joystick cross -->
<svg width="72" height="72" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom:4px;">
  <rect x="4" y="4" width="56" height="56" rx="12" stroke="#D63031" stroke-width="1.5" fill="none" opacity="0.3"/>
  <!-- Ball arc -->
  <circle cx="32" cy="28" r="10" stroke="#D63031" stroke-width="2.5" fill="none" opacity="0.3"/>
  <path d="M22 28 Q28 22 32 24 Q36 26 42 28" stroke="#D63031" stroke-width="2" fill="none" opacity="0.3"/>
  <!-- Cross/joystick -->
  <rect x="30" y="40" width="4" height="18" rx="2" fill="#D63031" opacity="0.7"/>
  <rect x="24" y="44" width="16" height="4" rx="2" fill="#D63031" opacity="0.7"/>
  <!-- Pulse dots -->
  <circle cx="28" cy="27" r="1.5" fill="#D63031" opacity="0.5"/>
  <circle cx="36" cy="27" r="1.5" fill="#D63031" opacity="0.5"/>
</svg>

<br/>

# LAENGINE
### Sports Simulation · Squad Management · League Engine

<p style="margin:12px 0;">
  <img src="https://img.shields.io/badge/Python-%E2%89%A53.11-3776AB?style=flat&logo=python&logoColor=fff" alt="Python 3.11+"/>
  &nbsp;
  <img src="https://img.shields.io/badge/Status-BASIC-fdcb6e?style=flat" alt="Status: BASIC"/>
  &nbsp;
  <img src="https://img.shields.io/badge/License-MIT-31c754?style=flat" alt="License: MIT"/>
  &nbsp;
  <img src="https://img.shields.io/badge/MCP-7%20tools-a29bfe?style=flat" alt="7 MCP tools"/>
  &nbsp;
  <a href="https://github.com/laurentaf/laos"><img src="https://img.shields.io/badge/Ecosystem-LAOS-6c5ce7?style=flat" alt="LAOS Ecosystem"/></a>
</p>

<hr style="width:48px;margin:24px auto;border:none;border-top:2px solid #D63031;opacity:0.3;"/>

</div>

> **Brasfoot-style football simulation, engineered for agents.**  
> LAENGINE generates synthetic Brazilian teams with realistic attributes, simulates matches with play-by-play text commentary, runs full round-robin leagues, and exposes every operation through MCP tools. Built for LAOS — playable by any coding agent.

---

## What LAENGINE Is

LAENGINE is the game development capability for the LAOS ecosystem. It brings **Brasfoot-style match simulation** to the MCP protocol — synthetic team/player generation, match simulation with rich text commentary, round-robin scheduling, and live league standings.

**Why LAENGINE exists:** Game simulation is a stress test for agentic systems. It requires stateful orchestration, deterministic randomness, and real-time data flow. If LAOS can run a football league, it can run anything.

---

## Architecture

<div align="center" style="margin:24px 0;">

<table style="border-collapse:separate;border-spacing:0;min-width:560px;">
  <tr>
    <td colspan="3" align="center" style="padding:0 0 8px 0;">
      <div style="display:inline-block;border:1.5px solid #D63031;border-radius:8px;padding:12px 24px;text-align:center;">
        <div style="font-weight:700;font-size:1em;letter-spacing:0.04em;color:#D63031;">LAENGINE MCP Server</div>
        <div style="font-size:0.8em;opacity:0.5;">Python · Flask · MCP Protocol</div>
      </div>
    </td>
  </tr>
  <tr>
    <td colspan="3" align="center" style="padding:0;">
      <div style="width:1.5px;height:16px;background:#D63031;opacity:0.2;margin:0 auto;"></div>
    </td>
  </tr>
  <tr>
    <td align="center" style="padding:0 8px;width:33%;">
      <div style="border:1px solid #D63031;border-radius:6px;padding:8px 14px;text-align:center;">
        <div style="font-weight:600;font-size:0.85em;letter-spacing:0.02em;">Data Generation</div>
        <div style="font-size:0.7em;opacity:0.5;">Teams · Players<br/>Attributes · Rosters</div>
      </div>
    </td>
    <td align="center" style="padding:0 8px;width:33%;">
      <div style="border:1px solid #fdcb6e;border-radius:6px;padding:8px 14px;text-align:center;">
        <div style="font-weight:600;font-size:0.85em;letter-spacing:0.02em;">Match Engine</div>
        <div style="font-size:0.7em;opacity:0.5;">90-min simulation<br/>Text commentary · Events</div>
      </div>
    </td>
    <td align="center" style="padding:0 8px;width:33%;">
      <div style="border:1px solid #D63031;border-radius:6px;padding:8px 14px;text-align:center;">
        <div style="font-weight:600;font-size:0.85em;letter-spacing:0.02em;">League Management</div>
        <div style="font-size:0.7em;opacity:0.5;">Round-robin schedule<br/>Standings · Results</div>
      </div>
    </td>
  </tr>
</table>

</div>

```
laengine/
├── src/laengine/
│   ├── brasfoot/
│   │   ├── models.py    (Team, Player, Match, MatchEvent, Standings)
│   │   ├── data.py      (synthetic team/player generation)
│   │   └── engine.py    (schedule, simulation, standings)
│   └── mcp/
│       └── server.py    ← MCP server exposing game tools
├── skills/
│   └── game-ui-skill.md ← Design patterns for game UIs
└── pyproject.toml
```

---

## MCP Tools

<table style="width:100%;border-collapse:separate;border-spacing:0;font-size:0.9em;">
  <tr style="border-bottom:1px solid #D63031;border-bottom-opacity:0.2;">
    <th align="left" style="padding:10px 14px;font-weight:600;opacity:0.5;width:25%;">Tool</th>
    <th align="left" style="padding:10px 14px;font-weight:600;opacity:0.5;">Description</th>
  </tr>
  <tr>
    <td style="padding:8px 14px;font-weight:500;"><code>generate_seed</code></td>
    <td style="padding:8px 14px;opacity:0.7;">Generate 10 Brazilian football teams with realistic attributes</td>
  </tr>
  <tr>
    <td style="padding:8px 14px;font-weight:500;"><code>get_teams</code></td>
    <td style="padding:8px 14px;opacity:0.7;">List all teams with full squad details</td>
  </tr>
  <tr>
    <td style="padding:8px 14px;font-weight:500;"><code>get_team_players</code></td>
    <td style="padding:8px 14px;opacity:0.7;">Get the player roster for a specific team</td>
  </tr>
  <tr>
    <td style="padding:8px 14px;font-weight:500;"><code>generate_schedule</code></td>
    <td style="padding:8px 14px;opacity:0.7;">Create a round-robin schedule (turno + returno)</td>
  </tr>
  <tr>
    <td style="padding:8px 14px;font-weight:500;"><code>simulate_next_round</code></td>
    <td style="padding:8px 14px;opacity:0.7;">Simulate the next pending round with full commentary</td>
  </tr>
  <tr>
    <td style="padding:8px 14px;font-weight:500;"><code>simulate_all_rounds</code></td>
    <td style="padding:8px 14px;opacity:0.7;">Simulate the entire season in one call</td>
  </tr>
  <tr>
    <td style="padding:8px 14px;font-weight:500;"><code>get_standings</code></td>
    <td style="padding:8px 14px;opacity:0.7;">Get current league table with points, goals, and form</td>
  </tr>
</table>

---

## Game Output Preview

When `simulate_next_round` runs, LAENGINE produces play-by-play text commentary:

```
🏁 FIM DE JOGO! Corinthians 2 x 3 Palmeiras 
  ⚽ Aos 12' - QUE GOL! Yuri Alberto recebe na área, gira e chuta 
    no ângulo! GOL DO CORINTHIANS!
  🧤 Aos 34' - Weverton faz uma defesa espetacular! Evita o gol.
  🟨 Aos 56' - Cartão amarelo! Murilo para o contra-ataque.
  ⚽ Aos 67' - GOLAÇO! Raphael Veiga domina no peito e bate colocado!
  ⚽ Aos 90+3' - GOOOOOOL! Palmeiras vira nos acréscimos! É de 
    matar o coração!
```

League standings update automatically after each simulated round:

| # | Time | Pts | J | V | E | D | SG |
|---|------|:---:|:-:|:-:|:-:|:-:|:--:|
| 1 | Palmeiras | 42 | 18 | 13 | 3 | 2 | +24 |
| 2 | Corinthians | 38 | 18 | 11 | 5 | 2 | +18 |
| 3 | São Paulo | 35 | 18 | 10 | 5 | 3 | +12 |
| 4 | Santos | 31 | 18 | 9 | 4 | 5 | +8 |

---

## Quick Start

```bash
# Clone and install
git clone https://github.com/laurentaf/laengine.git
cd laengine
uv sync

# Start the MCP server (for LAOS orchestration)
uv run laengine-server

# Or use directly as a Python library
uv run python -c "
from laengine.brasfoot import gerar_times, simular_partida
times = gerar_times()
print(f'{len(times)} times gerados')
"
```

### Requirements

<table style="font-size:0.85em;border-collapse:separate;border-spacing:0;">
  <tr><td style="padding:6px 12px;font-weight:500;">Python</td><td style="padding:6px 12px;opacity:0.6;">≥ 3.11</td></tr>
  <tr><td style="padding:6px 12px;font-weight:500;">Dependencies</td><td style="padding:6px 12px;opacity:0.6;">mcp, pydantic, flask, flask-cors</td></tr>
  <tr><td style="padding:6px 12px;font-weight:500;">Launcher</td><td style="padding:6px 12px;opacity:0.6;"><code>uv run laengine-server</code> starts the MCP server</td></tr>
</table>

---

## Contributing

LAENGINE is a LAOS capability. Changes follow the ecosystem governance model:

| Scope | Path |
|-------|------|
| **New feature** | LACOUNCIL proposal → Conselho majority → implement |
| **Bug fix** | Open an [issue](https://github.com/laurentaf/laengine/issues) or submit a PR |
| **Documentation** | PR with description — no gate required |

See the [LAOS governance model](https://github.com/laurentaf/laos) for full details.

---

## License

<div style="margin:16px 0;">

**MIT** — see [`LICENSE`](https://github.com/laurentaf/laengine/blob/main/LICENSE) for the full text.

LAENGINE is free software. Use it to build leagues, simulate seasons, and bring football simulation to any agent that speaks MCP.

</div>

---

<div align="center" style="margin:36px 0;opacity:0.25;font-size:0.8em;">
<svg width="28" height="28" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom:4px;">
  <rect x="4" y="4" width="56" height="56" rx="12" stroke="#D63031" stroke-width="1.5" fill="none" opacity="0.15"/>
  <circle cx="32" cy="28" r="10" stroke="#D63031" stroke-width="2.5" fill="none" opacity="0.3"/>
  <rect x="30" y="40" width="4" height="18" rx="2" fill="#D63031" opacity="0.4"/>
  <rect x="24" y="44" width="16" height="4" rx="2" fill="#D63031" opacity="0.4"/>
</svg>
<br/>
LAENGINE — part of the <a href="https://github.com/laurentaf/laos" style="text-decoration:none;">LAOS</a> ecosystem
</div>
