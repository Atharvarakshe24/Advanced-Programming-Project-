import os
import tempfile
import json
import storage


def test_storage_add_and_delete(tmp_path, monkeypatch):
    # Use a temporary media.json for testing
    tmp_file = tmp_path / 'media.json'
    monkeypatch.setattr(storage, 'DATA_FILE', tmp_file)

    # Start empty
    assert storage.list_all() == []

    # Create item
    item = {'name': 'Test Book', 'author': 'Me', 'date': '2025', 'category': 'Novel'}
    created = storage.create_item(item)
    assert 'id' in created

    # Now load and check
    all_items = storage.list_all()
    assert len(all_items) == 1
    assert all_items[0]['name'] == 'Test Book'

    # Delete it
    removed = storage.delete_item(created['id'])
    assert removed is not None
    assert storage.list_all() == []
