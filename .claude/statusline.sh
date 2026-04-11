#!/bin/bash
input=$(cat)

# Parse all values at once using node (jq not available on all systems)
eval $(node -e "
const d = JSON.parse(process.argv[1]);
const u = d.context_window?.used_percentage ?? '';
const cur = d.context_window?.current_usage ?? {};
const total = (cur.input_tokens||0)+(cur.cache_creation_input_tokens||0)+(cur.cache_read_input_tokens||0)+(cur.output_tokens||0);
const ctxSize = d.context_window?.context_window_size ?? 1000000;
const cost = d.cost?.total_cost_usd ?? '';
const model = d.model?.display_name ?? 'Claude';
const cwd = d.cwd ?? '';
console.log('USED=\"'+u+'\"');
console.log('TOTAL_TOK=\"'+total+'\"');
console.log('CTX_SIZE=\"'+ctxSize+'\"');
console.log('COST=\"'+cost+'\"');
console.log('MODEL=\"'+model+'\"');
console.log('CWD=\"'+cwd+'\"');
" "$input" 2>/dev/null)

# Context bar
if [ -n "$USED" ]; then
  BAR_LEN=20
  FILLED=$(awk "BEGIN {v=int($USED / 100 * $BAR_LEN); if(v<1 && $USED>0) v=1; printf \"%d\", v}")
  BAR=""
  i=0; while [ $i -lt $FILLED ]; do BAR="${BAR}█"; i=$((i+1)); done
  while [ $i -lt $BAR_LEN ]; do BAR="${BAR}░"; i=$((i+1)); done
  CTX_DISPLAY="${BAR} ${USED}%"
else
  CTX_DISPLAY="ctx:--"
fi

# Tokens (current usage / context size)
TOK_DISPLAY=""
if [ -n "$TOTAL_TOK" ] && [ -n "$CTX_SIZE" ]; then
  TOK_K=$(awk "BEGIN {printf \"%.1fk\", $TOTAL_TOK/1000}")
  SIZE_K=$(awk "BEGIN {printf \"%.0fk\", $CTX_SIZE/1000}")
  TOK_DISPLAY=" ${TOK_K}/${SIZE_K}"
fi

# Cost
COST_DISPLAY=""
if [ -n "$COST" ]; then
  COST_DISPLAY=" \$$(printf "%.2f" "$COST")"
fi

# Git
GIT_DISPLAY=""
if [ -n "$CWD" ]; then
  BRANCH=$(git -C "$CWD" --no-optional-locks branch --show-current 2>/dev/null || echo "")
  if [ -n "$BRANCH" ]; then
    STAGED=$(git -C "$CWD" --no-optional-locks diff --cached --quiet 2>/dev/null && echo "" || echo "+")
    DIRTY=$(git -C "$CWD" --no-optional-locks diff --quiet 2>/dev/null && echo "" || echo "*")
    GIT_DISPLAY=" | git:${BRANCH}${STAGED}${DIRTY}"
  fi
fi

printf "%s | %s%s%s%s\n" "$MODEL" "$CTX_DISPLAY" "$TOK_DISPLAY" "$COST_DISPLAY" "$GIT_DISPLAY"
