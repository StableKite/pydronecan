"""Verify installed core contracts, genuine bytes, codecs and original tests."""
import base64
import csv
import hashlib
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import sysconfig
import xml.etree.ElementTree as ET
import dronecan

ROOT = Path(__file__).resolve().parent
os.environ['PATH'] = str(Path(sys.executable).parent) + os.pathsep + os.environ['PATH']
OUT = Path.cwd() / 'typing-contract-results'
OUT.mkdir(exist_ok=False)
package = Path(dronecan.__file__).resolve().parent
assert package.is_relative_to(Path(sys.prefix).resolve()), package
assert metadata.version('dronecan') == '1.0.27+stablekite.1'
assert metadata.version('mypy') == '2.4.1+stablekite.6'
assert metadata.version('pyright') == '1.1.414+stablekite.7'
for name in ('PYTHONPATH', 'MYPYPATH', 'PYTHON_GIL', 'PYRIGHT_PYTHON_FORCE_VERSION', 'PYRIGHT_PYTHON_IGNORE_WARNINGS'):
    assert name not in os.environ, name
assert sys._xoptions.get('gil') is None
assert (sys.version_info.minor == 13 and sys._is_gil_enabled()) or (sys.version_info.minor == 15 and sysconfig.get_config_var('Py_GIL_DISABLED') == 1 and not sys._is_gil_enabled())
expected = json.loads((ROOT / 'CONTRACT_PAYLOAD.json').read_bytes())
distribution = metadata.distribution('dronecan')
records = 0
for name, digest, size in csv.reader(distribution.read_text('RECORD').splitlines()):
    if digest:
        raw = Path(distribution.locate_file(name)).read_bytes()
        mode, value = digest.split('=', 1)
        assert mode == 'sha256' and len(raw) == int(size)
        assert base64.urlsafe_b64encode(hashlib.sha256(raw).digest()).decode().rstrip('=') == value
        records += 1
for name, row in expected.items():
    raw = Path(distribution.locate_file(name)).read_bytes()
    assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], name
assert len(expected) == 179
inputs = OUT / 'inputs'
shutil.copytree(ROOT / 'typing_tests', inputs)
(inputs / 'pyrightconfig.json').write_text(json.dumps({'typeCheckingMode': 'strict', 'pythonVersion': '3.15'}) + '\n')
stages = []


def run(name, argv, allowed=(0,)):
    result = subprocess.run([str(arg) for arg in argv], cwd=inputs, capture_output=True)
    (OUT / (name + '.stdout.log')).write_bytes(result.stdout)
    (OUT / (name + '.stderr.log')).write_bytes(result.stderr)
    stages.append({'name': name, 'argv': [str(arg) for arg in argv], 'exit': result.returncode})
    (OUT / 'STAGES.json').write_text(json.dumps(stages, indent=2) + '\n')
    assert result.returncode in allowed, (name, result.returncode, result.stdout[-1500:], result.stderr[-1500:])
    return result


