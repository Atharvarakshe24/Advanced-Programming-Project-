import json
from pathlib import Path
from threading import Lock
import uuid

DATA_FILE = Path(__file__).with_name("media.json")
_lock = Lock()


def load_data():
    """Load and return list of media items from JSON file."""
    if not DATA_FILE.exists():
        return []
    try:
        with DATA_FILE.open('r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return []

    # Ensure every item has an id
    updated = False
    for item in data:
        if 'id' not in item:
            item['id'] = str(uuid.uuid4())
            updated = True
    if updated:
        save_data(data)
    return data


def save_data(data):
    """Persist list of media items to JSON file."""
    with _lock:
        with DATA_FILE.open('w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def list_all():
    return load_data()


def list_by_category(category):
    if not category or category == 'All':
        return list_all()
    return [m for m in load_data() if m.get('category') == category]


def get_by_id(item_id):
    for m in load_data():
        if str(m.get('id')) == str(item_id):
            return m
    return None


def search_by_name_exact(name):
    if not name:
        return None
    name = name.strip()
    for m in load_data():
        if m.get('name') == name:
            return m
    return None


def create_item(item):
    d = load_data()
    if 'id' not in item:
        item['id'] = str(uuid.uuid4())
    d.append(item)
    save_data(d)
    return item


def delete_item(item_id):
    d = load_data()
    for i, m in enumerate(d):
        if str(m.get('id')) == str(item_id):
            removed = d.pop(i)
            save_data(d)
            return removed
    return None


def update_item(item_id, new_values):
    d = load_data()
    for i, m in enumerate(d):
        if str(m.get('id')) == str(item_id):
            # preserve id
            new = {**m, **new_values}
            new['id'] = m.get('id')
            d[i] = new
            save_data(d)
            return new
    return None
