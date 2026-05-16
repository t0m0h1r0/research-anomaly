.PHONY: all paper prompt-sync prompt-sync-dry-run prompt-deploy prompt-audit clean

all: paper

paper:
	$(MAKE) -C paper

prompt-sync-dry-run:
	python3 scripts/sync_research_agent.py --dry-run

prompt-sync:
	python3 scripts/sync_research_agent.py

prompt-deploy:
	python3 scripts/deploy_prompt_system.py

prompt-audit:
	python3 scripts/validate_prompt_deployment.py

clean:
	$(MAKE) -C paper clean
