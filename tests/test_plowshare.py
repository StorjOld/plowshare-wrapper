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
        if args and 'fail' in args[0]:
            raise subprocess.CalledProcessError(1, args[0][0] if args and args[0] else '', '')
        else:
            return 'output'

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

@pytest.fixture
def patch_plow_host_errors(monkeypatch, plowinst):
    from collections import defaultdict
    result = defaultdict(int, [('rghost', 0), ('multiupload', 3), ('ge_tt', 1)])
    monkeypatch.setattr(plowinst, '_host_errors', result)
    return plowinst

@pytest.fixture
def patch_settings(monkeypatch):
    import settings
    monkeypatch.setattr(settings, 'MIN_FILE_REDUNDANCY', 0.2)


# Tests ###

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
    result = plowinst.upload_to_host('fail', 'rghost')
    assert result == {
            'host_name': 'rghost',
            'error': "Command 'plowup' returned non-zero exit status 1"
        }


def test_download(plowinst, patch_plow_download_from_host):
    result = plowinst.download([{'host_name': 'rghost', 'url': 'testurl'}], 'test', 'test.tgz')
    assert result == {'filename': 'test/test.tgz', 'host_name': 'rghost'}

def test_download_error(plowinst, patch_subprocess_exc):
    result = plowinst.download([{'host_name': 'rghost', 'url': 'fail'}], 'test', 'test.tgz')
    assert result == {}

def test_download_none(plowinst):
    result = plowinst.download([], 'test', 'test.tgz')
    assert result == {'error': 'no valid sources'}

def test_download_failover(plowinst, patch_subprocess_exc, patch_rename):
    sources = [
        {'host_name': 'rghost', 'url': 'fail'},
        {'host_name': 'ge_tt', 'error': 'testerror'},
        {'host_name': 'multiupload', 'url': 'testurl'},
    ]
    result = plowinst.download(sources, 'test', 'test.tgz')
    assert result == {'host_name': 'multiupload', 'filename': 'test/test.tgz'}


def test_upload(plowinst, patch_plow_multiupload):
    result = plowinst.upload('test.tgz', 3)
    assert result == [{'host_name': 'rghost', 'url': 'http://rghost.net/57830097'}]


def test_multiupload(plowinst, patch_plow_upload_to_host):
    result = plowinst.multiupload('test.tgz', ['rghost'])
    assert result == [{'host_name': 'rghost', 'url': 'http://rghost.net/57830097'}]

def test_multiupload_failover(patch_plow_host_errors, patch_subprocess_exc, patch_settings):
    inst = patch_plow_host_errors
    result = inst.multiupload('test.tgz', ['fail', 'multiupload', 'rghost', 'ge_tt'])
    # Only one host upload will be done since the redundancy threshold is so low (0.2)
    assert result == [{'host_name': 'rghost', 'url': 'output'}]


def test_hosts_by_success(patch_plow_host_errors):
    inst = patch_plow_host_errors
    result = inst._hosts_by_success(inst.hosts)
    assert result == ['rghost', 'ge_tt', 'multiupload']

def test_filter_sources(patch_plow_host_errors):
    inst = patch_plow_host_errors
    sources = [
        {'host_name': 'multiupload', 'url': 'testurl'},
        {'host_name': 'rghost', 'url': 'testurl'},
        {'host_name': 'ge_tt', 'error': 'testerror'},
    ]

    result = inst._filter_sources(sources)
    assert result == [
        {'host_name': 'rghost', 'url': 'testurl'},
        {'host_name': 'multiupload', 'url': 'testurl'}
    ]
