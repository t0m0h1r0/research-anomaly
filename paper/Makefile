PDF := build/main.pdf
MAIN := main.tex
TEX := $(MAIN) $(wildcard sections/*.tex)
BUILD_DIR := build

.PHONY: all clean distclean open

all: $(PDF)

$(PDF): $(TEX)
	mkdir -p $(BUILD_DIR)
	xelatex -interaction=nonstopmode -halt-on-error -output-directory=$(BUILD_DIR) $(MAIN)
	xelatex -interaction=nonstopmode -halt-on-error -output-directory=$(BUILD_DIR) $(MAIN)

open: $(PDF)
	open $(PDF)

clean:
	rm -rf $(BUILD_DIR)

distclean: clean
