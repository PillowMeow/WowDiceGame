"""UI 연출용 기록.
kind 목록 (Game이 남기는 것)
| kind | data | 언제|
| turn_start | turn | 턴 시작 (첫 턴 포함) |
| rolled | face(나온 면 값), value(효과 보정 후 값) | 주사위 굴린 직후, 이동 전|
| moved| start, end, teleport(0 또는 1)| move가 끝날 때 한 번 |
| landed | tile | 칸에 멈췄을 때 |
| coins| delta(실제 변화량), total | 코인이 실제로 바뀌었을 때 |
| used | effect(효과 id) | 액티브 효과 사용 |
| bought | die, price | 상점 구매|
| die_replaced | die| 주사위 교체|
| turn_end | turn | 턴 종료|
| win| (없음)| 승리 |

효과가 g.add_log로 맘대로 로그를 남겨도 됨
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LogEntry:
    kind: str
    pid: str | None  # 누가 발생한 것인지
    data: dict[str, int | str]
