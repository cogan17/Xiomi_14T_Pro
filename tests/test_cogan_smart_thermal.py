#!/usr/bin/env python3
"""Offline tests for the thermal part of Cogan Smart Kernel against a fake /sys and /proc.

The module runs on Android with mksh and one-true-awk; these tests use them when installed
(mksh, original-awk) and otherwise the runner's POSIX sh and awk. THERMAL_SH / THERMAL_AWK pick others.
"""
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "modules/cogan-smart"
SHELL = os.environ.get("THERMAL_SH") or shutil.which("mksh") or shutil.which("dash") or "/bin/sh"
AWK = os.environ.get("THERMAL_AWK") or shutil.which("original-awk") or shutil.which("awk")

ZONES = {
    "soc_max": "55000", "cpu-big-core0": "52300", "gpu1": "48000", "battery": "36000", "shell_back": "39000",
    "md_pa": "41000", "apu": "40000", "board_ntc": "38000", "unused_sensor": "0", "broken": "-274000",
}


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def proc_stat(pid, comm, ppid, utime, stime):
    return f"{pid} ({comm}) S {ppid} {pid} 0 0 -1 4194560 100 0 0 0 {utime} {stime} 0 0 20 0 1 0 100 0 0\n"


class FakePhone:
    def __init__(self, base):
        self.base = base
        self.sys = base / "sys"
        self.proc = base / "proc"
        self.data = base / "data"
        self.out = base / "sdcard/Download/CoganThermal"
        self.bin = base / "bin"
        self.root = base / "smart"
        shutil.copytree(MODULE, self.root)
        self.mod = self.root / "thermal"
        for index, (kind, temp) in enumerate(ZONES.items()):
            write(self.sys / f"class/thermal/thermal_zone{index}/type", kind + "\n")
            write(self.sys / f"class/thermal/thermal_zone{index}/temp", temp + "\n")
        battery = self.sys / "class/power_supply/battery"
        write(battery / "status", "Charging\n")
        write(battery / "current_now", "-2100000\n")
        write(battery / "temp", "361\n")
        write(self.sys / "kernel/ged/hal/gpu_utilization", "65 0 0\n")
        write(self.sys / "class/backlight/panel0-backlight/brightness", "1200\n")
        for policy, khz in (("0", "1800000"), ("4", "2850000"), ("7", "3250000")):
            write(self.sys / f"devices/system/cpu/cpufreq/policy{policy}/scaling_cur_freq", khz + "\n")
        self.set_net(0, 0)
        self.set_cpu(0)
        self.bin.mkdir()
        tools = {
            "dumpsys": "case \"$2\" in displays) echo '  mCurrentFocus=Window{1a2b u0 com.mobile.legends/com.moba.Unity}' ;; esac",
            "uname": "echo 6.1.177-Cogan-r3",
            "getprop": "case \"$1\" in sys.boot_completed) echo 1 ;; ro.product.model) echo TestPhone ;; "
                       "ro.build.version.release) echo 15 ;; esac",
            "am": "exit 0",
            "cmd": f"echo \"$*\" >> {base}/notifications",
        }
        for name, body in tools.items():
            write(self.bin / name, "#!/bin/sh\n" + body + "\n")
            (self.bin / name).chmod(0o755)
        os.symlink(SHELL, self.bin / "sh")
        os.symlink(AWK, self.bin / "awk")
        self.power = base / "power"   # Cogan Smart · Power's data (its controller state)
        self.env = dict(os.environ, PATH=f"{self.bin}:{os.environ['PATH']}", TZ="WIB-7", CP_DATA=str(self.power),
                        CT_DATA=str(self.data), CT_SYS=str(self.sys), CT_PROC=str(self.proc), CT_OUT=str(self.out))

    def set_net(self, wifi, cell):
        for name, total in (("wlan0", wifi), ("ccmni0", cell)):
            write(self.sys / f"class/net/{name}/statistics/rx_bytes", f"{total}\n")
            write(self.sys / f"class/net/{name}/statistics/tx_bytes", "0\n")

    def set_cpu(self, step):
        # 8 cores; each step adds 1000 ticks of which 400 busy. The game uses 250, a kworker 80.
        busy, idle = 1000 + 400 * step, 8000 + 600 * step
        write(self.proc / "stat", f"cpu  {busy} 0 0 {idle} 0 0 0 0 0 0\ncpu0 1 0 0 1 0 0 0 0 0 0\n")
        procs = ((1, "init", 0, 10, 10, "/system/bin/init"), (2, "kthreadd", 0, 0, 0, ""),
                 (4321, "kworker/u16:2", 2, 50 + 80 * step, 0, ""),
                 (5000, "UnityMain", 600, 100 + 200 * step, 50 + 50 * step, "com.mobile.legends"),
                 (6000, "Binder:900_1", 600, 20 + 30 * step, 0, "com.google.android.gms:persistent"))
        for pid, comm, ppid, utime, stime, cmdline in procs:
            write(self.proc / f"{pid}/stat", proc_stat(pid, comm, ppid, utime, stime))
            write(self.proc / f"{pid}/cmdline", cmdline + ("\0" if cmdline else ""))

    def run(self, script, *args, check=True):
        result = subprocess.run([str(self.bin / "sh"), str(self.mod / script), *args], env=self.env,
                                capture_output=True, text=True, timeout=60)
        if check and result.returncode:
            raise AssertionError(f"{script} {args}: {result.returncode}\n{result.stdout}\n{result.stderr}")
        return result.stdout

    def report(self, *args):
        return self.run("report.sh", *args)


