from __future__ import annotations
import subprocess
import sys
import time
from pathlib import Path

class USDEScientificTestMonitor:
    def discover_tests(self):
        root=Path("tests/modules")
        if not root.exists():
            return []

        return sorted(
            str(p)
            for p in root.glob("test_usde_*.py")
        )

    def run(self):
        tests=self.discover_tests()

        print("="*80)
        print("USDE SCIENTIFIC TEST MONITOR")
        print("="*80)
        print(f"TOTAL_TEST_FILES={len(tests)}")
        print("="*80)

        results=[]

        for i,test in enumerate(tests,1):
            print(f"[{i}/{len(tests)}] RUNNING {test}")
            started=time.time()

            proc=subprocess.run(
                [sys.executable,"-m","pytest",test,"-q"],
                capture_output=True,
                text=True
            )

            elapsed=time.time()-started

            status="PASSED" if proc.returncode==0 else "FAILED"

            print(f"[{i}/{len(tests)}] {status} {test} ({elapsed:.2f}s)")

            if proc.stdout.strip():
                print(proc.stdout.strip())

            if proc.stderr.strip():
                print(proc.stderr.strip())

            results.append({
                "test":test,
                "status":status,
                "seconds":round(elapsed,2),
                "returncode":proc.returncode
            })

            print("-"*80)

        passed=sum(1 for r in results if r["status"]=="PASSED")
        failed=sum(1 for r in results if r["status"]=="FAILED")

        print("="*80)
        print(f"SUMMARY PASSED={passed} FAILED={failed} TOTAL={len(results)}")
        print("="*80)

        return {
            "passed":passed,
            "failed":failed,
            "total":len(results),
            "results":results
        }

if __name__=="__main__":
    r=USDEScientificTestMonitor().run()
    raise SystemExit(0 if r["failed"]==0 else 1)
