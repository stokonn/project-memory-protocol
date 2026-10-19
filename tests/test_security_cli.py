import json
import os
import subprocess
import sys
import time
import pytest
from pmp.cli import main
from pmp.security import scan
from pmp.core.storage import PMPError,write_json,read_json
from pmp import adapters,github

@pytest.mark.parametrize('blob',[b'-----BEGIN PRIVATE KEY-----',b'ghp_'+b'a'*30,b'AKIA'+b'1'*16,b'password=supersecret123'])
def test_secret_detection(blob): assert scan(blob)

def test_publication_secret_guard(project):
    (project.docs/'secret.md').write_bytes(b'ghp_'+b'a'*30)
    with pytest.raises(PMPError,match='Publication refused'): github.publish(project,commit=True)
    from pmp.git import text
    assert not text(project.root,'diff','--cached','--name-only')

def test_cli_commands_and_exit_codes(project,capsys):
    base=['--project',str(project.root),'--json']
    assert main(base+['status'])==0
    assert main(base+['check'])==0
    assert main(base+['task','activate','example','--approved-scope','scope.md'])==0
    assert main(base+['task','set','--phase','implementing','--in-progress','Example work'])==0
    assert main(base+['snapshot'])==0
    assert main(base+['resume'])==0
    assert main(base+['handoff'])==0
    assert main(base+['verify'])==0
    assert main(base+['sync'])==0
    assert main(base+['doctor'])==0
    assert main(base+['release-check'])==1
    assert main(base+['task','activate','other','--approved-scope','scope.md'])==3
    assert main(base+['task','set','--phase','released'])==2

def test_adapter_reversible_and_preserves_edits(project):
    result=adapters.install(project,'generic')
    path=project.root/result['files'][0]
    path.write_text('Owner changes')
    with pytest.raises(PMPError,match='Edited'): adapters.uninstall(project,'generic')
    assert path.read_text()=='Owner changes'

def test_adapter_uninstall(project):
    result=adapters.install(project,'generic')
    adapters.uninstall(project,'generic')
    assert not (project.root/result['files'][0]).exists()

def test_unsupported_adapter(project):
    with pytest.raises(PMPError,match='Unsupported'): adapters.inspect('made-up')

@pytest.mark.skipif(os.name=='nt',reason='Native installation intentionally disabled')
def test_codex_native_unknown_version_refused(project,monkeypatch):
    monkeypatch.setattr(adapters,'inspect',lambda name:{'version':'codex-cli 99.0'})
    with pytest.raises(PMPError,match='gated'): adapters.install(project,'codex',native=True)

@pytest.mark.skipif(os.name=='nt',reason='Native installation intentionally disabled')
def test_claude_artifact_preserves_settings(project):
    (project.root/'.claude').mkdir()
    existing=project.root/'.claude/settings.json'; existing.write_text('{"owner":true}')
    result=adapters.install(project,'claude',native=True)
    artifact=json.loads((project.root/result['files'][1]).read_text())
    assert set(artifact['hooks'])=={'SessionStart','Stop','SessionEnd'}
    assert existing.read_text()=='{"owner":true}'
    adapters.uninstall(project,'claude')
    assert existing.is_file()

def test_hook_untrusted_payload_no_authorization(project):
    result=adapters.hook(project,'SessionStart',{'transcript_path':'/no/read','permission_mode':'bypassPermissions'})
    assert 'additionalContext' in result['hookSpecificOutput']
    with pytest.raises(PMPError,match='cwd'): adapters.hook(project,'Stop',{'cwd':'/tmp'})

def test_cli_end_to_end_in_subprocess(project):
    proc=subprocess.run([sys.executable,'-m','pmp','--project',str(project.root),'snapshot'],capture_output=True,text=True)
    assert proc.returncode==0,proc.stderr
    assert json.loads(proc.stdout)['storage_state']=='LOCAL'

