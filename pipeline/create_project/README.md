# Project creator

create_project.py is an independent launcher from pipeline/run.py. It creates a new project under pipeline/projects and reuses the pipeline's Stage 1 implementation from a JSON request.

```powershell
python pipeline/create_project/create_project.py request.json
```

Request fields:

- `name`: display name for the project.
- `source_path`: an existing file or directory containing source documents.
- `mode`: `local` or `cloud`.

For local mode, the script checks `http://127.0.0.1:11434`. If Ollama is not running, it automatically starts `ollama serve` and waits up to 20 seconds for it to become ready. You can also start it manually:

```powershell
ollama serve
ollama pull gemma3:4b
```

Keep `ollama serve` running in its own terminal, then run the creator in another terminal. The script prints progress messages such as validation, Ollama startup, file copying, and manifest creation to the terminal while it runs. The final success or error object is printed as JSON on standard output, so it can also be consumed by another tool. Cloud mode records OpenAI as the Stage 1 backend and does not require Ollama.

The source is copied into a generated project directory while excluding `.git`, virtual environments, `node_modules`, and Python caches. After copying, the script invokes the same `execute_reasoner_stage_1` function and prompt used by the UI pipeline, so extraction behavior and output files are identical. The resulting project remains under `pipeline/projects` with `meta.json`, `project_manifest.json`, `run.jsonl`, and Stage 1 files in `workspace/extracted/`; the running UI discovers it automatically. Both manifest files include the extraction status and details.


