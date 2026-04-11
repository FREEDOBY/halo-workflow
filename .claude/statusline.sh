#!/bin/bash
input=$(cat)

# ANSI colors
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
CYAN='\033[36m'
DIM='\033[2m'
RESET='\033[0m'

# Parse all values using node
eval $(node -e "
const d = JSON.parse(process.argv[1]);
const u = d.context_window?.used_percentage ?? '';
const cur = d.context_window?.current_usage ?? {};
const total = (cur.input_tokens||0)+(cur.cache_creation_input_tokens||0)+(cur.cache_read_input_tokens||0)+(cur.output_tokens||0);
const ctxSize = d.context_window?.context_window_size ?? 1000000;
const cost = d.cost?.total_cost_usd ?? '';
const model = d.model?.display_name ?? 'Claude';
const cwd = d.cwd ?? '';
const r5 = d.rate_limits?.five_hour?.used_percentage ?? '';
const r7 = d.rate_limits?.seven_day?.used_percentage ?? '';
console.log('USED=\"'+u+'\"');
console.log('TOTAL_TOK=\"'+total+'\"');
console.log('CTX_SIZE=\"'+ctxSize+'\"');
console.log('COST=\"'+cost+'\"');
console.log('MODEL=\"'+model+'\"');
console.log('CWD=\"'+cwd+'\"');
console.log('RATE_5H=\"'+r5+'\"');
console.log('RATE_7D=\"'+r7+'\"');
" "$input" 2>/dev/null)

# Color picker based on percentage: green < 50, yellow < 80, red >= 80
color_for() {
  local pct=$1
  if [ "$pct" -ge 80 ] 2>/dev/null; then echo "$RED"
  elif [ "$pct" -ge 50 ] 2>/dev/null; then echo "$YELLOW"
  else echo "$GREEN"
  fi
}

# Build progress bar with color
make_bar() {
  local pct=$1 len=$2 color=$3
  local filled=$(awk "BEGIN {v=int($pct / 100 * $len); if(v<1 && $pct>0) v=1; printf \"%d\", v}")
  local bar=""
  local i=0
  while [ $i -lt $filled ]; do bar="${bar}█"; i=$((i+1)); done
  local empty=""
  while [ $i -lt $len ]; do empty="${empty}░"; i=$((i+1)); done
  printf "${color}${bar}${DIM}${empty}${RESET}"
}

# --- Line 1: Model | Context bar | Tokens | Cost | Git ---
CTX_BAR=""
if [ -n "$USED" ]; then
  CTX_COLOR=$(color_for "$USED")
  CTX_BAR=$(make_bar "$USED" 20 "$CTX_COLOR")
  CTX_BAR="${CTX_BAR} ${CTX_COLOR}${USED}%${RESET}"
else
  CTX_BAR="ctx:--"
fi

TOK_DISPLAY=""
if [ -n "$TOTAL_TOK" ] && [ -n "$CTX_SIZE" ]; then
  TOK_K=$(awk "BEGIN {printf \"%.1fk\", $TOTAL_TOK/1000}")
  SIZE_K=$(awk "BEGIN {printf \"%.0fk\", $CTX_SIZE/1000}")
  TOK_DISPLAY=" ${TOK_K}/${SIZE_K}"
fi

COST_DISPLAY=""
if [ -n "$COST" ]; then
  COST_DISPLAY=" \$$(printf "%.2f" "$COST")"
fi

GIT_DISPLAY=""
if [ -n "$CWD" ]; then
  BRANCH=$(git -C "$CWD" --no-optional-locks branch --show-current 2>/dev/null || echo "")
  if [ -n "$BRANCH" ]; then
    STAGED=$(git -C "$CWD" --no-optional-locks diff --cached --quiet 2>/dev/null && echo "" || echo "+")
    DIRTY=$(git -C "$CWD" --no-optional-locks diff --quiet 2>/dev/null && echo "" || echo "*")
    GIT_DISPLAY=" | ${CYAN}git:${BRANCH}${STAGED}${DIRTY}${RESET}"
  fi
fi

LINE1=$(printf "${CYAN}%s${RESET} | %s%s%s%s" "$MODEL" "$CTX_BAR" "$TOK_DISPLAY" "$COST_DISPLAY" "$GIT_DISPLAY")

# --- Line 2: Rate limits ---
RATE_5H_BAR=""
RATE_7D_BAR=""
if [ -n "$RATE_5H" ]; then
  R5_COLOR=$(color_for "$RATE_5H")
  RATE_5H_BAR=$(make_bar "$RATE_5H" 10 "$R5_COLOR")
  RATE_5H_BAR="5h ${RATE_5H_BAR} ${R5_COLOR}${RATE_5H}%${RESET}"
fi
if [ -n "$RATE_7D" ]; then
  R7_COLOR=$(color_for "$RATE_7D")
  RATE_7D_BAR=$(make_bar "$RATE_7D" 10 "$R7_COLOR")
  RATE_7D_BAR="7d ${RATE_7D_BAR} ${R7_COLOR}${RATE_7D}%${RESET}"
fi

LINE2=""
if [ -n "$RATE_5H" ] || [ -n "$RATE_7D" ]; then
  LINE2=$(printf "Rate Limit: %s  %s" "$RATE_5H_BAR" "$RATE_7D_BAR")
fi

# Output
printf "%b\n" "$LINE1"
if [ -n "$LINE2" ]; then
  printf "%b\n" "$LINE2"
fi
