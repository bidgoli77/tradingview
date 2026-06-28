import json

def log_event(title: str, payload: dict | None = None):
    print('=' * 70)
    print(title)
    if payload is not None:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    print('=' * 70)
