from pathlib import Path

cwd = Path(__file__).parent.parent
UNSAFES_BASE = set(filter(bool, open(cwd/'localutils/unsafes/base.txt', 'r', encoding='utf-8').read().split()))
UNSAFES_ROOT = set(filter(bool, open(cwd/'localutils/unsafes/root.txt', 'r', encoding='utf-8').read().split())) | UNSAFES_BASE
UNSAFES_USER = set(filter(bool, open(cwd/'localutils/unsafes/user.txt', 'r', encoding='utf-8').read().split())) | UNSAFES_BASE


def safe_private_filename(filepath: Path) -> Path | None:
    filename = str(filepath).lower()
    for unsafe in UNSAFES_ROOT:
        if unsafe in filename:
            return None # unsafe hit
    return filepath # safe pass


def safe_global_filename(filename) -> str|None:
    for unsafe in UNSAFES_USER:
        if unsafe == filename.split('.')[-1].strip().lower():
            return unsafe # unsafe hit
    return None # safe pass
