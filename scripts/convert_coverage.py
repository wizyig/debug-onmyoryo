from pathlib import Path
import json

DEFAULT_REQUIRED = 85.0

def load_changed_files(changed_file="artifacts/changed_files.txt"):
    path = Path(changed_file)
    if not path.exists():
        return set()
    return {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}

def convert(source="coverage.json", target="artifacts/coverage.json", changed_file="artifacts/changed_files.txt"):
    with open(source, encoding="utf-8") as f:
        raw = json.load(f)
    changed = load_changed_files(changed_file)
    modules = {}
    changed_files = {}
    for file_path, data in raw.get("files", {}).items():
        percent = round(data["summary"]["percent_covered"], 2)
        file_name = Path(file_path).name
        modules[file_name] = percent
        if file_path in changed:
            changed_files[file_name] = {"coverage": percent, "required": DEFAULT_REQUIRED}
    result = {
        "global": round(raw["totals"]["percent_covered"], 2),
        "modules": modules,
        "changed_files": changed_files,
    }
    Path(target).parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    return result

if __name__ == "__main__":
    convert()
