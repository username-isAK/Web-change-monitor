def extract_changes(diff, max_chars=3000):
    changes = []

    if "values_changed" in diff:
        for change in diff["values_changed"].values():
            changes.append(
                f"[MODIFIED]\nOLD:\n{change['old_value']}\n\nNEW:\n{change['new_value']}"
            )

    if "iterable_item_added" in diff:
        for para in diff["iterable_item_added"].values():
            changes.append(
                f"[ADDED]\n{para}"
            )

    if "iterable_item_removed" in diff:
        for para in diff["iterable_item_removed"].values():
            changes.append(
                f"[REMOVED]\n{para}"
            )

    combined = "\n\n---\n\n".join(changes)
    return combined[:max_chars]
