# theright2read — corpus refresh entry points.
#
# The LS + RS crawler is the public package `sansad-semantic-crawler`
# (PolyForm-NC), pinned in requirements.txt. The host project supplies
# the topic profile (`topics/libraries.json`, vendored from the upstream
# `examples/topics/libraries.json` because the package install does not
# include the `examples/` directory) and the output directory
# (`data/_parliament_libraries/`, gitignored).
#
# As of 2026-05-12 the pipeline runs against sansad-semantic-crawler
# v1.0.0, which adds an analytical layer on top of the crawl/parse/export
# basics: extract-answers → analyse-discourse → analyse-ministry. The
# `corpus-enrich` step joins those analytical outputs into
# assets/parliament_libraries.js via scripts/build_parliament_libraries.py
# (the upstream `export` only emits the manifest-derived summary).
#
# After regenerating assets/parliament_libraries.js, BUMP THE `?v=N`
# cache-bust suffix everywhere it is referenced.

VENV   := .venv
PYTHON := $(VENV)/bin/python
PIP    := $(VENV)/bin/pip

TOPIC_PROFILE := topics/libraries.json
CORPUS_OUT    := data/_parliament_libraries
EXPORT_PATH   := assets/parliament_libraries.js

.PHONY: deps corpus-crawl corpus-parse corpus-export corpus-extract-answers \
        corpus-analyse-discourse corpus-analyse-ministry corpus-analyse \
        corpus-enrich corpus-refresh sync-agents help

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

# v1.0.0 analytical layer.
corpus-extract-answers: $(PYTHON)
	$(PYTHON) -m sansad_semantic_crawler extract-answers \
	  --out $(CORPUS_OUT)

corpus-analyse-discourse: $(PYTHON)
	$(PYTHON) -m sansad_semantic_crawler analyse-discourse \
	  --out $(CORPUS_OUT)

corpus-analyse-ministry: $(PYTHON)
	$(PYTHON) -m sansad_semantic_crawler analyse-ministry \
	  --topic $(TOPIC_PROFILE) \
	  --out   $(CORPUS_OUT)

corpus-analyse: corpus-extract-answers corpus-analyse-discourse corpus-analyse-ministry

# Join the upstream manifest export with the v1.0.0 analytical outputs
# into a single enriched assets/parliament_libraries.js.
corpus-enrich: corpus-export
	$(PYTHON) scripts/build_parliament_libraries.py

# Full pipeline: crawl → parse → analyse → export → enrich. After this
# finishes, manually bump the `?v=N` cache-bust everywhere index.html /
# data/index.html / inequality/index.html load assets/parliament_libraries.js.
corpus-refresh: corpus-crawl corpus-parse corpus-analyse corpus-enrich

sync-agents:
	python3 scripts/sync_agents.py

help:
	@echo "Corpus refresh (sansad-semantic-crawler v1.0.0):"
	@echo "  make corpus-refresh                   — full pipeline (crawl + parse + analyse + enrich)"
	@echo "  make corpus-crawl   ARGS='--max-records 5 --no-download'  — smoke-test"
	@echo "  make corpus-parse                     — re-extract text from cached PDFs"
	@echo "  make corpus-analyse                   — extract-answers + analyse-discourse + analyse-ministry"
	@echo "  make corpus-export                    — upstream manifest-only export"
	@echo "  make corpus-enrich                    — export + join analytical files (the public artefact)"
	@echo "Setup:"
	@echo "  make deps                             — install pinned deps into .venv"
	@echo "Agent rules:"
	@echo "  make sync-agents                      — regenerate CLAUDE.md + AGENTS.md from CONTEXT.md"
