# Cogan Smart · Thermal: helpers shared by report.awk and the sampler's alert check.
# Plain POSIX awk (Android's one-true-awk): no gawk extensions, no strftime.
function tr(id, en) { return LANG == "en" ? en : id }

# Sensor group of a thermal zone type. Order matters: specific names before the generic CPU match.
function group(type,   t) {
    t = tolower(type)
    if (t ~ /gpu|mali/) return "gpu"
    if (t ~ /batt|^bat_|_bat|bms/) return "bat"
    if (t ~ /charg|chg|usb|wlc|vbus/) return "chg"
    if (t ~ /skin|shell|back|board|ap_ntc|case|frame|xo_therm|quiet|ltepa_ntc/) return "skin"
    if (t ~ /apu|npu|^ai|vpu|mdla/) return "apu"
    if (t ~ /modem|^md|mdpa|^pa_|_pa_|^pa$|nrpa|^nr|lte|rfic|^rf_|5g|sdr/) return "modem"
    if (t ~ /pmic|vcore|buck/) return "pmic"
    if (t ~ /wifi|wlan|conn/) return "wifi"
    if (t ~ /cpu|soc|mcu|cluster|tsens|cpuss|core|tzts|^ap/) return "cpu"
    return "other"
}

function group_name(g) {
    return g == "cpu" ? tr("Prosesor", "Processor") : g == "gpu" ? "GPU" : g == "bat" ? tr("Baterai", "Battery") : g == "skin" ? tr("Badan HP", "Phone body") : \
           g == "modem" ? "Modem" : g == "chg" ? "Charger" : g == "pmic" ? "PMIC" : g == "apu" ? "AI (APU)" : \
           g == "wifi" ? "Wi-Fi" : tr("Lainnya", "Other")
}

# Friendly names for common packages, then the app names the root manager reported for this phone
# (LABELS, see report.sh labels); anything else keeps its package name.
function label(pkg,   l) {
    if (pkg == "" || pkg == "-") return tr("Tidak diketahui", "Unknown")
    if (pkg == "screen_off") return tr("Layar mati", "Screen off")
    if (pkg == "com.instagram.android") return "Instagram"
    if (pkg == "com.mobile.legends" || pkg ~ /^com\.mobile\.legends/) return "Mobile Legends"
    if (pkg == "com.whatsapp" || pkg == "com.whatsapp.w4b") return "WhatsApp"
    if (pkg == "com.google.android.youtube") return "YouTube"
    if (pkg == "com.zhiliaoapp.musically" || pkg == "com.ss.android.ugc.trill") return "TikTok"
    if (pkg == "com.facebook.katana") return "Facebook"
    if (pkg == "com.facebook.orca") return "Messenger"
    if (pkg == "org.telegram.messenger" || pkg == "org.telegram.messenger.web") return "Telegram"
    if (pkg == "com.android.chrome") return "Chrome"
    if (pkg == "com.tencent.ig") return "PUBG Mobile"
    if (pkg == "com.dts.freefireth" || pkg == "com.dts.freefiremax") return "Free Fire"
    if (pkg == "com.miHoYo.GenshinImpact") return "Genshin Impact"
    if (pkg == "com.HoYoverse.hkrpgoversea") return "Honkai: Star Rail"
    if (pkg == "com.levelinfinite.sgameGlobal") return "Honor of Kings"
    if (pkg == "com.roblox.client") return "Roblox"
    if (pkg == "com.spotify.music") return "Spotify"
    if (pkg == "com.netflix.mediaclient") return "Netflix"
    if (pkg == "com.shopee.id") return "Shopee"
    if (pkg == "com.tokopedia.tkpd") return "Tokopedia"
    if (pkg == "com.gojek.app") return "Gojek"
    if (pkg == "com.grabtaxi.passenger") return "Grab"
    if (pkg == "com.google.android.apps.maps") return "Google Maps"
    if (pkg == "com.android.camera" || pkg == "com.android.camera2") return tr("Kamera", "Camera")
    if (pkg == "com.miui.home" || pkg == "com.mi.android.globallauncher") return tr("Layar utama (launcher)", "Home screen (launcher)")
    if (pkg == "com.android.systemui") return "System UI"
    if (pkg == "system_server") return tr("Sistem Android", "Android system")
    if (pkg == "surfaceflinger") return tr("SurfaceFlinger (tampilan)", "SurfaceFlinger (display)")
    if (pkg == "com.termux") return "Termux"
    l = learned(pkg)
    return l != "" ? l : pkg
}
function learned(pkg,   line, kv) {
    if (!LBL_READ) {
        LBL_READ = 1
        if (LABELS != "") { while ((getline line < LABELS) > 0) if (split(line, kv, "\t") == 2) LBL[kv[1]] = kv[2]; close(LABELS) }
    }
    return (pkg in LBL) ? LBL[pkg] : ""
}

