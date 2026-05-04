.PHONY: all paper clean

all: paper

paper:
	$(MAKE) -C paper

clean:
	$(MAKE) -C paper clean
