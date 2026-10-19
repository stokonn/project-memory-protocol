import copy
import json
from pathlib import Path
import pytest
from pmp.core.config import Project,initialize,validate
from pmp.core.storage import PMPError,write_json
from pmp.security import relative_path

def test_init_preserves_existing(tmp_path,monkeypatch):
    monkeypatch.setenv('PMP_STATE_HOME',str(tmp_path.parent/(tmp_path.name+'-private')))
    (tmp_path/'AGENTS.md').write_text('Canonical owner rules')
    (tmp_path/'docs/ai').mkdir(parents=True)
    (tmp_path/'docs/ai/PROJECT.md').write_text('Existing roadmap')
    p,msg=initialize(tmp_path)
    assert (tmp_path/'AGENTS.md').read_text()=='Canonical owner rules'
    assert (tmp_path/'docs/ai/PROJECT.md').read_text()=='Existing roadmap'
    assert msg
    again,_=initialize(tmp_path)
    assert p.project_id==again.project_id

def test_init_orphan_state_refused(tmp_path):
    (tmp_path/'.pmp').mkdir()
    (tmp_path/'.pmp/state.json').write_text('{}')
    with pytest.raises(PMPError,match='without configuration'): initialize(tmp_path)
    assert not (tmp_path/'.pmp.yml').exists()

@pytest.mark.parametrize('version',['0.9','1.1','2.0','bogus'])
def test_incompatible_versions(project,version):
    cfg=copy.deepcopy(project.config); cfg['protocol_version']=version
    with pytest.raises(PMPError): validate('config',cfg)

def test_unknown_fields_fail_closed(project):
    cfg=copy.deepcopy(project.config); cfg['auto_release']=True
    with pytest.raises(PMPError): validate('config',cfg)

@pytest.mark.parametrize('name',['../outside','/tmp/out','C:/out',r'C:\out',r'folder\file','.git/config','.'])
def test_portable_path_guard(project,name):
    with pytest.raises(PMPError): relative_path(project.root,name)

def test_symlink_guard(project,tmp_path):
    (project.root/'outside').symlink_to(tmp_path,target_is_directory=True)
    with pytest.raises(PMPError): relative_path(project.root,'outside/private.json')

def test_state_identity_guard(project):
    state=project.state(); state['project_id']='other'
    write_json(project.shared/'state.json',state)
    with pytest.raises(PMPError,match='identity'): project.state()

def test_yaml_config_supported(project):
    import yaml
    (project.root/'.pmp.yml').write_text(yaml.safe_dump(project.config))
    assert Project(project.root).project_id==project.project_id

def test_memory_overlap_rejected(project):
    cfg=project.config; cfg['memory']['docs']='.pmp/docs'
    write_json(project.root/'.pmp.yml',cfg)
    with pytest.raises(PMPError,match='overlap'): Project(project.root)

def test_packaged_schemas_match():
    root=Path(__file__).resolve().parents[1]
    for file in (root/'schemas').glob('*.json'):
        assert file.read_bytes()==(root/'src/pmp/schemas'/file.name).read_bytes()

def test_private_store_inside_worktree_refused(project,monkeypatch):
    monkeypatch.setenv('PMP_STATE_HOME',str(project.root/'private'))
    with pytest.raises(PMPError,match='outside'): Project(project.root)
