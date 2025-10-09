
AMD_64_CXX ?= g++
ARM_64_CXX ?=  aarch64-linux-gnu-g++
LOGROTEE_DIR = ../logrotee
BUILDDIR = build

logrotee: $(LOGROTEE_DIR)/logrotee.cpp
	mkdir -p $(BUILDDIR)/amd64
	mkdir -p $(BUILDDIR)/arm64
	$(AMD_64_CXX) $(LOGROTEE_DIR)/logrotee.cpp -o $(BUILDDIR)/amd64/logrotee
	$(ARM_64_CXX) $(LOGROTEE_DIR)/logrotee.cpp -o $(BUILDDIR)/arm64/logrotee

clean:
	rm -f $(BUILDDIR)

.PHONY: clean