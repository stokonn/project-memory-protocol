"""Run explicit checks without collecting stdout, stderr, or environment variables."""
import hashlib
import os
import platform
import subprocess
import sys
import uuid
import xml.etree.ElementTree as ET
from pmp.core.config import validate
from pmp.core.storage import PMPError, intact, now, read_json, seal, write_json
from pmp.events import Journal

def evidence_list(project):
    result=[]
    seen={}
    paths=sorted((project.local/'evidence').glob('*.json'))+sorted((project.shared/'evidence').glob('*.json'))
    for path in paths:
        e=validate('evidence',read_json(path))
        if not intact(e) or e['project_id']!=project.project_id or e['evidence_id']!=path.stem:
            raise PMPError(f'Evidence integrity/identity failure: {path}')
        if e['evidence_id'] in seen:
            if seen[e['evidence_id']] != e: raise PMPError('Conflicting shared/local evidence identity')
            continue
        seen[e['evidence_id']]=e
        result.append(e)
    return result

def applicable(e,source):
    return (e['source']['complete'] and source['complete'] and
            e['source']['head']==source['head'] and e['source']['fingerprint']==source['fingerprint'])

def summary(project):
    source=project.source()
    return [dict(e,applicable=applicable(e,source)) for e in evidence_list(project)]

def junit_count(blob):
    if len(blob)>4*1024*1024 or b'<!DOCTYPE' in blob.upper() or b'<!ENTITY' in blob.upper():
        raise PMPError('JUnit report oversized or contains DTD/entity declarations')
    try:
        tree=ET.fromstring(blob)
    except ET.ParseError as exc:
        raise PMPError(f'Invalid JUnit XML: {exc}') from exc
    cases=list(tree.iter('testcase'))
    executed=[c for c in cases if c.find('skipped') is None]
    failed=any(c.find('failure') is not None or c.find('error') is not None for c in cases)
    return len(executed),failed

def execute(project,check,command,timeout=3600):
    if not command:
        raise PMPError('Supply an explicit check command after --')
    if any('\x00' in arg for arg in command):
        raise PMPError('Invalid command argument')
    from pmp.security import scan
    if scan(' '.join(command).encode()):
        raise PMPError('Command may contain a secret. Use a tool-specific credential store.')
    source=project.source()
    ident=str(uuid.uuid4())
    report=project.local/'reports'/(ident+'.xml')
    report.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    argv=[x.replace('{report}',str(report)) for x in command]
    Journal(project).append('verification.started',{'check':check})
    outcome='blocked'; exit_code=None
    try:
        # Inherit terminal output; PMP never captures or persists arbitrary command logs.
        r=subprocess.run(argv,cwd=project.root,timeout=timeout)
        exit_code=r.returncode
        outcome='passed' if exit_code==0 else 'failed'
    except (subprocess.TimeoutExpired,KeyboardInterrupt):
        outcome='interrupted'
    except OSError:
        outcome='blocked'
    count=None; report_hash=None; report_ref=None
    if '{report}' in ' '.join(command) and report.exists():
        if report.is_symlink():
            report.unlink(missing_ok=True)
            blob=b''
            outcome='blocked'
        else:
            with report.open('rb') as stream: blob=stream.read(4*1024*1024+1)
        try:
            count,failed=junit_count(blob)
            if failed and outcome=='passed': outcome='failed'
        except PMPError:
            outcome='blocked'
        report_hash=hashlib.sha256(blob).hexdigest() if len(blob)<=4*1024*1024 and blob else None
        report_ref=str(report.relative_to(project.local))
        # Reports can contain test stdout, source fragments and personal paths.
        # Parse once, retain only hash/count, then remove generated private raw report.
        report.unlink(missing_ok=True)
        report_ref=None
    after=project.source()
    if after['head'] != source['head'] or after['fingerprint']!=source['fingerprint'] or not after['complete']:
        source['complete']=False
    data=seal({'schema_version':'1.0','evidence_id':ident,'project_id':project.project_id,'source':source,
               'check':check,'command':command,'environment':{'python':sys.version.split()[0],'platform':platform.system()},
               'outcome':outcome,'credibility':'verified','exit_code':exit_code,'tests_executed':count,
               'report_ref':report_ref,'report_hash':report_hash,'timestamp':now()})
    validate('evidence',data)
    write_json(project.local/'evidence'/(ident+'.json'),data,exclusive=True)
    Journal(project).append('verification.finished',{'evidence_id':ident})
    return data

def release_check(project):
    state=project.state()
    checks=summary(project)
    missing=[]
    for name in project.config['verification']['required_checks']:
        good=[e for e in checks if e['check']==name and e['applicable'] and e['outcome']=='passed' and e['credibility']=='verified']
        if project.config['verification']['require_test_count']:
            good=[e for e in good if (e['tests_executed'] or 0)>0]
        if not good:
            missing.append(name)
    problems=[]
    if missing: problems.append('Missing applicable verified checks with required execution counts: '+', '.join(missing))
    if not state['release_authorization']: problems.append('No explicit owner release authorization reference recorded')
    if state['phase'] not in ['ready_for_release','released']: problems.append('Task has not been explicitly promoted to ready_for_release')
    if state['status']!='active': problems.append('Task is not operationally active')
    if not project.source()['clean']: problems.append('Worktree is dirty; release source identity is not committed')
    return {'ready':not problems,'problems':problems,'published':False}
