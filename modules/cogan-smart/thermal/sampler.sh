#!/system/bin/sh
# Cogan Smart · Thermal: background sampler. Every INTERVAL seconds it appends one line to
# $CT_DATA/data/<date>.tsv with every temperature and what the phone was doing at that moment:
#
#   ts  app  screen  charging  current_mA  battery_t10  cpu_x10  kernel_x10  gpu  top  net  freqs  zones  cap
#
# top = "name:pct_x10;..." (busiest user processes), net = "wifi:kB/s,cell:kB/s",
# zones = "type=tenths_of_degC,...", cap = CPU cap of Cogan Smart · Power "big%/little%/step" or "-"
# (since v2.9.1). Usage: sampler.sh [--once]

MODDIR=${0%/*}; [ "$MODDIR" = "$0" ] && MODDIR=.   # started as "sh report.sh"
. "$MODDIR/common.sh"

sample() {
  now=$(date +%s)
  mkdir -p "$CT_DATA/data" "$CT_RUN"
  bridge_heartbeat thermal "$(module_code)"

  # CPU since the previous sample: the whole phone, kernel threads and the busiest processes.
  cpu_now=$(head -n 1 "$CT_PROC/stat")
  cpu_prev=$(cat "$CT_RUN/cpu.prev" 2>/dev/null)
  cat "$CT_PROC"/[0-9]*/stat > "$CT_RUN/pids.new" 2>/dev/null
  [ -f "$CT_RUN/pids.prev" ] || : > "$CT_RUN/pids.prev"
  awk -v prev="$cpu_prev" -v cur="$cpu_now" -f "$MODDIR/cpu.awk" "$CT_RUN/pids.prev" "$CT_RUN/pids.new" \
    > "$CT_RUN/cpu.out" 2>/dev/null
  mv "$CT_RUN/pids.new" "$CT_RUN/pids.prev"
  echo "$cpu_now" > "$CT_RUN/cpu.prev"
  cpu=-1; kernel=-1; top=""
  while read -r kind a b c; do
    case "$kind" in
      C) cpu=$a; kernel=$b ;;
      P) top="$top${top:+;}$(proc_name "$b" "$c"):$a" ;;
    esac
  done < "$CT_RUN/cpu.out"

  # Network speed since the previous sample.
  set -- $(read_net_bytes)
  wifi=$1; cell=$2
  net="-"
  if read -r pts pwifi pcell < "$CT_RUN/net.prev" 2>/dev/null && [ "$now" -gt "$pts" ]; then
    dt=$((now - pts))
    net="wifi:$(((wifi - pwifi) / 1024 / dt)),cell:$(((cell - pcell) / 1024 / dt))"
  fi
  echo "$now $wifi $cell" > "$CT_RUN/net.prev"

  screen=$(read_screen)
  if [ "$screen" = 0 ]; then app=screen_off; else app=$(read_foreground); fi
  set -- $(read_battery)
  charging=$1; current=$2; battery=$3
  gpu=$(read_gpu)
  freqs=$(read_freqs)
  zones=$(read_zones)
  power_cap

  day=$(date +%Y-%m-%d)
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$now" "$app" "$screen" "$charging" "$current" \
    "$battery" "$cpu" "$kernel" "$gpu" "${top:--}" "$net" "$freqs" "${zones:--}" "$cap" > "$CT_RUN/sample.tsv"
  cat "$CT_RUN/sample.tsv" >> "$CT_DATA/data/$day.tsv"
  echo "$now" > "$CT_RUN/last"

  # Short report of this sample for other modules (Cogan Smart · Power reads it):
  # ts  main_temp  battery_temp  charging  app_label  cause (from the last few samples, see report.awk)
  # The last 40 samples also show a sensor stuck at one value (written to run/stuck for live reads).
  tail -n 40 "$CT_DATA/data/$day.tsv" > "$CT_RUN/recent.tsv"
  awk -v mode=latest -v since=0 -v now=$((now + 1)) -v HOT=$((HOT_TEMP * 10)) -v LABELS="$CT_DATA/labels.tsv" \
      -v STUCKFILE="$CT_RUN/stuck" -f "$MODDIR/thermal.awk" -f "$MODDIR/report.awk" "$CT_RUN/recent.tsv" > "$CT_RUN/latest.tmp" 2>/dev/null
  [ -s "$CT_RUN/latest.tmp" ] && mv "$CT_RUN/latest.tmp" "$CT_RUN/latest"
  IFS='	' read -r _ main _ _ label _ < "$CT_RUN/latest" 2>/dev/null
  [ "$NOTIFY" = 1 ] || return 0
  body=$(body_temp "$zones")
  case "$body" in ''|*[!0-9-]*|-9999) body=$battery ;; esac   # no phone body sensor: the battery
  alert "$now" "$label" "$cpu" "$gpu" "$body"
}