def sample(ts, app, zones, charging=0, current=300, cpu=150, kernel=20, gpu=10, top="-", net="wifi:5,cell:0", cap=None):
    zone_text = ",".join(f"{name}={value}" for name, value in zones.items())
    fields = (ts, app, 0 if app == "screen_off" else 1, charging, current, 350, cpu, kernel, gpu, top, net, "p0:1800", zone_text)
    return "\t".join(map(str, fields + ((cap,) if cap else ()))) + "\n"


class SamplerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.phone = FakePhone(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def lines(self):
        files = sorted((self.phone.data / "data").glob("*.tsv"))
        self.assertEqual(len(files), 1)
        return [line.split("\t") for line in files[0].read_text().splitlines()]

    def test_sample_records_every_sensor_and_what_the_phone_does(self):
        self.phone.run("sampler.sh", "--once")
        self.phone.set_cpu(1)
        self.phone.set_net(20 * 1024 * 300, 0)
        net_prev = self.phone.data / "run/net.prev"
        net_prev.write_text(f"{int(time.time()) - 20} 0 0\n")
        self.phone.run("sampler.sh", "--once")
        first, second = self.lines()
        self.assertEqual(len(second), 14)
        ts, app, screen, charging, current, battery, cpu, kernel, gpu, top, net, freqs, zones, cap = second
        self.assertEqual(cap, "-")                            # Cogan Smart · Power is not running here
        self.assertEqual(first[6:8], ["-1", "-1"])           # no previous CPU reading yet
        self.assertEqual((app, screen, charging, current, battery, gpu), ("com.mobile.legends", "1", "1", "2100", "361", "65"))
        self.assertEqual(cpu, "400")                          # 400 of 1000 ticks busy = 40.0 %
        self.assertEqual(kernel, "80")                        # kworker (child of kthreadd) = 8.0 %
        self.assertEqual(top.split(";")[0], "com.mobile.legends:250")
        self.assertIn("com.google.android.gms:30", top)       # ":persistent" is dropped from the name
        wifi, cell = net.split(",")                           # 6000 KB over 20 s, or 21 s on a busy runner
        self.assertIn(wifi, ("wifi:300", "wifi:285"))
        self.assertEqual(cell, "cell:0")
        self.assertEqual(freqs, "p0:1800,p4:2850,p7:3250")
        self.assertIn("soc_max=550", zones)
        self.assertIn("battery=360", zones)
        self.assertNotIn("unused_sensor", zones)
        self.assertNotIn("broken", zones)
        self.assertNotIn("hyperos_board", zones)

    def test_hyperos_board_temperature_is_logged_as_phone_body(self):
        # Owner 2026-10-24: HyperOS's board_sensor_temp (40613) next to quiet_therm, in the same log.
        write(self.phone.sys / "class/thermal/thermal_message/board_sensor_temp", "40613\n")
        self.phone.run("sampler.sh", "--once")
        zones = self.lines()[0][12]
        self.assertIn("hyperos_board=406", zones)
        now = json.loads(self.phone.report("now"))
        board = [zone for zone in now["zones"] if zone["name"] == "hyperos_board"]
        self.assertEqual((board[0]["t"], board[0]["id"]), (406, "skin"))
        self.assertEqual((now["body"], now["body_from"]), (406, "skin"))

    def test_sample_records_the_power_cap(self):
        # v2.9.1 (owner 2026-10-24): every sample shows the CPU cap of Cogan Smart · Power, "-" when it is off.
        self.phone.run("sampler.sh", "--once")
        state = '{"ts":%d,"mode":"seimbang","main":650,"body":415,"limit":41,"brake":0,"busy":1,"level":2,"big":80,' \
                '"little":100,"battery":{"level":50,"status":"discharging","temp":380,"current":-900},"charge_off":""}\n'
        write(self.phone.power / "run/state.json", state % int(time.time()))
        self.phone.run("sampler.sh", "--once")
        write(self.phone.power / "run/state.json", state % (int(time.time()) - 300))   # stopped 5 minutes ago
        self.phone.run("sampler.sh", "--once")
        self.assertEqual([line[13] for line in self.lines()], ["-", "80/100/2", "-"])

    def test_latest_report_for_other_modules(self):
        self.phone.run("sampler.sh", "--once")
        ts, main, battery, charging, app, cause = (self.phone.data / "run/latest").read_text().rstrip("\n").split("\t")
        self.assertLessEqual(abs(int(ts) - time.time()), 5)
        self.assertEqual((main, battery, charging, app), ("550", "361", "1", "Mobile Legends"))
        self.assertEqual(cause, "Cas cepat")                   # charging at 2100 mA comes first

    def test_heat_notification_only_when_enabled_and_hot(self):
        self.phone.run("sampler.sh", "--once")
        self.assertFalse((self.phone.base / "notifications").exists())
        # v2.9: the phone body (39 °C here), not the processor (55 °C), decides.
        self.assertEqual(json.loads(self.phone.report("set", "NOTIFY", "1", "NOTIFY_TEMP", "40")), {"ok": 1})
        self.phone.run("sampler.sh", "--once")
        self.assertFalse((self.phone.base / "notifications").exists())
        self.assertEqual(json.loads(self.phone.report("set", "NOTIFY_TEMP", "39")), {"ok": 1})
        self.phone.run("sampler.sh", "--once")
        notes = (self.phone.base / "notifications").read_text()
        self.assertIn("Badan HP 39 °C", notes)
        self.assertIn("Mobile Legends", notes)
        self.phone.run("sampler.sh", "--once")               # at most once every 10 minutes
        self.assertEqual(len((self.phone.base / "notifications").read_text().splitlines()), 1)

    def test_start_and_stop(self):
        self.phone.report("set", "INTERVAL", "10")
        status = json.loads(self.phone.report("start"))
        try:
            self.assertEqual(status["running"], 1)
            self.assertGreater(status["pid"], 0)
            self.assertEqual(json.loads(self.phone.report("start"))["pid"], status["pid"])   # no second copy
            deadline = time.time() + 10
            while time.time() < deadline and not list((self.phone.data / "data").glob("*.tsv")):
                time.sleep(0.2)
            self.assertTrue(list((self.phone.data / "data").glob("*.tsv")))
            self.assertIn("6.1.177-Cogan-r3", (self.phone.data / "kernels.tsv").read_text())
        finally:
            stopped = json.loads(self.phone.report("stop"))
        self.assertEqual(stopped["running"], 0)


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.phone = FakePhone(Path(self.tmp.name))
        now = int(time.time())
        start = now - 140 * 20
        (self.phone.data / "data").mkdir(parents=True)
        write(self.phone.data / "kernels.tsv", f"{start - 100}\t6.1.138-android14-11\n{start + 70 * 20}\t6.1.177-Cogan-r3\n")
        lines = []
        for i in range(140):
            ts = start + i * 20
            # "Hot" is the phone body (shell_back) at or above 41 °C (v2.9.0).
            if i < 60:     # Mobile Legends: GPU heavy and hot
                lines.append(sample(ts, "com.mobile.legends", {"soc_max": 470 + i % 30, "gpu1": 460, "battery": 370,
                                    "shell_back": 430 + i % 5}, cpu=280, gpu=70, top="com.mobile.legends:250"))
            elif i < 90:   # Instagram while Play services work in the background
                lines.append(sample(ts, "com.instagram.android", {"soc_max": 430, "battery": 360, "shell_back": 425},
                                    cpu=200, top="com.google.android.gms:150;com.instagram.android:40"))
            elif i < 120:  # screen off, cool
                lines.append(sample(ts, "screen_off", {"soc_max": 350, "battery": 330, "shell_back": 360}, cpu=30))
            else:          # fast charging on the home screen (the newest 20 samples)
                lines.append(sample(ts, "com.miui.home", {"soc_max": 440, "battery": 400, "shell_back": 425},
                                    charging=1, current=2500))
        # Older samples and a sample from the future are ignored.
        lines.insert(0, sample(start - 9 * 86400, "com.mobile.legends", {"soc_max": 990}))
        lines.insert(1, sample(now + 3600, "com.mobile.legends", {"soc_max": 990}))
        day = time.strftime("%Y-%m-%d", time.gmtime(now + 7 * 3600))
        write(self.phone.data / "data" / f"{day}.tsv", "".join(lines))
        self.now = now

    def tearDown(self):
        self.tmp.cleanup()

    def test_summary_names_the_causes(self):
        summary = json.loads(self.phone.report("summary", "86400"))
        self.assertEqual(summary["samples"], 140)
        self.assertEqual(summary["peak"]["t"], 499)
        self.assertEqual(summary["peak"]["app"], "Mobile Legends")
        causes = {cause["name"]: cause["pct"] for cause in summary["causes"]}
        self.assertEqual(summary["causes"][0]["name"], "Grafis berat: Mobile Legends")
        self.assertIn("Latar belakang: com.google.android.gms", causes)
        self.assertIn("Cas cepat", causes)
        self.assertLessEqual(abs(sum(causes.values()) - 100), 1)          # rounded per cause
        kinds = {cause["kind"]: cause["tip"] for cause in summary["causes"]}
        self.assertEqual(kinds["gpu"], "Turunkan grafis atau FPS di game itu.")
        self.assertIn("HyperCharge", kinds["fast"])
        self.assertIn("➜ Saran: Turunkan grafis atau FPS di game itu.", summary["text"])
        apps = {app["pkg"]: app for app in summary["apps"]}
        self.assertEqual(apps["com.mobile.legends"]["name"], "Mobile Legends")
        self.assertEqual(apps["screen_off"]["name"], "Layar mati")
        kernels = {kernel["name"]: kernel["pct"] for kernel in summary["kernels"]}
        self.assertEqual(kernels, {"6.1.138-android14-11": 50, "6.1.177-Cogan-r3": 50})
        self.assertLessEqual(len(summary["series"]), 120)
        self.assertIn("Kesimpulan: paling sering panas karena Grafis berat: Mobile Legends", summary["text"])
        groups = {group["name"]: group for group in summary["groups"]}
        self.assertLessEqual({"Prosesor", "GPU", "Baterai"}, set(groups))
        self.assertEqual((groups["GPU"]["avg"], groups["GPU"]["peak"]), (460, 460))   # only samples with a GPU zone
        self.assertEqual((groups["Badan HP"]["id"], groups["Prosesor"]["id"]), ("skin", "cpu"))
        # Per app, kernel and mode: the phone body; the peak tile stays the processor.
        self.assertEqual((apps["com.mobile.legends"]["avg"], apps["com.mobile.legends"]["peak"]), (432, 434))
        self.assertIn("Penyebab panas (Badan HP ≥ 41.0 °C)", summary["text"])
        self.assertEqual(max(value for _, value in summary["series"]), 434)

    def test_a_hot_processor_alone_is_not_hot(self):
        now = int(time.time())
        lines = [sample(now - 600 + i * 20, "com.android.chrome", {"soc_max": 650, "battery": 380, "shell_back": 395}, cpu=300)
                 for i in range(10)]
        # Without a phone body sensor the battery stands in for it.
        lines += [sample(now - 300 + i * 20, "com.android.chrome", {"soc_max": 650, "battery": 425}, cpu=300) for i in range(5)]
        for old in (self.phone.data / "data").glob("*.tsv"):
            old.unlink()
        write(self.phone.data / "data" / time.strftime("%Y-%m-%d.tsv", time.gmtime(now + 7 * 3600)), "".join(lines))
        summary = json.loads(self.phone.report("summary", "3600"))
        self.assertEqual((summary["samples"], summary["hot_pct"], summary["peak"]["t"]), (15, 33, 650))
        self.assertEqual([cause["name"] for cause in summary["causes"]], ["Aplikasi berat: Chrome"])

    def test_causes_per_part_of_the_phone(self):
        # Owner's log 2026-10-24: YouTube over 5G warmed the phone; the modem was the hottest part.
        now = int(time.time())
        lines = [sample(now - 900 + i * 20, "com.google.android.youtube", {"soc_max": 530, "battery": 400, "shell_back": 420},
                        cpu=120, net="wifi:0,cell:400") for i in range(20)]
        # Then Wi-Fi, still warm: screen and ordinary use.
        lines += [sample(now - 450 + i * 20, "com.google.android.youtube", {"soc_max": 500, "battery": 405, "shell_back": 415},
                         cpu=120) for i in range(20)]
        for old in (self.phone.data / "data").glob("*.tsv"):
            old.unlink()
        write(self.phone.data / "data" / time.strftime("%Y-%m-%d.tsv", time.gmtime(now + 7 * 3600)), "".join(lines))
        summary = json.loads(self.phone.report("summary", "3600"))
        causes = {cause["name"]: cause for cause in summary["causes"]}
        self.assertEqual(set(causes), {"Modem (data seluler): YouTube", "Layar & pemakaian: YouTube"})
        self.assertEqual(causes["Modem (data seluler): YouTube"]["kind"], "modem")
        self.assertIn("Wi-Fi", causes["Modem (data seluler): YouTube"]["tip"])
        self.assertIn("kecerahan", causes["Layar & pemakaian: YouTube"]["tip"])
        english = json.loads(self.phone.report("--lang", "en", "summary", "3600"))
        self.assertIn("Modem (cellular data): YouTube", [cause["name"] for cause in english["causes"]])

    def test_summary_per_power_mode(self):
        start = self.now - 140 * 20
        write(self.phone.data / "modes.tsv", f"{start + 30 * 20}\tgame\n{start + 90 * 20}\tseimbang\n")
        summary = json.loads(self.phone.report("summary", "86400"))
        modes = {mode["mode"]: mode for mode in summary["modes"]}
        self.assertEqual({key: modes[key]["pct"] for key in modes}, {"none": 21, "game": 43, "seimbang": 36})
        self.assertEqual(modes["game"]["name"], "Performa")
        self.assertEqual(modes["game"]["hot_pct"], 100)
        self.assertEqual(modes["seimbang"]["hot_pct"], 40)      # 20 of 50: the fast-charging samples
        self.assertIn("Per mode", summary["text"])
        self.assertIn("Kontrol daya mati", summary["text"])
        self.assertEqual(json.loads(self.phone.report("now"))["mode"], "Kernel Default")
        self.phone.report("clear")
        self.assertEqual((self.phone.data / "modes.tsv").read_text().split("\t")[1], "seimbang\n")

    def test_summary_shows_how_much_the_cpu_was_lowered(self):
        now = int(time.time())
        zones = {"soc_max": 600, "battery": 380, "shell_back": 405}
        caps = ["100/100/0"] * 10 + ["80/100/2"] * 4 + ["70/100/3"] + ["60/80/0"] * 5
        lines = [sample(now - 600 + i * 20, "com.android.chrome", zones, cap=cap) for i, cap in enumerate(caps)]
        lines += [sample(now - 100 + i * 20, "com.android.chrome", zones) for i in range(3)]   # older module: no cap
        for old in (self.phone.data / "data").glob("*.tsv"):
            old.unlink()
        write(self.phone.data / "data" / time.strftime("%Y-%m-%d.tsv", time.gmtime(now + 7 * 3600)), "".join(lines))
        summary = json.loads(self.phone.report("summary", "3600"))
        self.assertEqual(summary["cap"], {"samples": 20, "heat_pct": 25, "mode_pct": 25, "min_big": 70, "min_little": 100})
        self.assertIn("CPU diturunkan karena panas: 25% waktu (terendah CPU besar 70%, kecil 100%) · batas mode Hemat 25% waktu",
                      summary["text"])
        detail = self.phone.report("detail", "3600")
        self.assertEqual(detail.count("| batas CPU "), 10)
        self.assertIn("| batas CPU 80/100% |", detail)
        table = list(csv.DictReader(self.phone.report("csv", "3600").splitlines()))
        self.assertEqual([row["batas_cpu"] for row in table].count("80/100"), 4)
        self.assertEqual(table[-1]["batas_cpu"], "")

    def test_a_stuck_sensor_is_left_out(self):
        # Owner's log 2026-10-24: the charger IC read 50.0 °C for an hour while the processor went up and down.
        now = int(time.time())
        lines = [sample(now - 1200 + i * 20, "com.android.chrome",
                        {"soc_max": 450 + (i % 6) * 60, "battery": 370, "shell_back": 390, "charger1_therm": 420 + i % 3,
                         "mtk-master-charger": 500}) for i in range(50)]
        for old in (self.phone.data / "data").glob("*.tsv"):
            old.unlink()
        write(self.phone.data / "data" / time.strftime("%Y-%m-%d.tsv", time.gmtime(now + 7 * 3600)), "".join(lines))
        summary = json.loads(self.phone.report("summary", "3600"))
        self.assertEqual(summary["stuck"], "mtk-master-charger")    # battery and shell_back stay: never left out
        charger = {group["id"]: group for group in summary["groups"]}["chg"]
        self.assertEqual(charger["peak"], 500)            # counted until it proved stuck (30 samples)
        self.assertLess(charger["avg"], 470)
        self.assertIn("Sensor macet, tidak dihitung: mtk-master-charger", summary["text"])
        # A sensor that only stays still while the phone rests is not stuck.
        calm = [sample(now - 1200 + i * 20, "screen_off", {"soc_max": 450, "battery": 300}) for i in range(50)]
        write(self.phone.data / "data" / time.strftime("%Y-%m-%d.tsv", time.gmtime(now + 7 * 3600)), "".join(calm))
        self.assertEqual(json.loads(self.phone.report("summary", "3600"))["stuck"], "")

    def test_the_phone_body_is_hyperos_own_number(self):
        # Owner 2026-10-24, "suhu masih inkonsistensi": one Badan HP everywhere, the number HyperOS uses.
        now = int(time.time())
        lines = [sample(now - 600 + i * 20, "com.android.chrome", {"soc_max": 550, "battery": 380, "shell_back": 418,
                                                                     "hyperos_board": 406}) for i in range(10)]
        for old in (self.phone.data / "data").glob("*.tsv"):
            old.unlink()
        write(self.phone.data / "data" / time.strftime("%Y-%m-%d.tsv", time.gmtime(now + 7 * 3600)), "".join(lines))
        summary = json.loads(self.phone.report("summary", "3600"))
        body = {group["id"]: group for group in summary["groups"]}["skin"]
        self.assertEqual((body["avg"], body["peak"], summary["hot_pct"]), (406, 406, 0))   # 41.8 elsewhere would be hot
        write(self.phone.sys / "class/thermal/thermal_message/board_sensor_temp", "37400\n")
        live = json.loads(self.phone.report("now"))
        self.assertEqual((live["body"], {g["id"]: g["t"] for g in live["groups"]}["skin"]), (374, 374))   # shell_back is 39.0

    def test_live_tiles_skip_a_stuck_sensor(self):
        write(self.phone.sys / "class/thermal/thermal_zone20/type", "mtk-master-charger\n")
        write(self.phone.sys / "class/thermal/thermal_zone20/temp", "50000\n")
        write(self.phone.data / "run/stuck", "mtk-master-charger\n")
        now = json.loads(self.phone.report("now"))
        self.assertNotIn("chg", [group["id"] for group in now["groups"]])
        zone = [zone for zone in now["zones"] if zone["name"] == "mtk-master-charger"][0]
        self.assertEqual((zone["t"], zone["stuck"]), (500, 1))

    def test_app_names_from_the_root_manager(self):
        # A spoofed manager has a random package name (owner 2026-10-24: weonse.bxmfmy.qeomje).
        now = int(time.time())
        lines = [sample(now - 600 + i * 20, "weonse.bxmfmy.qeomje", {"soc_max": 500, "battery": 380, "shell_back": 415},
                        top="com.anthropic.claude:150;com.mobile.legends:20") for i in range(10)]
        for old in (self.phone.data / "data").glob("*.tsv"):
            old.unlink()
        write(self.phone.data / "data" / time.strftime("%Y-%m-%d.tsv", time.gmtime(now + 7 * 3600)), "".join(lines))
        self.assertEqual(sorted(json.loads(self.phone.report("pkgs"))), ["com.anthropic.claude", "weonse.bxmfmy.qeomje"])
        hexed = lambda text: text.encode().hex()
        answer = json.loads(self.phone.report("labels", "weonse.bxmfmy.qeomje", hexed("KernelSU Next"),
                                              "com.anthropic.claude", hexed("Claude, \"AI\" ✨"),
                                              "bad..name", hexed("Nope"), "com.example.ctrl", hexed("Line\nBreak"),
                                              "com.example.long", hexed("x" * 61)))
        self.assertEqual(answer, {"ok": 1, "labels": 2})
        self.assertEqual(self.phone.report("pkgs").strip(), "[]")
        summary = json.loads(self.phone.report("summary", "3600"))
        self.assertEqual(summary["apps"][0]["name"], "KernelSU Next")
        self.assertIn("Latar belakang: Claude, \"AI\" ✨", [cause["name"] for cause in summary["causes"]])
        table = list(csv.DictReader(self.phone.report("csv", "3600").splitlines()))
        self.assertEqual((table[0]["aplikasi"], table[0]["proses_teratas"]), ("KernelSU Next", 'Claude, "AI" ✨ 15.0%; Mobile Legends 2.0%'))
        # A newer name replaces the old one; other names stay.
        self.phone.report("labels", "weonse.bxmfmy.qeomje", hexed("BakaSU"))
        self.assertEqual(json.loads(self.phone.report("summary", "3600"))["apps"][0]["name"], "BakaSU")

    def test_short_range_only_sees_recent_samples(self):
        summary = json.loads(self.phone.report("summary", "300"))
        self.assertLessEqual(summary["samples"], 16)
        self.assertEqual([cause["name"] for cause in summary["causes"]], ["Cas cepat"])

    def test_text_csv_and_now(self):
        text = self.phone.report("text", "86400")
        self.assertIn("ringkasan 1 hari", text)
        self.assertIn("Suhu tertinggi: 49.9 °C (Prosesor)", text)
        self.assertIn("Per kernel", text)
        rows = self.phone.report("csv", "86400").splitlines()
        self.assertEqual(len(rows), 141)
        self.assertTrue(rows[0].startswith("waktu,aplikasi,layar,cas"))
        self.assertIn(',"Mobile Legends",nyala,tidak,', rows[1])
        table = list(csv.reader(rows))
        self.assertEqual({len(row) for row in table}, {len(table[0])})
        first = dict(zip(table[0], table[1]))
        self.assertEqual((first["proses_teratas"], first["wifi_kBps"], first["seluler_kBps"]), ("Mobile Legends 25.0%", "5", "0"))
        now = json.loads(self.phone.report("now"))
        self.assertEqual(now["main"], 550)                     # read from the sensors just now
        self.assertEqual((now["app"], now["charging"], now["release"]), ("Layar utama (launcher)", 1, "6.1.177-Cogan-r3"))
        self.assertEqual(now["running"], 0)
        self.assertIn({"name": "soc_max", "group": "Prosesor", "id": "cpu", "t": 550, "stuck": 0}, now["zones"])
        self.assertEqual((now["body"], now["body_from"]), (390, "skin"))   # the warmer of shell_back and board_ntc
        self.assertIn({"name": "Badan HP", "id": "skin", "t": 390}, now["groups"])

    def test_save_writes_txt_and_csv(self):
        saved = json.loads(self.phone.report("save", "3600"))
        self.assertEqual(saved["ok"], 1)
        self.assertEqual(saved["dir"], str(self.phone.out))
        self.assertTrue(saved["txt"].endswith("_1jam.txt"))
        txt = Path(saved["txt"]).read_text()
        self.assertIn("Cogan Smart · Thermal — ringkasan 1 jam", txt)
        self.assertIn("Detail per sampel:", txt)
        self.assertIn("teratas: com.google.android.gms 15.0%; Instagram 4.0%", txt)
        self.assertIn("kernel 6.1.177-Cogan-r3", txt)
        csv_rows = Path(saved["csv"]).read_text().splitlines()
        self.assertEqual(len(csv_rows) - 1, saved["samples"])
        self.assertGreater(saved["samples"], 100)
        self.assertTrue(json.loads(self.phone.report("save", "90"))["txt"].endswith("_1menit.txt"))

    def test_empty_history(self):
        self.assertEqual(json.loads(self.phone.report("clear")), {"ok": 1})
        summary = json.loads(self.phone.report("summary", "3600"))
        self.assertEqual(summary["samples"], 0)
        self.assertIn("Belum ada data", summary["text"])
        self.assertEqual(json.loads(self.phone.report("now"))["age"], -1)
        self.assertEqual(json.loads(self.phone.report("now"))["mode"], "")
        self.assertEqual(json.loads(self.phone.report("status"))["days"], 0)

    def test_settings_are_validated(self):
        self.assertEqual(json.loads(self.phone.report("set", "HOT_TEMP", "40", "INTERVAL", "30")), {"ok": 1})
        status = json.loads(self.phone.report("status"))
        self.assertEqual((status["hot"], status["interval"], status["retention"], status["notify"]), (40, 30, 7, 0))
        for args in (("INTERVAL", "5"), ("HOT_TEMP", "1;reboot"), ("FOO", "1"), ("NOTIFY", "2")):
            result = json.loads(self.phone.report("set", *args))
            self.assertEqual(result["ok"], 0, args)
        self.assertEqual(json.loads(self.phone.report("status"))["interval"], 30)
        config = (self.phone.data / "config").read_text()
        self.assertNotIn("reboot", config)
        self.assertNotIn("FOO", config)


class PackageTests(unittest.TestCase):
    def test_module_files(self):
        prop = dict(line.split("=", 1) for line in (MODULE / "module.prop").read_text().splitlines() if "=" in line)
        self.assertEqual(prop["id"], "cogan_smart")
        self.assertRegex(prop["versionCode"], r"^\d+$")
        for name in ("service.sh", "action.sh", "uninstall.sh", "customize.sh", "bridge.sh",
                     "thermal/service.sh", "thermal/sampler.sh", "thermal/report.sh", "thermal/uninstall.sh",
                     "thermal/common.sh", "thermal/cpu.awk", "thermal/thermal.awk", "thermal/report.awk",
                     "webroot/thermal.html", "webroot/client.js",
                     "META-INF/com/google/android/update-binary", "META-INF/com/google/android/updater-script"):
            self.assertTrue((MODULE / name).is_file(), name)
        html = (MODULE / "webroot/thermal.html").read_text()
        self.assertIn("/data/adb/modules/cogan_smart/thermal/report.sh", html)

    def test_zip(self):
        with tempfile.TemporaryDirectory() as out:
            result = subprocess.run([sys.executable, str(ROOT / "scripts/package_module.py"), str(MODULE), out],
                                    capture_output=True, text=True, check=True)
            target = Path(result.stdout.strip())
            version = next(l.split("=", 1)[1] for l in (MODULE / "module.prop").read_text().splitlines() if l.startswith("version="))
            self.assertEqual(target.name, f"Cogan-Smart-Kernel-{version}.zip")
            with zipfile.ZipFile(target) as archive:
                modes = {info.filename: (info.external_attr >> 16) & 0o777 for info in archive.infolist()}
        self.assertEqual(modes["module.prop"], 0o644)
        self.assertEqual(modes["service.sh"], 0o755)
        self.assertEqual(modes["META-INF/com/google/android/update-binary"], 0o755)
        self.assertEqual(modes["thermal/sampler.sh"], 0o755)
        self.assertIn("webroot/thermal.html", modes)
        self.assertNotIn("README.md", modes)
        # Released ZIPs kept in rilis/ never end up inside a new ZIP.
        self.assertTrue((MODULE / "rilis").is_dir())
        self.assertFalse([name for name in modes if name.startswith("rilis/")])


if __name__ == "__main__":
    unittest.main()
