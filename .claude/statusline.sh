#!/bin/bash
# Claude Code Statusline - Context Usage Display
# Shows: Model | Input/Output tokens | Context usage % with bar | Cost | Duration
#
# Setup:
#   1. Ensure .claude/statusline.sh is executable: chmod +x .claude/statusline.sh
#   2. Add to .claude/settings.json:
#      "statusLine": { "type": "command", "command": ".claude/statusline.sh" }

input=$(cat)

# Extract all fields in a single jq invocation (pipe-delimited to handle spaces in model name)
IFS='|' read -r MODEL PCT INPUT_TOKENS OUTPUT_TOKENS COST API_DURATION_MS <<< "$(echo "$input" | jq -r '[
  .model.display_name,
  (.context_window.used_percentage // 0 | floor),
  (.context_window.total_input_tokens // 0),
  (.context_window.total_output_tokens // 0),
  (.cost.total_cost_usd // 0),
  (.cost.total_api_duration_ms // 0)
] | join("|")')"

# ANSI colors
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
CYAN='\033[36m'
RESET='\033[0m'

# Color based on context usage threshold
if [ "$PCT" -ge 90 ]; then
    BAR_COLOR="$RED"
elif [ "$PCT" -ge 70 ]; then
    BAR_COLOR="$YELLOW"
else
    BAR_COLOR="$GREEN"
fi

# Build progress bar (10 chars wide)
BAR_WIDTH=10
FILLED=$((PCT * BAR_WIDTH / 100))
EMPTY=$((BAR_WIDTH - FILLED))
BAR=""
[ "$FILLED" -gt 0 ] && printf -v FILL "%${FILLED}s" && BAR="${FILL// /█}"
[ "$EMPTY" -gt 0 ] && printf -v PAD "%${EMPTY}s" && BAR="${BAR}${PAD// /░}"

# Format cost
COST_FMT=$(printf '$%.4f' "$COST")

# Format API duration (ms -> seconds)
API_SEC=$(awk "BEGIN { printf \"%.1f\", $API_DURATION_MS / 1000 }")

# Output
echo -e "${CYAN}${MODEL}${RESET} | ${INPUT_TOKENS}/${OUTPUT_TOKENS} tokens | ${BAR_COLOR}${BAR} ${PCT}%${RESET} | ${YELLOW}${COST_FMT}${RESET} | ${API_SEC}s"
