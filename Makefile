# freelibraries4all — corpus refresh entry points.
#
# As of 2026-05-06 the LS + RS crawler that builds the parliamentary
# library corpus is the public package `sansad-semantic-crawler`
# (PolyForm-NC), pinned in requirements.txt at v0.2.0. The host project
# supplies the topic profile (`topics/libraries.json`, vendored from
# the upstream `examples/topics/libraries.json` because the package
# install does not include the `examples/` directory) and the output
# directory (`data/_parliament_libraries/`, gitignored).
#
# Two legacy scripts (`scripts/sansad_library_crawl.py`,
# `scripts/sansad_library_parse.py`) were retired in the same commit;
# their LS-side schema variations are now harmonised by the package.
#
# After regenerating `assets/parliament_libraries.js`, BUMP THE
# `?v=N` cache-bust suffix everywhere it is referenced — see AGENTS.md
# section 5 for the one-pass `find ... sed` command.

VENV   := .venv
PYTHON := $(VENV)/bin/python
PIP    := $(VENV)/bin/pip

TOPIC_PROFILE := topics/libraries.json
CORPUS_OUT    := data/_parliament_libraries
EXPORT_PATH   := assets/parliament_libraries.js

.PHONY: deps corpus-crawl corpus-parse corpus-export corpus-refresh help

$(PYTHON):
	python3 -m venv $(VENV)
	$(PIP) install -q -r requirements.txt

deps:
	$(PIP) install -r requirements.txt

corpus-crawl: $(PYTHON)
	@test -f $(TOPIC_PROFILE) || { echo "missing $(TOPIC_PROFILE)"; exit 1; }
	$(PYTHON) -m sansad_semantic_crawler crawl \
	  --topic $(TOPIC_PROFILE) \
	  --out   $(CORPUS_OUT) \
	  $(ARGS)

corpus-parse: $(PYTHON)
	$(PYTHON) -m sansad_semantic_crawler parse \
	  --topic $(TOPIC_PROFILE) \
	  --out   $(CORPUS_OUT)

corpus-export: $(PYTHON)
	$(PYTHON) -m sansad_semantic_crawler export \
	  --topic       $(TOPIC_PROFILE) \
	  --out         $(CORPUS_OUT) \
	  --format      js \
	  --js-global   PARLIAMENT_LIBRARY_DATA \
	  --export-path $(EXPORT_PATH)

# Full pipeline: crawl, parse, export. After this finishes, manually
# bump the `?v=N` cache-bust everywhere index.html / data/index.html /
# inequality/index.html load assets/parliament_libraries.js. See
# AGENTS.md section 5 for the canonical sed command.
corpus-refresh: corpus-crawl corpus-parse corpus-export

help:
	@echo "Corpus refresh (sansad-semantic-crawler):"
	@echo "  make corpus-refresh                   — full pipeline (crawl + parse + export)"
	@echo "  make corpus-crawl   ARGS='--max-records 5 --no-download'  — smoke-test"
	@echo "  make corpus-parse                     — re-extract text from cached PDFs"
	@echo "  make corpus-export                    — regenerate assets/parliament_libraries.js"
	@echo "Setup:"
	@echo "  make deps                             — install pinned deps into .venv"