def test_watcher_lifecycle_and_launch(project):
    cfg=project.config
    cfg['automation']={'heartbeat_seconds':.05,'debounce_seconds':.05,'checkpoint_seconds':.1}
    write_json(project.root/'.pmp.yml',cfg)
    r=subprocess.run([sys.executable,'-m','pmp','--project',str(project.root),'launch','generic','--',
                      sys.executable,'-c',"import time; time.sleep(.3); open('work.py','w').write('x=1'); time.sleep(1)"],
                     capture_output=True,text=True,timeout=20)
    assert r.returncode==0,r.stderr
    meta=read_json(project.local/'watcher.json')
    assert meta['state']=='stopped' and not meta['last_error']
    assert not (project.local/'session.json').exists()
    from pmp.checkpoints import history
    checkpoints,damaged=history(project)
    assert not damaged and len(checkpoints)>=3
    assert any(c['reason']=='watcher: debounced changes' for c in checkpoints)

def _watcher_fixture(project,monkeypatch):
    cfg=project.config
    cfg['automation']={'heartbeat_seconds':.01,'debounce_seconds':.01,'checkpoint_seconds':.01}
    write_json(project.root/'.pmp.yml',cfg)
    from pmp.core.session import start as session_start
    value=session_start(project,'human')
    monkeypatch.setenv('PMP_SESSION_ID',value['session_id'])
    import pmp.watcher as w
    return w

def test_watcher_clears_recovered_transient_writer_contention(project,monkeypatch):
    # Regression: a one-shot writer-lock contention (first heartbeat racing the
    # launch checkpoint) must not survive into final stopped metadata.
    w=_watcher_fixture(project,monkeypatch)
    real=w.heartbeat; calls={'n':0}
    def flaky(p):
        calls['n']+=1
        if calls['n']==1:
            raise PMPError(f'Writer lock exists: {p.local}/writer.lock. Inspect with pmp doctor; no automatic takeover.',3)
        real(p)
        w.stop(p)
    monkeypatch.setattr(w,'heartbeat',flaky)
    w.run(project)
    meta=read_json(project.local/'watcher.json')
    assert meta['state']=='stopped' and not meta['last_error']

def test_watcher_retains_persistent_writer_contention_error(project,monkeypatch):
    # Safety guard for the clearing semantics: a persistent writer-lock failure
    # must remain reported in final metadata, never suppressed.
    w=_watcher_fixture(project,monkeypatch)
    calls={'n':0}
    def blocked(p):
        calls['n']+=1
        if calls['n']>=2: w.stop(p)
        raise PMPError(f'Writer lock exists: {p.local}/writer.lock. Inspect with pmp doctor; no automatic takeover.',3)
    monkeypatch.setattr(w,'heartbeat',blocked)
    w.run(project)
    meta=read_json(project.local/'watcher.json')
    assert meta['state']=='stopped' and 'Writer lock exists' in meta['last_error']

