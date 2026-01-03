# agents/comparator.py
# agents/comparator.py
from deepdiff import DeepDiff

def compare_snapshots(old_text, new_text, min_change_size=200):
    diff = DeepDiff(
        old_text,
        new_text,
        ignore_order=True
    )

    if not diff:
        return None

    change_size = abs(len(new_text) - len(old_text))

    if change_size < min_change_size:
        return None  # ignore tiny changes

    return diff

