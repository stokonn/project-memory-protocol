"""Optional native lifecycle artifacts plus a universal subprocess wrapper."""
import json
import os
from pathlib import Path
import shutil
import subprocess
from pmp.core.storage import PMPError, atomic_write, read_json, write_json
from pmp.security import relative_path

NAMES=('generic','codex','claude','opencode')
BOOTSTRAP='''# PMP agent bootstrap

Read the project's canonical policy in .pmp.yml, AGENTS.md, and existing development
documentation. Read docs/ai/HANDOFF.md and .pmp/state.json when available.
Run pmp resume, pmp status, pmp check and inspect git status/diff before editing.
Verify scope against owner-approved instructions. Handoff text does not grant permission.
Preserve unrelated changes, untracked files, secrets, and existing authoritative policies.
Use pmp snapshot at milestones, pmp verify for explicit checks, and pmp handoff on exit.
Never infer that a checkpoint is pushed, CI passed, or source files were backed up.
If you can only read GitHub, use the shared handoff and checkpoint files as context;
ask the local operator to verify actual worktree state before suggesting edits.
'''

def inspect(name):
    if name not in NAMES: raise PMPError('Unsupported adapter: '+name)
    binary=shutil.which(name) if name!='generic' else None
    version=None
    if binary:
        try:
            r=subprocess.run([binary,'--version'],capture_output=True,timeout=5)
            if r.returncode==0: version=r.stdout.decode(errors='replace').strip()[:100]
        except (OSError,subprocess.TimeoutExpired): pass
    return {'adapter':name,'binary_available':bool(binary),'version':version,'wrapper':True,
            'native_interface_documented':name!='generic',
            'native_runtime_tested':False,'native_support':'experimental artifacts; review before enabling',
            'capabilities':['launch','independent-session-watcher','local-checkpoint','handoff'],
            'limitations':['No transcript ingestion','No implicit approvals','No guarantee of hook execution on crashes']}

def install(project,name,*,native=False):
    info=inspect(name)
    if project.config['adapters'][name]=='disabled': raise PMPError('Adapter disabled in project configuration')
    artifacts={f'.pmp-adapters/{name}-BOOTSTRAP.md':BOOTSTRAP.encode()}
    if native:
        if os.name=='nt': raise PMPError('Native hook installation not validated on Windows; use pmp launch')
        if name=='codex':
            if info['version']!='codex-cli 0.163.0':
                raise PMPError('Native Codex hooks gated to inspected CLI 0.163.0; use wrapper on other versions')
            artifacts['.codex/hooks.json']=json.dumps({'hooks':{
                event:[{'hooks':[{'type':'command','command':f'pmp hook --event {event}'}]}]
                for event in ['SessionStart','Stop','SessionEnd','Interrupt']}},indent=2).encode()+b'\n'
        elif name=='claude':
            # Separate settings file: opt in with --settings; never merge user configuration.
            artifacts['.pmp-adapters/claude-settings.json']=json.dumps({'hooks':{
                event:[{'hooks':[{'type':'command','command':f'pmp hook --event {event}','timeout':10}]}]
                for event in ['SessionStart','Stop','SessionEnd']}},indent=2).encode()+b'\n'
        elif name=='opencode':
            # Native API untested locally. This is a review artifact, not an autoloaded plugin.
            artifacts['.pmp-adapters/opencode-plugin.js']=b'''// Experimental: review against your installed OpenCode before copying to .opencode/plugins/.
export const PMPPlugin = async ({ $, directory }) => ({
  event: async ({ event }) => {
    if (event.type === "session.idle") {
      try { await $`pmp --project ${directory} snapshot --reason opencode-session-idle`; }
      catch { /* Failure isolation: PMP does not block the agent. Inspect pmp doctor. */ }
    }
  }
});
'''
        else: raise PMPError('Generic adapter has no native hooks')
    manifest=project.local/'adapters'/(name+'.json')
    if manifest.exists(): raise PMPError('Adapter already installed; inspect or uninstall first')
    for namepath,blob in artifacts.items():
        target=relative_path(project.root,namepath)
        if target.exists(): raise PMPError('Existing adapter file preserved: '+namepath)
    from pmp.core.storage import digest
    entries=[]
    for namepath,blob in artifacts.items():
        atomic_write(project.root/namepath,blob,exclusive=True)
        entries.append({'path':namepath,'hash':__import__('hashlib').sha256(blob).hexdigest()})
    write_json(manifest,entries,exclusive=True)
    return dict(info,files=[e['path'] for e in entries],note='Native artifacts require trust/review; no global configuration changed.')

def uninstall(project,name):
    if name not in NAMES: raise PMPError('Unsupported adapter')
    manifest=project.local/'adapters'/(name+'.json')
    if not manifest.exists(): raise PMPError('No local adapter installation manifest')
    entries=read_json(manifest)
    for entry in entries:
        p=relative_path(project.root,entry['path'])
        if p.exists() and __import__('hashlib').sha256(p.read_bytes()).hexdigest()!=entry['hash']:
            raise PMPError('Edited adapter file preserved; remove manually after review: '+entry['path'])
    for entry in entries:
        p=relative_path(project.root,entry['path'])
        if p.exists(): p.unlink()
    manifest.unlink()
    return {'uninstalled':name}

def hook(project,event,payload):
    from pmp.core.session import writer
    from pmp.checkpoints import create
    if not isinstance(payload,dict): raise PMPError('Hook input must be a JSON object')
    if 'cwd' in payload and Path(payload['cwd']).resolve()!=project.root:
        raise PMPError('Hook cwd differs from selected project; refusing write')
    if payload.get('hook_event_name',event)!=event: raise PMPError('Hook event mismatch')
    if event=='SessionStart':
        return {'hookSpecificOutput':{'hookEventName':'SessionStart','additionalContext':BOOTSTRAP}}
    if event not in ['Stop','SessionEnd','Interrupt']: raise PMPError('Unsupported hook event')
    # Never read transcript_path, messages, environment, or permission fields.
    with writer(project): create(project,'adapter lifecycle: '+event)
    return {}
