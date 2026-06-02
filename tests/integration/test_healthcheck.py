# -*- coding: utf-8 -*-


def test_healthcheck(client):
    response = client.get('/api/healthcheck')
    assert response.status_code == 200
    assert response.json == {'result': 'OK'}
