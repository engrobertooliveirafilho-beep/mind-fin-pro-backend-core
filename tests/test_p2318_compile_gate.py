import pytest
from app.runtime.p2318_compile_gate import audit_compile_logs
NAMES=['P2318_compile.log.txt','P2318B_compile.log.txt','P2318B_compile_retry.log.txt']
SHA256={'P2318_compile.log.txt':'516661e8fdd211e5b16ce3171c769088d4a5b9f3710886349e885ea49641ef3c','P2318B_compile.log.txt':'b60af536bad3550cbec5e238990ccb977a8731c7deae8f9363bee50912b7a485','P2318B_compile_retry.log.txt':'8dc334f550f9d9644857a0e5f8dc35275abe34b70ff81d336579258cba9ed6ba'}
def fake():
    return {name:'Result: 0 errors, 0 warnings, 3164 ms elapsed'.encode('utf-16') for name in NAMES}
def test_clean_compilation_is_not_consumption():
    r=audit_compile_logs(fake())
    assert r['logs_verified']==3 and not r['ea_consumption_certified']
    assert r['real_orders_authorized']==0
@pytest.mark.parametrize('missing',NAMES)
def test_missing_log(missing):
    logs=fake();del logs[missing]
    with pytest.raises(ValueError):audit_compile_logs(logs)
@pytest.mark.parametrize('bad',[b'not UTF16','Result: 1 errors, 0 warnings, 200 ms elapsed'.encode('utf-16'),'Result: 0 errors, 1 warnings, 200 ms elapsed'.encode('utf-16')])
def test_invalid_log(bad):
    logs=fake();logs[NAMES[0]]=bad
    with pytest.raises(ValueError):audit_compile_logs(logs)
