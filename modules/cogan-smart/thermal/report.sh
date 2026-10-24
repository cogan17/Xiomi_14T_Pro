#!/system/bin/sh
# Cogan Smart · Thermal: everything the WebUI and the Action button ask for. Output is JSON unless noted.
#
#   report.sh now                 latest sample + every sensor read right now
#   report.sh summary SECS        summary of the last SECS seconds
#   report.sh text SECS           the same summary as plain text
#   report.sh csv SECS            one CSV row per sample (text)
#   report.sh save SECS           write the summary (txt) and samples (csv) to $CT_OUT
#   report.sh status              sampler state and settings
#   report.sh pkgs                package names of the last day that have no app name yet (JSON list)
#   report.sh labels PKG HEX ...  app names from the root manager, UTF-8 hex-encoded (the WebUI asks)
#   report.sh set KEY VALUE ...   change settings (only known keys, plain numbers within range)
#   report.sh start | stop        start or stop the sampler
#   report.sh clear               delete the recorded history

CS_LANG=id
if [ "$1" = --lang ]; then [ "$2" = en ] && CS_LANG=en; shift 2; fi
MODDIR=${0%/*}; [ "$MODDIR" = "$0" ] && MODDIR=.   # started as "sh report.sh"
. "$MODDIR/common.sh"
load_config

persist_config() { write_config || { echo '{"ok":0,"error":"Gagal menyimpan setelan"}'; exit 0; }; }

now=$(date +%s)
tzoff=$(date +%z | awk '{ s = substr($0, 1, 1) == "-" ? -1 : 1; print s * (substr($0, 2, 2) * 3600 + substr($0, 4, 2) * 60) }')
kfile=$CT_DATA/kernels.tsv
[ -f "$kfile" ] || kfile=/dev/null
mfile=$CT_DATA/modes.tsv   # written by Cogan Smart · Power when installed
[ -f "$mfile" ] || mfile=/dev/null

# SECS as a number between one minute and 31 days (one hour when missing or not a number).
secs_arg() {
  case "$1" in ''|*[!0-9]*) echo 3600; return ;; esac
  if [ "$1" -lt 60 ]; then echo 60; elif [ "$1" -gt 2678400 ]; then echo 2678400; else echo "$1"; fi
}

run_awk() {   # run_awk MODE SECS FILES...
  mode=$1; secs=$2; shift 2
  awk -v mode="$mode" -v since=$((now - secs)) -v now="$now" -v secs="$secs" -v HOT=$((HOT_TEMP * 10)) \
      -v TZOFF="$tzoff" -v KFILE="$kfile" -v MFILE="$mfile" -v fresh="$fresh" -v release="$release" -v running="$running" \
      -v sensor_ts="${SS_TS:-0}" -v health="${cs_health:-null}" -v LANG="$CS_LANG" -v LABELS="$CT_DATA/labels.tsv" -v SKIP="$skip" \
      -f "$MODDIR/thermal.awk" -f "$MODDIR/report.awk" "$kfile" "$mfile" "$@"
}

# Day files that can hold samples from the last SECS seconds.
data_files() {
  min=$(awk -v mode=date -v since=$((now - $1)) -v TZOFF="$tzoff" -f "$MODDIR/thermal.awk" -f "$MODDIR/report.awk" < /dev/null)
  ls "$CT_DATA"/data/*.tsv 2>/dev/null | awk -v min="$min.tsv" '{ n = $0; sub(/.*\//, "", n); if (n >= min) print }'
}

report() {   # report MODE SECS
  run_awk "$1" "$2" $(data_files "$2")
}

sampler_pid() { safe_pid "$CT_RUN/sampler.pid" "$MODDIR/sampler.sh"; }

wake() { pid=$(sampler_pid) && kill -HUP "$pid" 2>/dev/null; return 0; }

start_sampler() {
  [ -n "$(sampler_pid)" ] && return 0
  mkdir -p "$CT_RUN"
  set -- sh "$MODDIR/sampler.sh"
  command -v nice > /dev/null 2>&1 && set -- nice -n 10 "$@"
  if command -v setsid > /dev/null 2>&1; then
    setsid "$@" < /dev/null > /dev/null 2>&1 &
  else
    nohup "$@" < /dev/null > /dev/null 2>&1 &
  fi
  i=0
  while [ $i -lt 30 ] && [ -z "$(sampler_pid)" ]; do sleep 0.1; i=$((i + 1)); done
  [ -n "$(sampler_pid)" ]
}

stop_sampler() {
  if pid=$(sampler_pid); then
    kill "$pid" 2>/dev/null || return 1
    i=0
    while [ $i -lt 60 ] && sampler_pid >/dev/null; do sleep 0.1; i=$((i + 1)); done
    sampler_pid >/dev/null && return 1
  fi
  bridge_heartbeat thermal 0
  rm -f "$CT_RUN/sampler.pid" "$CT_RUN/latest"
}

status_json() {
  thermal_health
  pid=$(sampler_pid) || pid=0
  days=$(ls "$CT_DATA"/data/*.tsv 2>/dev/null | wc -l)
  first=$(ls "$CT_DATA"/data/*.tsv 2>/dev/null | head -n 1)
  first=${first##*/}; first=${first%.tsv}
  size=$(du -sk "$CT_DATA/data" 2>/dev/null | awk '{ print $1 + 0 }')
  version=$(sed -n 's/^version=//p' "$MODROOT/module.prop" 2>/dev/null)
  printf '{"running":%d,"pid":%d,"version":"%s","interval":%d,"retention":%d,"hot":%d,"notify":%d,"notify_temp":%d,' \
    "$([ "$pid" -gt 0 ] && echo 1 || echo 0)" "$pid" "$version" "$INTERVAL" "$RETENTION_DAYS" "$HOT_TEMP" "$NOTIFY" "$NOTIFY_TEMP"
  printf '"days":%d,"first":"%s","size_kb":%d,"out":"%s"' "$days" "$first" "${size:-0}" "$CT_OUT"
  printf ',"autostart":%d,"kernel":' "$AUTOSTART"; kernel_json
  printf ',"device":'; device_json
  [ "$1" = brief ] || { printf ',"cooling":'; cooling_json; }
  printf ',"power":'; peer_json "$CP_MOD" "$CP_DATA/run/pid" power/controller.sh
  printf ',"power_mode":'; json_string "$(cat "$CP_DATA/run/mode" 2>/dev/null)"
  printf ',"monitor":'; thermal_health_json
  printf '}\n'
}

