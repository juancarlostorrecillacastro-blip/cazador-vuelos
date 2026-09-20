# Flight Deal Hunter

[![Tests](https://github.com/juancarlostorrecillacastro-blip/cazador-vuelos/actions/workflows/tests.yml/badge.svg)](https://github.com/juancarlostorrecillacastro-blip/cazador-vuelos/actions/workflows/tests.yml)

An automation that watches flights from Málaga (AGP) and Sevilla (SVQ) to anywhere in the world, uses Claude to judge whether a price is an actual bargain (not just "cheap"), and pings Telegram when it finds one. A local panel turns the whole thing on and off.

Built as a learning project to practice clean separation between business logic, I/O boundaries, and testable code, while shipping something genuinely useful.

## What it does

Every hour (or on demand), for each origin airport:

1. Fetches the 15 cheapest fares to anywhere in the world, any dates, via the [Travelpayouts Data API](https://www.travelpayouts.com/).
2. Asks Claude (Anthropic API) to judge each one: is this genuinely a bargain for that route, not just "a cheap-looking number"?
3. For the ones Claude flags as real deals, checks whether it's cheaper than the last deal already notified for that route — so it won't repeat itself.
4. Sends a Telegram message with the price, dates, airline and a booking link, plus Claude's one-line reasoning.

Example alert:

```
Chollo AGP -> STN
Precio: 27 EUR
Ida: 12/11/2026 - directo - FR
Vuelta: 16/11/2026
Por que: muy por debajo del precio habitual para esta ruta
https://www.aviasales.com/search/...
```

A local web panel turns the automation on and off:

```bash
python -m flight_hunter.web
```

It flips the GitHub Actions schedule on/off via the GitHub API — no routes to configure, no prices to set. While it's on, it checks every hour; while it's off, it does nothing.

## Architecture

Each module has exactly one job, split deliberately into **pure logic** (no network, no disk — trivially unit-tested) and **I/O boundaries** (talk to the outside world, verified by hand against the real services):

| Module | Responsibility | Kind |
|---|---|---|
| `config.py` | Loads credentials from `.env` | I/O |
| `api_client.py` | Fetches the cheapest fares to anywhere from an origin, via Travelpayouts | I/O |
| `ai_judge.py` | Asks Claude whether a price is a genuine bargain | Pure logic (parsing) + I/O |
| `deal_finder.py` | Decides if a price is worth a new alert (vs. the last one notified) | Pure logic |
| `storage.py` | Persists the best price already notified per route (SQLite) | I/O |
| `notifier.py` | Builds the alert text and sends it via the Telegram Bot API | Pure logic + I/O |
| `automation_control.py` | Reads/flips the GitHub Actions schedule on/off | I/O |
| `web.py` | Local Flask on/off panel | I/O |
| `main.py` | Wires everything together into one run | Orchestration |

This split matters in practice: `deal_finder.py`'s decisions, `notifier.py`'s message formatting, and `ai_judge.py`'s response parsing are covered by fast unit tests with no network calls, while the modules that actually talk to Travelpayouts, Anthropic, Telegram and GitHub were verified by hand against the real services during development.

## Tech stack

- Python 3.12+
- [Travelpayouts Data API](https://www.travelpayouts.com/) — cheapest fares to anywhere from an airport
- [Anthropic API](https://console.anthropic.com/) (Claude Haiku) — judges whether a price is a real bargain
- Telegram Bot API for notifications
- SQLite (stdlib `sqlite3`) for the seen-deals history
- Flask for the local on/off panel
- GitHub Actions for scheduling, controlled remotely via the GitHub REST API
- pytest for the test suite

## Project structure

```
cazador_vuelos/
├── .github/workflows/
│   ├── check-deals.yml   # scheduled + manual search run
│   └── tests.yml         # runs pytest on every push/PR
├── src/flight_hunter/
│   ├── config.py
│   ├── api_client.py
│   ├── ai_judge.py
│   ├── deal_finder.py
│   ├── storage.py
│   ├── notifier.py
│   ├── automation_control.py
│   ├── web.py
│   ├── templates/index.html
│   └── main.py
├── tests/
├── requirements.txt / requirements-dev.txt
└── pyproject.toml
```

## Getting started

**1. Clone and set up a virtual environment**

```bash
git clone https://github.com/juancarlostorrecillacastro-blip/cazador-vuelos.git
cd cazador-vuelos
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash; use .venv\Scripts\activate on cmd/PowerShell
pip install -r requirements-dev.txt
pip install -e .
```

**2. Get a Travelpayouts API token**

Sign up at [travelpayouts.com](https://www.travelpayouts.com/), create a project (any personal profile/site link works as the "traffic source"), then grab your token from Profile → API token.

**3. Create a Telegram bot**

Message [@BotFather](https://t.me/BotFather) on Telegram, send `/newbot`, and follow the prompts to get a bot token. Then message your new bot once, and visit `https://api.telegram.org/bot<TOKEN>/getUpdates` to find your `chat.id`.

**4. Get an Anthropic API key**

Create one at [console.anthropic.com](https://console.anthropic.com/). Used with the cheapest model (Haiku) for a short yes/no classification, cost is negligible at this volume.

**5. Configure credentials**

```bash
cp .env.example .env
```

Fill in `TRAVELPAYOUTS_TOKEN`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` and `ANTHROPIC_API_KEY`.

**6. (Optional) Enable the on/off panel**

`GITHUB_TOKEN` and `GITHUB_REPO` in `.env` are only needed to run the local panel (`python -m flight_hunter.web`), never by GitHub Actions itself. Create a [fine-grained personal access token](https://github.com/settings/personal-access-tokens) scoped to just this repo, with **Actions: Read and write** permission — nothing more.

## Running it

```bash
python -m flight_hunter.main
```

## Running the tests

```bash
pytest tests/ -v
```

## Automation

A GitHub Actions workflow (`.github/workflows/check-deals.yml`) runs the search every hour and can also be triggered manually from the Actions tab. It needs these repository secrets set under **Settings → Secrets and variables → Actions**:

- `TRAVELPAYOUTS_TOKEN`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `ANTHROPIC_API_KEY`

Since GitHub Actions runners are ephemeral (no disk survives between runs), the workflow saves and restores `deals.db` via `actions/cache` so the "already notified" history carries over between executions.

The local panel (`python -m flight_hunter.web`) enables/disables this workflow through the GitHub REST API — turning it "off" means GitHub simply won't fire the scheduled runs until switched back on. The change takes effect immediately, but the next actual search still happens on the next hourly tick (or via a manual trigger from the Actions tab).

## Possible improvements

- A price-history dashboard (charts over time per destination)
- Multiple notification channels (email, Discord)
- More origin airports, configurable from the panel instead of hardcoded
- Two-stage filtering (a cheap price-per-km heuristic first, only sending the top candidates to Claude) to reduce API calls

## License

MIT — see [LICENSE](LICENSE).
