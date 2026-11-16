# 6편 예비 실험: 방식 A·B·C·D를 3번씩 돌려 초안 통과율과 최종 통과율, 모델 호출 수를 비교
import sys

from reflect import run

N = int(sys.argv[1]) if len(sys.argv) > 1 else 3
names = {"A": "한 번에", "B": "기준 없이 다시 보기", "C": "모델이 스스로 검토", "D": "코드가 검토"}
summary = {}
for m in "ABCD":
    rs = []
    for i in range(1, N + 1):
        print(f"\n[방식 {m} {names[m]} — {i}회]", flush=True)
        rs.append(run(m))
    summary[m] = rs
print("\n===== 요약 =====")
for m, rs in summary.items():
    print(f"방식 {m} {names[m]}: 초안 통과 {sum(r['first_ok'] for r in rs)}/{N} · 최종 통과 {sum(r['final_ok'] for r in rs)}/{N} · 모델 호출 평균 {sum(r['calls'] for r in rs) / N:.1f}번")