validate_values() {
  [ $# -gt 0 ] && [ $(( $# % 2 )) = 0 ] || return 1
  while [ $# -ge 2 ]; do
    uint "$2" || return 1
    case "$1" in
      INTERVAL) lo=10; hi=300 ;;
      RETENTION_DAYS) lo=1; hi=30 ;;
      HOT_TEMP) lo=35; hi=50 ;;
      NOTIFY_TEMP) lo=38; hi=55 ;;
      NOTIFY|AUTOSTART) lo=0; hi=1 ;;
      *) return 1 ;;
    esac
    [ "$2" -ge "$lo" ] && [ "$2" -le "$hi" ] || return 1
    eval "$1=\$2"
    shift 2
  done
}

set_values() {
  if ! validate_values "$@"; then
    echo '{"ok":0,"error":"Nilai tidak valid; tidak ada setelan disimpan"}'; return
  fi
  if write_config; then echo '{"ok":1}'; else echo '{"ok":0,"error":"Gagal menyimpan"}'; fi
}

save_log() {
  secs=$(secs_arg "$1")
  dir=$CT_OUT
  if ! mkdir -p "$dir" 2>/dev/null || ! [ -w "$dir" ]; then dir=$CT_DATA/logs; mkdir -p "$dir"; fi
  minutes=$((secs / 60))
  if [ $((minutes % 1440)) = 0 ]; then span="$((minutes / 1440))hari"
  elif [ $((minutes % 60)) = 0 ]; then span="$((minutes / 60))jam"
  else span="${minutes}menit"; fi
  name=cogan-thermal_$(date +%Y-%m-%d_%H-%M-%S)_$span
  files=$(data_files "$secs")
  device=$(getprop ro.product.marketname 2>/dev/null)
  [ -n "$device" ] || device=$(getprop ro.product.model 2>/dev/null)
  {
    run_awk text "$secs" $files
    echo
    if [ "$CS_LANG" = en ]; then
      echo "Device: ${device:-?} · Android $(getprop ro.build.version.release 2>/dev/null) · kernel $(kernel_release)"
      if bridge_available; then echo 'Identity: verified through Cogan Bridge (compile-time)'
      else echo 'Identity: /proc or uname candidate, unverified'; fi
      echo "Visible uname: $(uname -r)"
      echo "Module: $(sed -n 's/^version=//p' "$MODROOT/module.prop" 2>/dev/null) · sample every $INTERVAL seconds · hot = phone body ≥ $HOT_TEMP °C"
      echo
      echo 'Sample details:'
    else
      echo "Perangkat: ${device:-?} · Android $(getprop ro.build.version.release 2>/dev/null) · kernel $(kernel_release)"
      if bridge_available; then echo 'Identitas: terverifikasi melalui Cogan Bridge (compile-time)'
      else echo 'Identitas: kandidat /proc atau uname, belum terverifikasi'; fi
      echo "uname yang terlihat: $(uname -r)"
      echo "Modul: $(sed -n 's/^version=//p' "$MODROOT/module.prop" 2>/dev/null) · cek tiap $INTERVAL detik · panas = Badan HP ≥ $HOT_TEMP °C"
      echo
      echo 'Detail per sampel:'
    fi
    run_awk detail "$secs" $files
  } > "$dir/$name.txt"
  run_awk csv "$secs" $files > "$dir/$name.csv"
  rows=$(($(wc -l < "$dir/$name.csv") - 1))
  # Let the gallery/file pickers see the new files right away (best effort).
  for f in "$dir/$name.txt" "$dir/$name.csv"; do
    am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d "file://$f" > /dev/null 2>&1 &
  done
  printf '{"ok":1,"samples":%d,"dir":"%s","txt":"%s","csv":"%s"}\n' "$rows" "$dir" "$dir/$name.txt" "$dir/$name.csv"
}

