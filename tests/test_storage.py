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


def test_storage_update_and_filters(tmp_path, monkeypatch):
    """Ensure update, category filter, and name search work together."""
    tmp_file = tmp_path / 'media.json'
    monkeypatch.setattr(storage, 'DATA_FILE', tmp_file)

    # Seed two items in different categories
    item1 = storage.create_item({'name': 'Dune', 'author': 'Frank Herbert', 'date': '1965', 'category': 'SciFi'})
    item2 = storage.create_item({'name': 'Sapiens', 'author': 'Yuval Harari', 'date': '2011', 'category': 'History'})

    # Category filter should be precise
    scifi_only = storage.list_by_category('SciFi')
    assert len(scifi_only) == 1
    assert scifi_only[0]['name'] == 'Dune'

    # Update item1 and verify persistence
    updated = storage.update_item(item1['id'], {'author': 'F. Herbert'})
    assert updated is not None
    assert updated['author'] == 'F. Herbert'

    # get_by_id should reflect the update
    fetched = storage.get_by_id(item1['id'])
    assert fetched['author'] == 'F. Herbert'

    # Exact name search should find the second item
    found = storage.search_by_name_exact('Sapiens')
    assert found is not None
    assert found['id'] == item2['id']
