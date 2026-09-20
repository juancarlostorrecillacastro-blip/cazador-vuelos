# Flight Deal Hunter

[![Tests](https://github.com/juancarlostorrecillacastro-blip/cazador-vuelos/actions/workflows/tests.yml/badge.svg)](https://github.com/juancarlostorrecillacastro-blip/cazador-vuelos/actions/workflows/tests.yml)

A small automation that watches flight routes and pings you on Telegram the moment a price drops below a threshold you set — and never bugs you twice about the same deal.

Built as a learning project to practice clean separation between business logic, I/O boundaries, and testable code, while shipping something genuinely useful.

## What it does

Every hour (or on demand), the program:

1. Checks the cheapest fare for each route you're watching (round-trip or one-way, with flexible month-level dates — "cheapest in November", not a fixed day) via the [Travelpayouts Data API](https://www.travelpayouts.com/).
2. Compares it against the maximum price you configured for that route.
3. If it's a deal **and** it's cheaper than the last deal it already told you about for that route/month, sends a Telegram message with the price, dates, airline and a booking link.
4. Remembers the best price it has already notified you about per route *and* month combination, so re-running it doesn't spam you with the same deal.

Example alert:

```
Oferta MAD -> LON
Precio: 44 EUR
Ida: 05/11/2026 - directo - FR
Vuelta: 08/11/2026 - directo
https://www.aviasales.com/search/...
```

Routes are managed through a small local web form — no need to hand-edit YAML or memorize IATA airport codes: type a city name, pick departure/return months from a date picker, set a max price, and it's saved.

## Architecture

Each module has exactly one job, split deliberately into **pure logic** (no network, no disk — trivially unit-tested) and **I/O boundaries** (talk to the outside world, verified by hand against the real services):

| Module | Responsibility | Kind |
|---|---|---|
| `config.py` | Loads credentials (`.env`) and watched routes (`config.yaml`) | I/O |
| `api_client.py` | Fetches the cheapest fare for a route from Travelpayouts | I/O |
| `deal_finder.py` | Decides if a price counts as a deal, and if it's worth a new alert | Pure logic |
| `storage.py` | Persists the best price already notified per route + month (SQLite) | I/O |
| `notifier.py` | Builds the alert text and sends it via the Telegram Bot API | Pure logic + I/O |
| `airports.py` | Loads the bundled city/airport list used by the web form | I/O |
| `route_manager.py` | Parses form input into a route, reads/writes `config.yaml` | Pure logic + I/O |
| `web.py` | Local Flask form to add/remove watched routes | I/O |
| `main.py` | Wires everything together into one run | Orchestration |

This split matters in practice: `deal_finder.py`'s decisions and `notifier.py`'s message formatting are covered by fast unit tests with no network calls, while the modules that actually talk to Travelpayouts and Telegram were verified against the real APIs during development.

## Tech stack

- Python 3.12+
- [Travelpayouts Data API](https://www.travelpayouts.com/) for fares (round-trip, flexible month search)
- Telegram Bot API for notifications
- SQLite (stdlib `sqlite3`) for the seen-deals history
- Flask for the local route-management form
- GitHub Actions for scheduling (cron + manual trigger), with `actions/cache` to persist the SQLite file between ephemeral runs
- pytest for the test suite

## Project structure

```
cazador_vuelos/
├── .github/workflows/check-deals.yml   # scheduled + manual GitHub Actions run
├── config/
│   └── config.yaml                     # routes and price thresholds you're watching
├── src/flight_hunter/
│   ├── config.py
│   ├── api_client.py
│   ├── deal_finder.py
│   ├── storage.py
│   ├── notifier.py
│   ├── airports.py
│   ├── route_manager.py
│   ├── web.py
│   ├── data/cities.json                # bundled city/airport list for the form
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

**4. Configure credentials**

```bash
cp .env.example .env
```

Fill in `TRAVELPAYOUTS_TOKEN`, `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` (`TRAVELPAYOUTS_MARKER` is optional).

**5. Set your routes**

Run the local web form:

```bash
python -m flight_hunter.web
```

Open `http://127.0.0.1:5000`, type a city name (it autocompletes to the right airport code), pick departure/return months, set a max price, and save. Prefer editing by hand? `config/config.yaml` is plain YAML — see `config/config.example.yaml` for the field reference. Note: saving through the form rewrites the file, so any comments you added by hand will be lost on the next save.

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
- `TRAVELPAYOUTS_MARKER` (optional)
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Since GitHub Actions runners are ephemeral (no disk survives between runs), the workflow saves and restores `deals.db` via `actions/cache` so the "already notified" history carries over between executions.

## Possible improvements

- A price-history dashboard (charts over time per route), separate from the route-management form
- Multiple notification channels (email, Discord)
- Wildcard "cheapest anywhere from X" search instead of fixed routes
- Preserve comments in `config.yaml` when saving from the web form (would need `ruamel.yaml` instead of plain `PyYAML`)

## License

MIT — see [LICENSE](LICENSE).