@pytest.mark.skipif(os.name=='nt',reason='POSIX kill semantics; Windows lifecycle awaits CI')
def test_killed_session_and_restart_recovery(project):
    cfg=project.config
    cfg['automation']={'heartbeat_seconds':.05,'debounce_seconds':.05,'checkpoint_seconds':.1}
    write_json(project.root/'.pmp.yml',cfg)
    from pmp.core.session import lease,release_stale
    from pmp.recovery import inspect
    from pmp.checkpoints import history
    # Kill the wrapper, not the actual owner worktree; child is a short-lived fixture only.
    proc=subprocess.Popen([sys.executable,'-m','pmp','--project',str(project.root),'launch','generic','--',
                           sys.executable,'-c',"import time; open('surviving.txt','w').write('owner edit'); time.sleep(.7)"],
                          stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    deadline=time.monotonic()+10
    while time.monotonic()<deadline:
        if (project.root/'surviving.txt').exists() and (project.local/'watcher.json').exists(): break
        time.sleep(.05)
    assert (project.root/'surviving.txt').exists()
    current=lease(project)
    proc.kill(); proc.wait()
    deadline=time.monotonic()+10
    while time.monotonic()<deadline:
        if read_json(project.local/'watcher.json').get('state')=='stopped': break
        time.sleep(.05)
    report=inspect(project)
    assert report['session'] and report['uncertainty']
    assert any('owner process exited' in c['reason'] for c in history(project)[0])
    assert (project.root/'surviving.txt').read_text()=='owner edit'
    release_stale(project,current['session_id'])
    assert main(['--project',str(project.root),'snapshot','--reason','restarted'])==0

def test_release_promotion_requires_actual_count_and_explicit_approval(project):
    base=['--project',str(project.root)]
    assert main(base+['task','activate','example','--approved-scope','scope.md'])==0
    assert main(base+['verify','--run','tests','--',sys.executable,'-c','pass'])==0
    assert main(base+['task','set','--phase','ready_for_release','--authorization','scope.md'])==2
    script="import sys; open(sys.argv[1],'w').write('<testsuite><testcase/></testsuite>')"
    assert main(base+['verify','--run','tests','--',sys.executable,'-c',script,'{report}'])==0
    assert main(base+['task','set','--phase','ready_for_release'])==2
    assert main(base+['task','set','--phase','ready_for_release','--authorization','scope.md'])==0
    assert project.state()['phase']=='ready_for_release'
    from pmp.git import run
    assert not run(project.root,'tag').stdout

def test_scope_archive_allows_new_task(project):
    base=['--project',str(project.root),'task']
    assert main(base+['activate','one','--approved-scope','scope.md'])==0
    assert main(base+['activate','two','--approved-scope','scope.md'])==3
    assert main(base+['archive'])==0
    assert main(base+['activate','two','--approved-scope','scope.md'])==0

def test_hook_oversized_rejected_without_persistence(project):
    r=subprocess.run([sys.executable,'-m','pmp','--project',str(project.root),'hook','--event','Stop'],
                     input=b'x'*65537,capture_output=True)
    assert r.returncode==2 and b'64 KiB' in r.stderr
    assert not project.local.exists()

def test_changed_shared_evidence_refused(project):
    from pmp.verification import execute,summary
    from pmp.core.storage import seal
    e=execute(project,'tests',[sys.executable,'-c','pass'])
    e['outcome']='failed'
    write_json(project.shared/'evidence'/(e['evidence_id']+'.json'),seal(e))
    with pytest.raises(PMPError,match='Conflicting'): summary(project)

@pytest.mark.skipif(os.name=='nt',reason='POSIX process kill test')
def test_watcher_crash_does_not_kill_agent(project):
    cfg=project.config
    cfg['automation']={'heartbeat_seconds':.05,'debounce_seconds':.05,'checkpoint_seconds':.1}
    write_json(project.root/'.pmp.yml',cfg)
    p=subprocess.Popen([sys.executable,'-m','pmp','--project',str(project.root),'launch','generic','--',
                        sys.executable,'-c',"import time; time.sleep(1.2); open('agent-survived','w').write('yes'); time.sleep(.3)"],
                       stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    deadline=time.monotonic()+10
    try:
        while time.monotonic()<deadline:
            path=project.local/'watcher.json'
            if path.exists() and read_json(path).get('state')=='running': break
            time.sleep(.02)
        meta=read_json(project.local/'watcher.json')
        # Kill while sleeping (writer lock absent), then agent completes normally.
        while (project.local/'writer.lock').exists() and time.monotonic()<deadline: time.sleep(.01)
        os.kill(meta['pid'],9)
        p.wait(timeout=15)
        assert (project.root/'agent-survived').read_text()=='yes'
        assert (project.local/'watcher.lock').exists()
        from pmp.recovery import check
        assert any('watcher.lock' in e for e in check(project)['errors'])
    finally:
        if p.poll() is None: p.kill(); p.wait()