# cap = the CPU cap Cogan Smart · Power applies right now as "big%/little%/step" (step 0: no heat step),
# or "-" when its controller wrote no state in the last minute. Shell builtins only, no extra process.
power_cap() {
  cap=-; pc_state=""
  IFS= read -r pc_state < "$CP_DATA/run/state.json" 2>/dev/null || :
  pc_ts=${pc_state#*\"ts\":}; pc_ts=${pc_ts%%[!0-9]*}
  case "$pc_ts" in ''|*[!0-9]*) return 0 ;; esac
  [ $((now - pc_ts)) -le 60 ] && [ $((pc_ts - now)) -le 5 ] || return 0
  pc_big=${pc_state#*\"big\":}; pc_big=${pc_big%%[!0-9]*}
  pc_little=${pc_state#*\"little\":}; pc_little=${pc_little%%[!0-9]*}
  pc_level=${pc_state#*\"level\":}; pc_level=${pc_level%%[!0-9]*}   # the first "level" is the step
  [ -n "$pc_big" ] && [ -n "$pc_little" ] && [ -n "$pc_level" ] && cap="$pc_big/$pc_little/$pc_level"
  return 0
}

# Optional heat notification (NOTIFY=1), on the phone body, at most once every 10 minutes.
alert() {   # alert TS APP_LABEL CPU GPU BODY_TEMP
  [ "$NOTIFY" = 1 ] || return 0
  body=$5
  case "$body" in ''|*[!0-9-]*) return 0 ;; esac
  [ "$body" -ge $((NOTIFY_TEMP * 10)) ] || return 0
  last=$(cat "$CT_RUN/notified" 2>/dev/null || echo 0)
  [ $(($1 - last)) -ge 600 ] || return 0
  echo "$1" > "$CT_RUN/notified"
  text="Badan HP $((body / 10)) °C · $2"
  [ "$3" -ge 0 ] && text="$text · CPU $(($3 / 10))%"
  [ "$4" -ge 0 ] && text="$text · GPU $4%"
  cmd notification post -S bigtext -t "🔥 Cogan Thermal" cogan_thermal "$text" > /dev/null 2>&1 \
    || su 2000 -c "cmd notification post -S bigtext -t 'Cogan Thermal' cogan_thermal '$text'" > /dev/null 2>&1
}

prune() {
  find "$CT_DATA/data" -name '*.tsv' -mtime +"$RETENTION_DAYS" -exec rm -f {} + 2>/dev/null
}

load_config
mkdir -p "$CT_DATA/data" "$CT_RUN"
if [ "$1" = "--once" ]; then
  sample
  exit 0
fi

lock_take "$CT_RUN/daemon.lock" || exit 1
date +%s > "$CT_RUN/started"
echo $$ > "$CT_RUN/sampler.pid"
stop=0; sleeper=""
cleanup() {
  bridge_heartbeat thermal 0
  rm -f "$CT_RUN/sampler.pid" "$CT_RUN/latest"
  lock_drop "$CT_RUN/daemon.lock"
}
trap cleanup EXIT
trap 'stop=1; [ -n "$sleeper" ] && kill "$sleeper" 2>/dev/null' TERM INT
trap '[ -n "$sleeper" ] && kill "$sleeper" 2>/dev/null' HUP
# Kernel in use from now on, so reports can compare kernels (e.g. Cogan r3 against stock).
printf '%s\t%s\n' "$(date +%s)" "$(kernel_release)" >> "$CT_DATA/kernels.tsv"
count=0
while :; do
  [ -f "$MODROOT/disable" ] || [ -f "$MODROOT/remove" ] && break
  sample
  count=$((count + 1))
  [ $((count % 180)) = 1 ] && prune
  [ "$stop" = 1 ] && break
  sleep "$INTERVAL" &
  sleeper=$!
  wait "$sleeper"
  sleeper=""
  load_config
done
