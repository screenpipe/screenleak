.PHONY: help install bench bench-text bench-image bench-trace unify smoke test lint clean check pre-oss

PYTHON ?= python3

help:
	@echo "ScreenLeak — multi-modal PII disclosure benchmark"
	@echo ""
	@echo "Setup:"
	@echo "  make install        Install Python deps (pip install -e .)"
	@echo "  make bench          Run all 3 sub-benches against the sample corpus"
	@echo ""
	@echo "Run a sub-bench:"
	@echo "  make bench-text     Score every text adapter"
	@echo "  make bench-image    Score every image adapter"
	@echo "  make bench-trace    Replay + score trace adapters"
	@echo "  make bench          All three, sequentially"
	@echo "  make unify          Rebuild unified_leaderboard.md from sub-bench results"
	@echo ""
	@echo "Trace bench data prep (one-shot):"
	@echo "  make trace-data     build_seeds + inject (runs once; reproducible from --seed)"
	@echo ""
	@echo "QA / release:"
	@echo "  make smoke          End-to-end smoke test of trace pipeline (no API calls)"
	@echo "  make test           pytest"
	@echo "  make lint           ruff check"
	@echo "  make check          smoke + test + lint + verify gold integrity"
	@echo "  make pre-oss        Verify nothing private leaks before going public"
	@echo "  make clean          Remove generated artifacts (replays, predictions)"
	@echo ""
	@echo "Env:"
	@echo "  ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY  required for frontier adapters"
	@echo "  SCREENLEAK_CLAUDE_MODEL / GPT5_MODEL / GEMINI_MODEL  optional model overrides"

install:
	$(PYTHON) -m pip install -e ".[trace]"
	@echo "(image + text deps live in their vendored requirements files; install per-bench as needed)"

bench-text:
	@echo "[bench-text] running text/src/score.py against sample (n=36)"
	cd text && $(PYTHON) -m src.score --adapter $${ADAPTER:-regex} --annotations data/sample.jsonl

bench-image:
	@echo "[bench-image] running image/src/score.py against sample (n=30)"
	cd image && $(PYTHON) -m src.score --adapter $${ADAPTER:-regex_ocr} --annotations corpus/sample/annotations_sample.jsonl

bench-trace:
	@echo "[bench-trace] replaying $${ADAPTER:-claude} on sample (n=5)"
	@mkdir -p trace/results/replays
	$(PYTHON) -m trace.src.replay --adapter $${ADAPTER:-claude} \
		--in trace/data/injected_sample.jsonl \
		--out trace/results/replays/$${ADAPTER:-claude}.jsonl
	$(PYTHON) -m trace.src.score \
		--traces trace/data/injected_sample.jsonl \
		--replays trace/results/replays/*.jsonl \
		--out trace/results/leaderboard.md

bench: bench-text bench-image bench-trace unify

unify:
	$(PYTHON) scripts/build_unified_leaderboard.py

smoke:
	@echo "[smoke] verifying trace sample gold integrity (no API calls)"
	$(PYTHON) -c "import json; \
		fails = 0; total = 0; \
		[ (total := total + 1, fails := fails + (item['text'] not in row['messages'][row['injected_tool_idx']]['content'])) \
		  for line in open('trace/data/injected_sample.jsonl') if line.strip() \
		  for row in [json.loads(line)] \
		  for item in row['injected_pii'] ]; \
		print(f'  {total} gold items, {fails} mismatches'); \
		raise SystemExit(0 if fails == 0 else 1)"
	@echo "[smoke] ok"

test:
	$(PYTHON) -m pytest tests/ -q

lint:
	-ruff check .
	-shellcheck scripts/*.sh

check: smoke test lint
	@echo "[check] all green"

pre-oss:
	bash scripts/pre_oss_check.sh

clean:
	rm -rf trace/results/replays trace/results/leaderboard.md
	rm -f results/unified_leaderboard.md
	$(PYTHON) scripts/build_unified_leaderboard.py
	@echo "[clean] artifacts dropped, unified leaderboard regenerated"
