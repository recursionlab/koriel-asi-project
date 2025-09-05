import json, pathlib
pathlib.Path("ops").mkdir(exist_ok=True)
b = {
    "context_file": "docs/CONTEXT.md",
    "system_prompt": "prompts/system.md",
    "agents_config": "prompts/agents.jsonl",
    "version": "v0.1",
}
pathlib.Path("ops/context_bundle.json").write_text(json.dumps(b, indent=2))
