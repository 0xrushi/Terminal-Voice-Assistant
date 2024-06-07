default: run
run:
	@sudo sh src/run_mac.sh

clean:
	@echo "Nothing to clean."

kill: 
	@sudo pkill -f "thinking_siri_animation.py"

.PHONY: run clean