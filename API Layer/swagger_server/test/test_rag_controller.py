"""
    Tests related to RAG endpoints
"""
# coding: utf-8

import pytest

@pytest.mark.skip(reason='Slow')
@pytest.mark.slow()
def test_ai_query_post(client, login):
    headers = {'Authorization':login, 'query':'This is a test query.'}
    response = client.post('/ai-query', headers=headers)
    assert response.status_code == 200
    assert 'dashboard' in response.json
    assert 'report' in response.json