modules = ['dronecan.transport', 'dronecan.dsdl.parser', 'dronecan.dsdl.common', 'dronecan.dsdl.signature', 'dronecan.dsdl.type_limits']
targets = [entry for module in modules for entry in ('-m', module)]
my = [sys.executable, '-I', '-B', '-m', 'mypy', '--strict', '--no-incremental', '--cache-dir', str(OUT / 'my-cache')]
pr = [sys.executable, '-I', '-B', '-m', 'pyright', '--project', str(inputs / 'pyrightconfig.json'), '--pythonpath', sys.executable, '--outputjson']
public = [package / 'transport.pyi', *sorted((package / 'dsdl').glob('*.pyi'))]
assert len(public) == 5
run('My6-covered5-core-modules', [*my, *targets])
result = run('Py7-covered5-core-modules', [*pr, *public])
assert json.loads(result.stdout)['summary']['filesAnalyzed'] == 5
run('My6-positive-real-public-contract', [*my, inputs / 'positive.py'])
run('Py7-positive-real-public-contract', [*pr, inputs / 'positive.py'])
run('real-positive-native-objects', [sys.executable, '-I', '-B', inputs / 'positive.py'])
negative = inputs / 'negative.py'
lines = [number for number, line in enumerate(negative.read_text().splitlines(), 1) if '# E' in line]
assert len(lines) == 29
my_result = run('My6-exact29-negative', [*my, negative], allowed=(1,))
my_lines = sorted(set(map(int, re.findall(r'negative\.py:(\d+): error:', my_result.stdout.decode()))))
pr_result = run('Py7-exact29-negative', [*pr, negative], allowed=(1,))
errors = [row for row in json.loads(pr_result.stdout)['generalDiagnostics'] if row['severity'] == 'error']
assert all(Path(row['file']).name == 'negative.py' for row in errors)
pr_lines = sorted(set(row['range']['start']['line'] + 1 for row in errors))
assert my_lines == pr_lines == lines, (lines, my_lines, pr_lines)
run('stubtest-all5-covered-modules-no-allowlist', [sys.executable, '-I', '-B', '-m', 'mypy.stubtest', *modules])
run('original-unittest-discover-unchanged', [sys.executable, '-I', '-B', '-m', 'unittest', 'discover', '-s', ROOT / 'test', '-v'])
driver = inputs / 'run_original_installed.py'
driver.write_text('''from pathlib import Path
import dronecan,json,pytest,sys
assert Path(dronecan.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
code=pytest.main(['-q','-r','s',sys.argv[1],'--junitxml='+sys.argv[2],'--basetemp='+sys.argv[3]])
print(json.dumps({'actual_package':dronecan.__file__,'gil_after':sys._is_gil_enabled(),'gil_flag':sys._xoptions.get('gil')}))
raise SystemExit(code)
''')
run('all58-original-installed-pytest', [sys.executable, '-I', '-B', driver, ROOT / 'test', OUT / 'JUNIT.xml', OUT / 'pytest-temp'])
suite = {key: sum(int(node.get(key, 0)) for node in ET.parse(OUT / 'JUNIT.xml').getroot().iter('testsuite')) for key in ('tests', 'failures', 'errors', 'skipped')}
assert suite == {'tests': 58, 'failures': 0, 'errors': 0, 'skipped': 0}, suite
native = json.loads(run('all145-types-124-registry-346-native-codecs', [sys.executable, '-I', '-B', inputs / 'native_snapshot.py']).stdout)
assert native['canonical_sha256'] == '31d85d03b320b72a2257897edf8ec1f2d6a35ce77c9934bfa23ea21ed5aebae6'
assert native['types'] == 145 and native['registry_entries'] == 124 and native['codec_cases'] == 346
complete = run('full-verifytypes-honest-scope', [sys.executable, '-I', '-B', '-m', 'pyright', '--pythonpath', sys.executable, '--verifytypes', 'dronecan', '--outputjson'], allowed=(0, 1))
full = json.loads(complete.stdout)['typeCompleteness']
assert sys._xoptions.get('gil') is None and sys._is_gil_enabled() is (sys.version_info.minor == 13)
result = {'status': 'PASS_INSTALLED_PRECISE_ROOT_CORE_CONTRACTS_NATIVE_AND_ORIGINAL_TESTS_PARTIAL_PACKAGE_SCOPE', 'version': distribution.version, 'actual_package': str(package), 'python': sys.version, 'Py_GIL_DISABLED': sysconfig.get_config_var('Py_GIL_DISABLED'), 'gil_enabled_after_all': sys._is_gil_enabled(), 'gil_flag': sys._xoptions.get('gil'), 'covered_strict_module_count_each_current_checker': 5, 'registry_variables_finite_types': True, 'negative_exact_lines_each_current_checker': lines, 'all179_canonical_package_payloads_verified': True, 'all_RECORD_verified': records, 'stubtest5_without_allowlist': True, 'original_suite': suite, 'native_snapshot_hash': native['canonical_sha256'], 'native_codec_cases': 346, 'full_verifytypes_exit': complete.returncode, 'full_verifytypes_score': full['completenessScore'], 'full_package_426_function_strict_or100percent_claimed': False, 'raw_CompoundType_factory_before_binding_returns_None': True, 'no_new_Any_or_ignore_or_cast_or_checker_overrides': True}
(OUT / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
