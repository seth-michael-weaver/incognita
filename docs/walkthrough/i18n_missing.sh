#!/bin/bash
# List canvas labels still untranslated in Spanish for one chapter step (dev aid, not deployed).
# usage: ./i18n_missing.sh <chapter> <step>   (runs the step ~5 s in headless Chrome with ?lang=es and dumps WT.missing)
CH=${WT_CHROME:-"/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"}; PORT=${WT_PORT:-8765}
DIR=$(wslpath "$(cmd.exe /c 'echo %TEMP%' 2>/dev/null | tr -d '\r')")
cd "$DIR" && timeout 60 "$CH" --headless=new --user-data-dir="$(wslpath -w "$DIR")\\wt_chrome_i18n_$1" --disk-cache-size=1 --disable-gpu --window-size=1440,900 --virtual-time-budget=6000 --dump-dom "http://localhost:$PORT/?shot=$1:$2&lang=es&i18ndump=1&t=$(date +%s%N)" 2>/dev/null \
 | python3 -c 'import sys,re,html; d=sys.stdin.read(); m=re.search(r"<pre id=\"i18n-missing\">(.*?)</pre>", d, re.S); print(html.unescape(m.group(1)) if m else "(no dump: page did not finish?)")'
