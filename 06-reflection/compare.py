# 6편 본 실험: 방식 A·B·C·D를 같은 과제로 N번씩 (기본 5번)
# 실행: python compare.py [N]
import sys

from reflect import MAX_ROUNDS, run

N = int(sys.argv[1]) if len(sys.argv) > 1 else 5
NAMES = {"A": "한 번에", "B": "기준 없이 다시 보기", "C": "모델이 스스로 검토", "D": "코드가 검토", "E": "코드가 검토 + 숫자"}
METHODS = sys.argv[2] if len(sys.argv) > 2 else "ABCD"

results = {}
for m in METHODS:
    results[m] = []
    for i in range(1, N + 1):
        print(f"\n[방식 {m} {NAMES[m]} — {i}회]", flush=True)
        results[m].append(run(m))

print(f"\n===== 요약 (방식별 {N}번, 고치기 최대 {MAX_ROUNDS}번) =====")
for m, rs in results.items():
    line = (f"방식 {m} {NAMES[m]}: 초안 통과 {sum(r['first_ok'] for r in rs)}/{N} · 최종 통과 {sum(r['final_ok'] for r in rs)}/{N}"
            f" · 모델 호출 평균 {sum(r['calls'] for r in rs) / N:.1f}번 · 고친 뒤 더 나빠짐 {sum(r['worse'] for r in rs)}번")
    print(line)
judge = [j for r in results.get("C", []) for j in r["judge"]]
if judge:
    print(f"모델 검토 판정 {len(judge)}번: 맞음 {judge.count('맞음')} · 문제를 놓침 {judge.count('놓침')} · 괜찮은 계획을 문제 있다고 함 {judge.count('헛짚음')}")