# The power part's modes, as written to modes.tsv.
function mode_name(m) {
    return m == "seimbang" ? "Kernel Default" : m == "game" ? tr("Performa", "Performance") : m == "hemat" ? tr("Hemat", "Power saver") : tr("Kontrol daya mati", "Power control off")
}

# Local wall clock from epoch seconds, using TZOFF (seconds east of UTC).
function days_to_date(z,   era, doe, yoe, y, doy, mp, d, m) {   # Howard Hinnant's civil_from_days
    z += 719468
    era = int((z >= 0 ? z : z - 146096) / 146097)
    doe = z - era * 146097
    yoe = int((doe - int(doe / 1460) + int(doe / 36524) - int(doe / 146096)) / 365)
    y = yoe + era * 400
    doy = doe - (365 * yoe + int(yoe / 4) - int(yoe / 100))
    mp = int((5 * doy + 2) / 153)
    d = doy - int((153 * mp + 2) / 5) + 1
    m = mp < 10 ? mp + 3 : mp - 9
    return sprintf("%04d-%02d-%02d", y + (m <= 2), m, d)
}
function local_date(ts) { return days_to_date(int((ts + TZOFF) / 86400)) }
function local_clock(ts,   s) { s = (ts + TZOFF) % 86400; if (s < 0) s += 86400; return sprintf("%02d:%02d", int(s / 3600), int((s % 3600) / 60)) }

function deg(tenths) { return sprintf("%.1f", tenths / 10) }
function jesc(s) { gsub(/\\/, "\\\\", s); gsub(/"/, "\\\"", s); return s }

# Hottest CPU/GPU zone of a sample's zone list ("type=tenths,..."), or the hottest of all.
function main_temp(zones,   n, z, i, kv, g, best, any) {
    best = -9999; any = -9999
    n = split(zones, z, ",")
    for (i = 1; i <= n; i++) {
        if (split(z[i], kv, "=") != 2) continue
        kv[2] += 0
        if (kv[2] > any) any = kv[2]
        g = group(kv[1])
        if ((g == "cpu" || g == "gpu") && kv[2] > best) best = kv[2]
    }
    return best > -9999 ? best : any
}

# The phone body (Badan HP) of a zone list, or -9999 when the phone has no body sensor. Owner 2026-10-24:
# "hot" and the power modes follow what a hand feels, not the processor (about 50 °C at rest). HyperOS's
# own body temperature (hyperos_board) when it is there, so every card and HyperOS show one number
# (owner's 6-hour log: within -0.7..+0.3 °C of quiet_therm 90% of the time); else the hottest skin zone.
function body_temp(zones,   n, z, i, kv, best) {
    best = -9999
    n = split(zones, z, ",")
    for (i = 1; i <= n; i++) {
        if (split(z[i], kv, "=") != 2) continue
        if (kv[1] == "hyperos_board") return kv[2] + 0
        if (group(kv[1]) == "skin" && kv[2] + 0 > best) best = kv[2] + 0
    }
    return best
}
