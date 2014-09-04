# -*- coding: utf-8 -*-
import pytest

from plowshare import Plowshare

# Fixtures ###

@pytest.fixture
def patch_subprocess(monkeypatch):
    import subprocess

    def plow_output(*args, **kwargs):
        if args and args[0]:
            if args[0][0] == 'plowdown':
                return 'fasd.tar.gz'
            elif args[0][0] == 'plowup':
                return 'http://rghost.net/57830097'
        return ''

    monkeypatch.setattr(subprocess, 'check_output', plow_output)

@pytest.fixture
def patch_subprocess_exc(monkeypatch):
    import subprocess

    def raise_exc(*args, **kwargs):
        raise subprocess.CalledProcessError(1, args[0][0] if args and args[0] else '', '')

    monkeypatch.setattr(subprocess, 'check_output', raise_exc)

@pytest.fixture
def patch_rename(monkeypatch):
    import os
    monkeypatch.setattr(os, 'rename', lambda *a: None)

FILEMETA = {'url': 'http://rghost.net/57830097', 'host_name': 'rghost'}

@pytest.fixture
def patch_rnd_choice(monkeypatch):
    import random
    monkeypatch.setattr(random, 'choice', lambda *a: FILEMETA)

@pytest.fixture
def patch_rnd_sample(monkeypatch):
    import random
    monkeypatch.setattr(random, 'sample', lambda pop, k: pop[:k])


# Plowshare fixtures and mocks

@pytest.fixture
def plowinst():
    return Plowshare(['ge_tt', 'multiupload', 'rghost'])

@pytest.fixture
def patch_plow_random_upload(monkeypatch):
    result = {'host_name': 'rghost', 'url': 'http://rghost.net/57830097'}
    monkeypatch.setattr(Plowshare, 'random_upload', lambda *a: result if a and a[1] else None)

@pytest.fixture
def patch_plow_upload_to_host(monkeypatch):
    result = {'host_name': 'rghost', 'url': 'http://rghost.net/57830097'}
    monkeypatch.setattr(Plowshare, 'upload_to_host', lambda *a: result)

@pytest.fixture
def patch_plow_multiupload(monkeypatch):
    result = [{'host_name': 'rghost', 'url': 'http://rghost.net/57830097'}]
    monkeypatch.setattr(Plowshare, 'multiupload', lambda *a: result)

@pytest.fixture
def patch_plow_download_from_host(monkeypatch):
    monkeypatch.setattr(Plowshare, 'download_from_host',
            lambda *a: {'host_name': 'rghost', 'filename': 'test/test.tgz'})


# Tests ###

def test_random_upload(plowinst, patch_rnd_choice):
    assert plowinst.random_upload(['ok', 'yes']) == FILEMETA

def test_random_upload_empty(plowinst, patch_rnd_choice):
    assert plowinst.random_upload([]) is None

def test_random_upload_empty_error(plowinst, patch_rnd_choice):
    assert plowinst.random_upload(['error']) is None


def test_random_hosts(plowinst, patch_rnd_sample):
    result = plowinst.random_hosts(2)
    assert result == ['ge_tt', 'multiupload']


def test_parse_output(plowinst):
    result = plowinst.parse_output('rghost',
        ('100 16008  100 16008    0     0  28920      0 --:--:-- --:--:-- --:--:-- 28895\n'
         'fasd.tar.gz')
    )
    assert result == 'fasd.tar.gz'


def test_download_from_host(plowinst, patch_subprocess, patch_rename):
    result = plowinst.download_from_host(FILEMETA, 'test', 'test.tgz')
    assert result == {'filename': 'test/test.tgz', 'host_name': 'rghost'}


def test_upload_to_host(plowinst, patch_subprocess):
    result = plowinst.upload_to_host('fasd.tar.gz', 'rghost')
    assert result == {'host_name': 'rghost', 'url': 'http://rghost.net/57830097'}

def test_upload_to_host_error(plowinst, patch_subprocess_exc):
    result = plowinst.upload_to_host('fasd.tar.gz', 'rghost')
    assert result == {
            'host_name': 'rghost',
            'error': "Command 'plowup' returned non-zero exit status 1"
        }


def test_download(plowinst, patch_plow_download_from_host, patch_plow_random_upload):
    result = plowinst.download(['test'], 'test', 'test.tgz')
    assert result == {'filename': 'test/test.tgz', 'host_name': 'rghost'}

def test_download_error(plowinst, patch_plow_random_upload, patch_subprocess_exc):
    result = plowinst.download(['test'], 'test', 'test.tgz')
    assert result == {
            'host_name': 'rghost',
            'error': "Command 'plowdown' returned non-zero exit status 1"
        }

def test_download_none(plowinst, patch_plow_random_upload):
    result = plowinst.download([], 'test', 'test.tgz')
    assert result == {'error': 'no valid uploads'}


def test_upload(plowinst, patch_plow_multiupload):
    result = plowinst.upload('test.tgz', 3)
    assert result == [{'host_name': 'rghost', 'url': 'http://rghost.net/57830097'}]


def test_multiupload(plowinst, patch_plow_upload_to_host):
    result = plowinst.multiupload('test.tgz', ['rghost'])
    assert result == [{'host_name': 'rghost', 'url': 'http://rghost.net/57830097'}]