# App names the root manager knows (owner 2026-10-24: a spoofed manager showed as weonse.bxmfmy.qeomje).
# The WebUI sends PKG HEX pairs, HEX being the UTF-8 name, because its commands take plain tokens only.
# Names with control characters or over 60 bytes are dropped; the newest name of a package wins.
learn_labels() {
  mkdir -p "$CT_DATA"
  printf '%s\n' "$@" | LC_ALL=C awk -v old="$CT_DATA/labels.tsv" '
    BEGIN { while ((getline line < old) > 0) if (split(line, kv, "\t") == 2) n[kv[1]] = kv[2]; close(old)
            for (i = 0; i < 16; i++) H[substr("0123456789abcdef", i + 1, 1)] = i }
    NR % 2 == 1 { pkg = $0; next }
    pkg ~ /^[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z0-9_]+)+$/ && $0 ~ /^([0-9a-f][0-9a-f])+$/ && length($0) <= 120 {
      s = ""; ok = 1
      for (i = 1; i < length($0); i += 2) {
        b = H[substr($0, i, 1)] * 16 + H[substr($0, i + 1, 1)]
        if (b < 32 || b == 127) { ok = 0; break }
        s = s sprintf("%c", b)
      }
      if (ok) n[pkg] = s
    }
    END { for (p in n) print p "\t" n[p] }' > "$CT_DATA/labels.tsv.tmp" && mv "$CT_DATA/labels.tsv.tmp" "$CT_DATA/labels.tsv"
  printf '{"ok":1,"labels":%d}\n' "$(wc -l < "$CT_DATA/labels.tsv")"
}

