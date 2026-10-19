import importlib.util
from pathlib import Path

def test_goldberg_disposable_demo(tmp_path):
    path=Path(__file__).parents[1]/'examples/demo.py'
    spec=importlib.util.spec_from_file_location('pmp_demo',path)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    result=module.demonstrate(tmp_path/'demo',goldberg_style=True)
    assert result['tests_executed']==1 and result['outcome']=='passed'
    assert result['source_preserved'] and result['handoff_read_without_agent']
    assert result['actual_goldberg_accessed'] is False
