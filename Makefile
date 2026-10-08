.PHONY: test doctor build install
test:    ; python3 -m pytest -q
doctor:  ; python3 skills/academic-core/scripts/doctor.py
build:   ; python3 tools/build_dist.py
install: ; python3 tools/install.py