case "$1" in now|summary|text|csv|detail|status|cooling|pkgs) ;; *)
  mkdir -p "$CT_RUN"
  lock_take "$CT_DATA/api.lock" || { echo '{"ok":0,"error":"Perintah lain sedang berjalan"}'; exit 0; }
  trap 'lock_drop "$CT_DATA/api.lock"' EXIT
  load_config
  ;;
esac
case "$1" in
  now)
    sensor_snapshot
    fresh=$SS_ZONES
    release=$(kernel_release)
    thermal_health; running=$CS_RUNNING; cs_health=$(thermal_health_json)
    skip=$(tr '\n' ',' 2>/dev/null < "$CT_RUN/stuck")   # sensors the sampler found stuck
    latest=$(ls "$CT_DATA"/data/*.tsv 2>/dev/null | tail -n 1)
    run_awk now 0 ${latest:-/dev/null}
    ;;
  summary) report json "$(secs_arg "$2")" ;;
  pkgs) report pkgs 86400 ;;
  labels) shift; learn_labels "$@" ;;
  text) report text "$(secs_arg "$2")" ;;
  csv) report csv "$(secs_arg "$2")" ;;
  detail) report detail "$(secs_arg "$2")" ;;
  save) save_log "$2" ;;
  status) status_json "$2" ;;
  cooling) cooling_json; printf '\n' ;;
  set) shift; set_values "$@" ;;
  apply|force)
    shift
    if [ $# -gt 0 ] && ! validate_values "$@"; then echo '{"ok":0,"error":"Nilai tidak valid"}'; exit 0; fi
    AUTOSTART=1; persist_config
    if start_sampler; then wake; status_json brief; else echo '{"ok":0,"error":"Pencatat gagal mulai"}'; fi ;;
  start)
    AUTOSTART=1; persist_config
    if start_sampler; then status_json brief; else echo '{"ok":0,"error":"Pencatat gagal mulai"}'; fi ;;
  stop)
    AUTOSTART=0; save_failed=0; write_config || save_failed=1
    if stop_sampler; then
      [ "$save_failed" = 0 ] || { echo '{"ok":0,"error":"Berhenti, tetapi setelan berhenti gagal disimpan untuk reboot"}'; exit 0; }; status_json
    else echo '{"ok":0,"error":"Pencatat belum berhenti"}'; fi ;;
  restart)
    if stop_sampler; then AUTOSTART=1; persist_config; start_sampler; status_json
    else echo '{"ok":0,"error":"Pencatat belum berhenti"}'; fi ;;
  reset)
    if ! stop_sampler; then echo '{"ok":0,"error":"Reset dibatalkan: pencatat belum berhenti"}'; exit 0; fi
    defaults; AUTOSTART=0; persist_config
    status_json brief ;;
  clear)
    was_running=0; sampler_pid >/dev/null && was_running=1
    stop_sampler || { echo '{"ok":0,"error":"Pencatat belum berhenti"}'; exit 0; }
    rm -f "$CT_DATA"/data/*.tsv "$CT_RUN/cpu.prev" "$CT_RUN/pids.prev" "$CT_RUN/net.prev" "$CT_RUN/last" "$CT_RUN/notified"
    printf '%s\t%s\n' "$now" "$(kernel_release)" > "$CT_DATA/kernels.tsv"
    # Keep the Cogan Smart · Power mode that is active now.
    current=$(tail -n 1 "$CT_DATA/modes.tsv" 2>/dev/null | cut -f 2)
    [ -n "$current" ] && printf '%s\t%s\n' "$now" "$current" > "$CT_DATA/modes.tsv"
    [ "$was_running" = 1 ] && start_sampler
    echo '{"ok":1}'
    ;;
  *)
    echo "Pakai: report.sh now|summary SECS|text SECS|csv SECS|save SECS|status|pkgs|labels PKG HEX ...|set KEY VALUE|apply|start|stop|restart|reset|clear" >&2
    exit 1
    ;;
esac
