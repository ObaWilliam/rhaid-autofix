import os, json, hashlib, logging

BASELINE_NAME = "rhaid_baseline.json"

def _root_dir(start: str) -> str:
    return os.path.abspath(start if os.path.isdir(start) else os.path.dirname(start))

def _fp(path: str) -> str:
    return os.path.join(_root_dir(path), BASELINE_NAME)

def issue_fingerprint(path: str, rid: str, msg: str) -> str:
    h = hashlib.sha1()
    h.update((path + "\n" + rid + "\n" + msg.strip()).encode("utf-8", "ignore"))
    return h.hexdigest()

def write_baseline(start_path: str, flat: list) -> str:
    root = _root_dir(start_path)
    outp = os.path.join(root, BASELINE_NAME)
    data = {
        "fingerprints": sorted(
            {issue_fingerprint(i["path"], i["id"], i["message"]) for i in flat}
        )
    }
    try:
        with open(outp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Failed to write baseline: {e}")
    return outp

def load_baseline(start_path: str) -> set:
    p = _fp(start_path)
    if not os.path.isfile(p):
        return set()
    try:
        with open(p, "r", encoding="utf-8") as f:
            return set(json.load(f).get("fingerprints", []))
    except Exception as e:
        logging.error(f"Failed to load baseline: {e}")
        return set()

def filter_new_against_baseline(start_path: str, flat: list) -> list:
    # ...rest of function unchanged...
    pass  # placeholder
