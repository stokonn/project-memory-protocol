import os
from pathlib import Path
import subprocess
import pytest
from pmp.core.config import initialize

@pytest.fixture
def project(tmp_path,monkeypatch):
    monkeypatch.setenv('PMP_STATE_HOME',str(tmp_path/'private'))
    monkeypatch.delenv('PMP_SESSION_ID',raising=False)
    root=tmp_path/'project'; root.mkdir()
    p,_=initialize(root)
    subprocess.run(['git','-C',str(root),'config','user.name','PMP Tests'],check=True)
    subprocess.run(['git','-C',str(root),'config','user.email','pmp@example.invalid'],check=True)
    (root/'scope.md').write_text('Owner-approved disposable test scope.\n')
    return p

@pytest.fixture
def commit(project):
    def make(message='fixture'):
        subprocess.run(['git','-C',str(project.root),'add','.'],check=True,capture_output=True)
        subprocess.run(['git','-C',str(project.root),'commit','-m',message],check=True,capture_output=True)
        return project.source()['head']
    return make
