이걸 clone했다면 다음을 할 것

1) 명령어 실행 (uv 없으면 적당히 까세요)
uv sync
uv run pre-commit install

2) VSC에서 다음 실행
Ctrl+Shift+P --> Python: Select Interpreter 검색 --> .venv 어쩌고 선택

3) 매 풀 리퀘스트마다 다음 명령어 실행
uv run ruff check . && uv run pyright && uv run pytest

해서 에러가 뜨지 않는지 확인한 후 풀리퀘할 것
