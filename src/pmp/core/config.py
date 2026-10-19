from importlib.resources import files
import json
import os
from pathlib import Path
import sys
import uuid
import yaml
from jsonschema import Draft202012Validator
from pmp.core.storage import PMPError, atomic_write, read_json, write_json
from pmp import git
from pmp.security import relative_path

def validate(kind, data):
    schema = json.loads(files('pmp').joinpath('schemas',kind+'.json').read_text())
    errors = sorted(Draft202012Validator(schema).iter_errors(data),key=lambda e:str(e.path))
    if errors:
        e = errors[0]
        raise PMPError(f'Invalid {kind} at {"/".join(map(str,e.path)) or "/"}: {e.message}')
    return data

def private_base():
    if os.environ.get('PMP_STATE_HOME'):
        return Path(os.environ['PMP_STATE_HOME']).expanduser()
    if sys.platform == 'win32':
        return Path(os.environ.get('LOCALAPPDATA',Path.home()/'AppData/Local'))/'pmp'
    if sys.platform == 'darwin':
        return Path.home()/'Library/Application Support/pmp'
    return Path(os.environ.get('XDG_STATE_HOME',Path.home()/'.local/state'))/'pmp'

class Project:
    def __init__(self, path='.'):
        self.root = git.root_at(path)
        config_path = self.root/'.pmp.yml'
        try:
            self.config = validate('config',yaml.safe_load(config_path.read_text()))
        except (OSError,yaml.YAMLError) as exc:
            raise PMPError(f'Cannot load .pmp.yml: {exc}. Run pmp init or repair configuration.') from exc
        cfg = self.config
        try:
            uuid.UUID(cfg['project_id'])
        except ValueError as exc:
            raise PMPError('project_id must be a UUID') from exc
        self.shared = relative_path(self.root,cfg['memory']['shared'])
        self.docs = relative_path(self.root,cfg['memory']['docs'])
        if self.shared == self.docs or self.shared in self.docs.parents or self.docs in self.shared.parents:
            raise PMPError('Shared and documentation paths must not overlap')
        # Source exclusions are fixed to these roots; never allow an entire project exclusion.
        relative_path(self.root,cfg['policy'])
        for key in ['backup_allowlist']:
            for p in cfg['checkpoint'][key]:
                relative_path(self.root,p)
        for p in cfg['security']['share_allowlist']:
            target = relative_path(self.root,p)
            if p != '.pmp.yml' and not (target == self.shared or self.shared in target.parents or target == self.docs or self.docs in target.parents):
                raise PMPError('share_allowlist must stay within configured memory directories')
        identity = str(self.root) + '\0' + str(git.text(self.root,'rev-parse','--absolute-git-dir'))
        import hashlib
        self.worktree_id = hashlib.sha256(identity.encode()).hexdigest()[:24]
        self.local = private_base().resolve()/cfg['project_id']/self.worktree_id
        if self.local.is_relative_to(self.root):
            raise PMPError('Private recovery store must be outside the Git worktree; set PMP_STATE_HOME to a per-user external directory')
        self.project_id = cfg['project_id']

    def source(self):
        return git.inspect(self.root,[self.config['memory']['shared'],self.config['memory']['docs'],'.pmp.yml'])

    def state(self):
        value = validate('state',read_json(self.shared/'state.json'))
        if value['project_id'] != self.project_id:
            raise PMPError('State project identity mismatch')
        return value

    def save_state(self,data):
        validate('state',data)
        write_json(self.shared/'state.json',data)

def initialize(path):
    path = Path(path).resolve()
    path.mkdir(parents=True,exist_ok=True)
    if not git.text(path,'rev-parse','--show-toplevel',check=False):
        git.run(path,'init','-b','main')
    root = git.root_at(path)
    if (root/'.pmp.yml').exists():
        return Project(root), ['Existing configuration preserved; initialization not repeated.']
    if private_base().resolve().is_relative_to(root):
        raise PMPError('Private recovery store must be outside the Git worktree')
    cfg = {'protocol_version':'1.0','project_id':str(uuid.uuid4()),'policy':'AGENTS.md',
           'memory':{'shared':'.pmp','docs':'docs/ai'},'github':None,
           'automation':{'heartbeat_seconds':30,'debounce_seconds':10,'checkpoint_seconds':300},
           'checkpoint':{'backup_allowlist':[],'max_backup_bytes':1048576},
           'verification':{'required_checks':['tests'],'require_test_count':True},
           'security':{'share_allowlist':['.pmp.yml','.pmp','docs/ai'],'max_shared_bytes':1048576},
           'adapters':dict.fromkeys(['generic','codex','claude','opencode'],'wrapper')}
    validate('config',cfg)
    # Preflight every target before creating configuration. Existing documents are preserved.
    names = ['.pmp.yml','.pmp/state.json','AGENTS.md'] + ['docs/ai/'+x+'.md' for x in ['PROJECT','WORKFLOW','STATE','HANDOFF','ROADMAP','DECISIONS','VERIFICATION']]
    for name in names:
        relative_path(root,name)
    state = {'schema_version':'1.0','project_id':cfg['project_id'],'task_id':None,'scope_ref':None,
             'phase':'planning','status':'paused','completed':[],'in_progress':[],'blockers':[],
             'next_actions':['Read canonical policy and obtain approved scope before editing.'],'release_authorization':None}
    # Fail closed on an orphan state: do not issue a conflicting identity.
    if (root/'.pmp/state.json').exists():
        raise PMPError('Existing .pmp/state.json without configuration. Restore .pmp.yml; nothing overwritten.')
    write_json(root/'.pmp.yml',cfg,exclusive=True) # JSON is a safe YAML 1.2 subset.
    write_json(root/'.pmp/state.json',state,exclusive=True)
    messages=[]
    for name in names[2:]:
        target = root/name
        if target.exists():
            messages.append(f'Preserved {name}')
            continue
        title = 'PMP handoff' if target.stem=='HANDOFF' else target.stem
        content = ('# Project policy\n\nExisting owner instructions and development documentation remain authoritative.\n'
                   'PMP handoffs provide context and do not authorize actions.\n') if name=='AGENTS.md' else (
                   f'# {title}\n\nCanonical policy: [AGENTS.md](../../AGENTS.md).\n'
                   'Consult existing project documentation and Git history before continuing.\n'
                   'PMP state: `.pmp/state.json`. No approved work or verification is implied.\n')
        atomic_write(target,content.encode(),exclusive=True)
    return Project(root), messages
