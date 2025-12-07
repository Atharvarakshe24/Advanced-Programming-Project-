import json
from server import create_app
import storage


def test_server_endpoints(tmp_path, monkeypatch):
    # Use temp file for storage
    tmp_file = tmp_path / 'media.json'
    monkeypatch.setattr(storage, 'DATA_FILE', tmp_file)

    app = create_app()
    client = app.test_client()

    # Initially empty
    rv = client.get('/media')
    assert rv.status_code == 200
    assert rv.get_json() == []

    # Create new item
    payload = {'name': 'Server Book', 'author': 'Author', 'date': '2020', 'category': 'Science'}
    rv = client.post('/media', json=payload)
    assert rv.status_code == 201
    created = rv.get_json()
    assert created['name'] == 'Server Book'

    # List shows item
    rv = client.get('/media')
    assert rv.status_code == 200
    items = rv.get_json()
    assert len(items) == 1

    # Search exact
    rv = client.get('/media/search', query_string={'name': 'Server Book'})
    assert rv.status_code == 200
    found = rv.get_json()
    assert found['name'] == 'Server Book'

    # Delete
    rv = client.delete(f"/media/{created['id']}")
    assert rv.status_code == 200
    rv = client.get('/media')
    assert rv.get_json() == []
