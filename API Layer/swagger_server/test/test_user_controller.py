"""
    Tests related to user endpoints
"""
# coding: utf-8

import pytest
import requests

def test_user_login_post(client):
    headers = {'username':'luigi.bianchi', 'password':'password2'}
    response = client.post('/user/login', headers=headers)
    assert response.status_code == 200