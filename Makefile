.PHONY: all paper prompt-sync prompt-sync-dry-run clean

all: paper

paper:
	$(MAKE) -C paper

prompt-sync-dry-run:
	python3 scripts/sync_research_agent.py --dry-run

prompt-sync:
	python3 scripts/sync_research_agent.py

clean:
	$(MAKE) -C paper clean
