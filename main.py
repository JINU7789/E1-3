import time
import json

EPSILON = 1e-9


def mac(pattern, filt):
    total = 0.0
    n = len(pattern)
    for i in range(n):
        for j in range(n):
            total += pattern[i][j] * filt[i][j]
    return total


def judge(cross_score, x_score):
    if abs(cross_score - x_score) < EPSILON:
        return "UNDECIDED"
    elif cross_score > x_score:
        return "Cross"
    else:
        return "X"


def normalize_label(label):
    label = str(label).strip().lower()
    if label in ("+", "cross"):
        return "Cross"
    elif label == "x":
        return "X"
    return label


def read_matrix(name, n=3):
    while True:
        print(f"{name} ({n}줄, 한 줄에 숫자 {n}개를 공백으로 구분)")
        matrix = []
        try:
            for _ in range(n):
                row = [float(v) for v in input().split()]
                if len(row) != n:
                    raise ValueError
                matrix.append(row)
            return matrix
        except ValueError:
            print(f"입력 형식 오류: 각 줄에 {n}개의 숫자를 공백으로 구분해 입력하세요.")


def measure_ms(pattern, filt, repeat=10):
    start = time.perf_counter()
    for _ in range(repeat):
        mac(pattern, filt)
    return (time.perf_counter() - start) / repeat * 1000


def mode1():
    filter_a = read_matrix("필터 A")
    filter_b = read_matrix("필터 B")
    pattern = read_matrix("패턴")

    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)

    if abs(score_a - score_b) < EPSILON:
        result = "판정 불가 (UNDECIDED)"
    elif score_a > score_b:
        result = "A"
    else:
        result = "B"

    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"평균 연산 시간: {measure_ms(pattern, filter_a):.4f} ms (10회 평균)")
    print(f"판정 결과: {result}")

def mode2(path="data.json"):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    filters = data["filters"]
    patterns = data["patterns"]
    total = passed = 0

    for key, case in patterns.items():
        total += 1
        try:
            n = int(key.split("_")[1])          # "size_5_1" → 5
            size_filters = filters[f"size_{n}"]
            cross_filter = size_filters["cross"]
            x_filter = size_filters["x"]
            pattern = case["input"]

            if len(pattern) != n or any(len(row) != n for row in pattern):
                raise ValueError(f"패턴 크기가 {n}x{n}이 아님")

            cross_score = mac(pattern, cross_filter)
            x_score = mac(pattern, x_filter)
            result = judge(cross_score, x_score)
            expected = normalize_label(case["expected"])
            ok = (result == expected)
            if ok:
                passed += 1

            reason = ""
            if not ok and result == "UNDECIDED":
                reason = " (사유: 필터 가중치로 인한 설계상 동점, epsilon 정책상 UNDECIDED)"
            elif not ok:
                reason = " (사유: 판정과 정답 불일치)"
            print(f"[{key}] Cross: {cross_score}, X: {x_score} "
                  f"→ 판정 {result} / 정답 {expected} → {'PASS' if ok else 'FAIL'}{reason}")
        except (KeyError, ValueError, IndexError) as e:
            print(f"[{key}] FAIL (사유: {e})")

    print(f"\n총 {total}개 중 {passed}개 PASS, {total - passed}개 FAIL")
    perf_table(filters)

def perf_table(filters):
    print("\n[성능 분석] (MAC 10회 평균)")
    print(f"{'크기(N×N)':<12}{'평균 시간(ms)':<16}{'연산 횟수(N²)':<12}")

    # 3×3은 data.json에 없으니 직접 만든 십자 패턴 사용
    cross3 = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
    cases = [(3, cross3, cross3)]
    for n in (5, 13, 25):
        f = filters[f"size_{n}"]["cross"]
        cases.append((n, f, f))

    for n, pattern, filt in cases:
        ms = measure_ms(pattern, filt)
        print(f"{f'{n}×{n}':<12}{ms:<16.4f}{n * n:<12}")

def main():
    print("=== Mini NPU 시뮬레이터 ===")
    print("1. 사용자 입력 (3×3)")
    print("2. data.json 분석")
    choice = input("모드를 선택하세요 (1/2): ").strip()
    if choice == "1":
        mode1()
    elif choice == "2":
        mode2()
    else:
        print("1 또는 2를 입력하세요.")


main()