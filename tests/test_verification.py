import sys
import pytest
from pmp.verification import execute,summary,junit_count,release_check
from pmp.core.storage import PMPError

def test_old_evidence_inapplicable(project,commit):
    (project.root/'code.py').write_text('x=1\n'); commit()
    e=execute(project,'tests',[sys.executable,'-c','pass'])
    assert e['outcome']=='passed' and e['credibility']=='verified'
    assert e['tests_executed'] is None
    assert summary(project)[0]['applicable']
    (project.root/'code.py').write_text('x=2\n')
    assert not summary(project)[0]['applicable']
    assert not release_check(project)['ready']

def test_command_changes_source_invalidates(project):
    execute(project,'tests',[sys.executable,'-c',"open('changed.py','w').write('x=1')"])
    assert not summary(project)[0]['applicable']

def test_actual_junit_execution_counts(project):
    script="import sys; open(sys.argv[1],'w').write('<testsuite><testcase/><testcase><skipped/></testcase></testsuite>')"
    e=execute(project,'tests',[sys.executable,'-c',script,'{report}'])
    assert e['tests_executed']==1 and e['report_hash']
    assert not list((project.local/'reports').glob('*.xml'))

def test_failure_and_timeout(project):
    e=execute(project,'bad',[sys.executable,'-c','raise SystemExit(7)'])
    assert e['outcome']=='failed' and e['exit_code']==7
    e=execute(project,'timeout',[sys.executable,'-c','import time; time.sleep(5)'],timeout=.02)
    assert e['outcome']=='interrupted'

def test_missing_binary_blocked(project):
    assert execute(project,'missing',['pmp-nonexistent-command'])['outcome']=='blocked'

def test_failing_report_overrides_exit_zero(project):
    script="import sys; open(sys.argv[1],'w').write('<testsuite><testcase><failure/></testcase></testsuite>')"
    assert execute(project,'tests',[sys.executable,'-c',script,'{report}'])['outcome']=='failed'

@pytest.mark.parametrize('report',[b'<!DOCTYPE x><testsuite/>',b'<!ENTITY x "y"><testsuite/>',b'<broken'])
def test_bad_xml_refused(report):
    with pytest.raises(PMPError): junit_count(report)

def test_zero_tests_is_not_execution():
    assert junit_count(b'<testsuite tests="200"/>')==(0,False)

def test_source_clean_dirty_untracked(project,commit):
    commit(); clean=project.source()
    assert clean['clean']
    (project.root/'untracked.py').write_text('print(1)')
    dirty=project.source()
    assert not dirty['clean'] and dirty['fingerprint']!=clean['fingerprint']
    assert (project.root/'untracked.py').exists()
