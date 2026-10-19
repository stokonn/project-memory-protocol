"""Actual disposable PMP workflow; no vendor runtime or Goldberg checkout access."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def demonstrate(output=None,goldberg_style=False):
    base=Path(output).resolve() if output else Path(tempfile.mkdtemp(prefix='pmp-demo-'))
    if output:
        base.mkdir(parents=True,exist_ok=False)
    root=base/'project'; root.mkdir()
    env=dict(os.environ,PMP_STATE_HOME=str(base/'private'))
    env.pop('PMP_SESSION_ID',None)
    def cli(*args,session=None):
        session_env=dict(env)
        if session: session_env['PMP_SESSION_ID']=session
        r=subprocess.run([sys.executable,'-m','pmp','--project',str(root),*args],env=session_env,
                         capture_output=True,text=True,check=False)
        if r.returncode: raise RuntimeError(f'pmp {args[0]} failed: {r.stderr}')
        return json.loads(r.stdout)
    def git(*args):
        return subprocess.run(['git','-C',str(root),*args],capture_output=True,text=True,check=True).stdout.strip()
    # Existing authoritative files must survive init, edits and recovery.
    rules='Canonical fixture policy: preserve personal data; no physical phone; owner approvals required.\n'
    (root/'AGENTS.md').write_text(rules)
    (root/'scope.md').write_text('Owner-approved example: make answer() return 42 in this disposable fixture only.\n')
    (root/'.gitignore').write_text('__pycache__/\n')
    initialized=cli('init')
    git('config','user.name','PMP Demo'); git('config','user.email','pmp-demo@example.invalid')
    if goldberg_style:
        git('switch','-c','goldberg-0.11-stage4-fixture')
        (root/'docs/ROADMAP.md').write_text('Synthetic existing roadmap. Stage 4 partial; Stage 5 not authorized.\n')
    (root/'app.py').write_text('def answer():\n    return 41\n')
    # Real unittest execution; structured result counts only, no full report/log collection.
    (root/'run_checks.py').write_text('''import sys, unittest, xml.etree.ElementTree as ET
from app import answer
class Example(unittest.TestCase):
    def test_answer(self): self.assertEqual(answer(),42)
r=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(Example))
suite=ET.Element('testsuite')
for index in range(r.testsRun):
    case=ET.SubElement(suite,'testcase',name=str(index))
    if not r.wasSuccessful(): ET.SubElement(case,'failure')
ET.ElementTree(suite).write(sys.argv[1])
raise SystemExit(0 if r.wasSuccessful() else 1)
''')
    git('add','.'); git('commit','-m','Create disposable approved example')
    branch=git('branch','--show-current')
    if goldberg_style: (root/'RELEASE_NOTES.md').write_text('Untracked owner draft; preserve verbatim.\n')
    cli('task','activate','approved-example','--approved-scope','scope.md')
    cli('task','set','--phase','implementing','--in-progress','Implement example answer')
    session=cli('session','start','--owner','simulated-interrupted-agent')['session_id']
    (root/'app.py').write_text('def answer():\n    return 42\n')
    evidence=cli('verify','--run','tests','--',sys.executable,'run_checks.py','{report}',session=session)
    assert evidence['outcome']=='passed' and evidence['tests_executed']==1
    checkpoint=cli('snapshot','--reason','verified dirty-source milestone',session=session)
    # The short-lived owning CLI has exited without ending its lease: interruption simulation.
    recovery=cli('resume')
    assert recovery['session']['session_id']==session
    assert (root/'app.py').read_text().endswith('return 42\n')
    cli('session','release-stale','--session-id',session)
    handoff=cli('handoff')
    shared=cli('handoff','--shared')
    standalone=(root/'docs/ai/HANDOFF.md').read_text() # Read with no agent/conversation.
    assert 'approved-example' in standalone and 'context, not authorization' in standalone
    assert (root/'AGENTS.md').read_text()==rules and git('branch','--show-current')==branch
    if goldberg_style:
        assert (root/'RELEASE_NOTES.md').read_text()=='Untracked owner draft; preserve verbatim.\n'
        assert '?? RELEASE_NOTES.md' in git('status','--short')
    assert cli('check')['valid']
    result={'project':str(root),'project_id':initialized['project_id'],'branch':branch,
            'tests_executed':evidence['tests_executed'],'outcome':evidence['outcome'],
            'checkpoint':checkpoint['checkpoint_id'],'interruption_detected':bool(recovery['session']),
            'handoff_read_without_agent':True,'source_preserved':True,'goldberg_style':goldberg_style,
            'actual_goldberg_accessed':False,'shared_handoff_sha256':hashlib.sha256(standalone.encode()).hexdigest()}
    (base/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',help='New directory for retained disposable fixture')
    p.add_argument('--goldberg-style',action='store_true')
    a=p.parse_args()
    print(json.dumps(demonstrate(a.output,a.goldberg_style),indent=2))
