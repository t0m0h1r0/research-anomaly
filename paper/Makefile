PDF := build/main.pdf
TEX := main.tex
BUILD_DIR := build

.PHONY: all clean distclean open

all: $(PDF)

$(PDF): $(TEX)
	mkdir -p $(BUILD_DIR)
	xelatex -interaction=nonstopmode -halt-on-error -output-directory=$(BUILD_DIR) $(TEX)
	xelatex -interaction=nonstopmode -halt-on-error -output-directory=$(BUILD_DIR) $(TEX)

open: $(PDF)
	open $(PDF)

clean:
	rm -rf $(BUILD_DIR)

distclean: clean
