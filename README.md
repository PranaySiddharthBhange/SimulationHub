# SimulationHub

Turns engineering documents into a verified simulation: it reads your source
documents, merges them into one brief, asks you about any open decisions,
writes a SysML v2 model, and compiles/runs a verified Modelica simulation.
Stage 1 (document understanding); Merge, Stage 2
(SysML generation) and Stage 3 (simulation + validation) use OpenAI.

The whole app -- backend API, pipeline, and web UI -- lives under
[`pipeline/`](pipeline/).

## Prerequisites

- Windows or Linux (macOS is not automated by `setup.py`, but `run.py` works
  the same way once dependencies are installed manually)
- Internet access for the one-time setup step below

Everything else (Python, Node.js, OpenModelica, the SysML v2 parser, Ollama)
is handled for you by the setup script.

## 1. One-time setup

From the repo root:

```
python setup.py
```

This scans what you already have installed, tells you what's missing (with
approximate download size), and lets you pick what to install. It sets up,
in dependency order:

1. OpenModelica compiler (`omc`) -- used to compile/run the simulation
2. The real SysML v2 parser (a `sysml` conda environment)
3. Node.js / npm -- needed for the frontend
4. Docker -- needed for the SysML v2 viewer
5. The SysML v2 viewer (SysON), started via `docker compose up -d` in
   [`sysml_setup/`](sysml_setup/)
6. Frontend npm packages (`pipeline/frontend/node_modules`)
7. This repo's own Python environment (`pipeline/.venv` + `pip install -e .[dev]`)
8. `pipeline/.env`, copied from `pipeline/.env.example`

Nothing already present is touched or reinstalled. You can re-run
`python setup.py` any time to pick up anything you skipped.

### Ollama and its model

Ollama itself isn't installed by `setup.py` -- install it separately from
[ollama.com/download](https://ollama.com/download) if you want local Stage 1
extraction. `run.py` (see below) will ask whether you have it running and
pull the configured model (`gemma3:4b` by default) automatically if it's
missing. If you skip Ollama, Stage 1 falls back to the Cloud (OpenAI)
extraction backend instead -- see below.

### API key

Stage 1 can run fully locally via Ollama, but Merge, Stage 2, and Stage 3
always call OpenAI. Open `pipeline/.env` after setup and add:

```
OPENAI_API_KEY=sk-...
```

Never paste your key into chat or commit it -- `pipeline/.env` is already
git-ignored.

## 2. Run the app

From the repo root:

```
pipeline\.venv\Scripts\python.exe pipeline\run.py      (Windows)
pipeline/.venv/bin/python pipeline/run.py               (Linux)
```

(equivalently, from inside `pipeline/`: `.venv/Scripts/python.exe run.py` /
`.venv/bin/python run.py`)

This single launcher:

1. Loads `pipeline/.env`
2. Checks whether Ollama is already running; if not, asks whether you have
   it installed and want to use it locally -- answer no and it skips Ollama
   and continues with the Cloud (OpenAI) backend for Stage 1 instead
3. If using Ollama, starts it and pulls the configured model if it's missing
4. Starts the backend API and the frontend dev server
5. Waits for both to become ready, then opens the UI in your browser

Press `Ctrl+C` to stop everything the launcher started. If a port is already
occupied by another instance, it automatically tries the next one.

## Project structure

```
pipeline/            the application (backend, pipeline, frontend, run.py)
  src/                Python backend + simulation pipeline
  frontend/           React + Vite web UI
  run.py              one-command launcher
  .env.example        configuration template
sysml_setup/          docker-compose for the SysON SysML v2 viewer
process_docs/         project decisions / working notes
test cases/           sample document sets for exercising the pipeline
setup.py              one-time environment setup (see above)
```
