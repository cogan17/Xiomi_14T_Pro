#!/usr/bin/env python3
"""Offline tests for the power part of Cogan Smart Kernel against a fake /sys.

Like tests/test_thermal_monitor.py it prefers mksh and one-true-awk (Android's shell and awk) when
installed; THERMAL_SH / THERMAL_AWK pick others. A small thread plays the charger: while the switch
under test is off the battery reports "Not charging". A fake `sleep` does the same at once, which
keeps the tests fast where `sleep` is not a shell builtin.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "modules/cogan-smart"
SHELL = os.environ.get("THERMAL_SH") or shutil.which("mksh") or shutil.which("dash") or "/bin/sh"
AWK = os.environ.get("THERMAL_AWK") or shutil.which("original-awk") or shutil.which("awk")
POLICIES = {   # name: (min, max, available steps)
    "policy0": (500000, 2000000, "500000 1000000 1500000 2000000"),
    "policy4": (1000000, 3000000, "1000000 1500000 2000000 2400000 2700000 3000000"),
    "policy7": (1200000, 3250000, "1200000 2000000 2500000 2900000 3250000"),
}


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


class FakePhone:
    def __init__(self, base, charger_switch=None):
        self.base = base
        self.sys = base / "sys"
        self.data = base / "power"
        self.monitor = base / "thermal"
        self.cpuctl = base / "cpuctl"
        self.bin = base / "bin"
        self.root = base / "smart"
        shutil.copytree(MODULE, self.root)
        self.mod = self.root / "power"
        self.bin.mkdir()
        self.set_temp(40.0)
        battery = self.sys / "class/power_supply/battery"
        self.battery = battery
        self.set_battery(50, "Charging", 30.0, -1000000)
        write(battery / "input_suspend", "0\n")
        write(battery / "battery_charging_enabled", "1\n")
        for name, (low, high, steps) in POLICIES.items():
            policy = self.sys / f"devices/system/cpu/cpufreq/{name}"
            write(policy / "cpuinfo_min_freq", f"{low}\n")
            write(policy / "cpuinfo_max_freq", f"{high}\n")
            write(policy / "scaling_max_freq", f"{high}\n")
            write(policy / "scaling_cur_freq", f"{low}\n")
            write(policy / "scaling_available_frequencies", steps + "\n")
        write(self.cpuctl / "top-app/cpu.uclamp.min", "0.00\n")
        (self.monitor / "run").mkdir(parents=True)
        # The charger: while the switch under test is off, the battery stops charging.
        tools = {"getprop": "echo 1"}
        self.charger = None
        if charger_switch:
            node, off = charger_switch
            status = battery / "status"
            tools["sleep"] = (f"if [ \"$(cat {battery / node})\" = {off} ]; then s='Not charging'; else s=Charging; fi\n"
                              f"echo \"$s\" > {status}.sleep && mv {status}.sleep {status}\nexec /bin/sleep 0")
            self.charger = threading.Event()

            def plugged_in():
                while not self.charger.is_set():
                    want = "Not charging" if (battery / node).read_text().strip() == off else "Charging"
                    if status.read_text().strip() not in (want, ""):
                        (battery / "status.thread").write_text(want + "\n")
                        os.replace(battery / "status.thread", status)
                    time.sleep(0.02)
            threading.Thread(target=plugged_in, daemon=True).start()
        for name, body in tools.items():
            write(self.bin / name, "#!/bin/sh\n" + body + "\n")
            (self.bin / name).chmod(0o755)
        os.symlink(SHELL, self.bin / "sh")
        os.symlink(AWK, self.bin / "awk")
        self.env = dict(os.environ, PATH=f"{self.bin}:{os.environ['PATH']}", CP_DATA=str(self.data), CP_SYS=str(self.sys),
                        CP_PROC=str(base / "proc"), CP_CPUCTL=str(self.cpuctl), CT_DATA=str(self.monitor),
                        CT_MOD=str(base / "modules/cogan_thermal"))

    def set_temp(self, celsius):
        for index, (kind, value) in enumerate((("soc_max", celsius), ("gpu1", celsius - 3), ("battery", 30.0))):
            write(self.sys / f"class/thermal/thermal_zone{index}/type", kind + "\n")
            write(self.sys / f"class/thermal/thermal_zone{index}/temp", f"{int(value * 1000)}\n")

    def set_body(self, celsius):
        """The phone body (skin) sensor that the modes follow since v2.9."""
        write(self.sys / "class/thermal/thermal_zone3/type", "shell_back\n")
        write(self.sys / "class/thermal/thermal_zone3/temp", f"{int(celsius * 1000)}\n")

    def unplug(self):
        if self.charger:
            self.charger.set()
            time.sleep(0.1)

    def set_battery(self, level, status, celsius, current_ua=-1000000):
        write(self.battery / "capacity", f"{level}\n")
        (self.battery / "status.new").write_text(status + "\n")
        os.replace(self.battery / "status.new", self.battery / "status")
        write(self.battery / "temp", f"{int(celsius * 10)}\n")
        write(self.battery / "current_now", f"{current_ua}\n")

    def start_recorder(self):
        """Since v2.8 a report counts only from an installed recorder whose sampler is alive."""
        mod = Path(self.env["CT_MOD"])
        write(mod / "module.prop", "id=cogan_thermal\n")
        write(mod / "thermal/sampler.sh", "while :; do /bin/sleep 1; done\n")
        self.recorder = subprocess.Popen(["/bin/sh", str(mod / "thermal/sampler.sh")])
        write(self.monitor / "run/sampler.pid", f"{self.recorder.pid}\n")
        write(self.monitor / "run/started", f"{int(time.time()) - 1000}\n")

    def close(self):
        if getattr(self, "recorder", None):
            self.recorder.kill()
            self.recorder.wait()
        self.unplug()

    def monitor_report(self, cause, app="Mobile Legends", age=0):
        write(self.monitor / "run/latest", f"{int(time.time()) - age}\t450\t300\t1\t{app}\t{cause}\n")
        write(self.monitor / "run/last", f"{int(time.time()) - age}\n")

    def caps(self):
        return {name: int((self.sys / f"devices/system/cpu/cpufreq/{name}/scaling_max_freq").read_text())
                for name in POLICIES}

    def node(self, name):
        return (self.battery / name).read_text().strip()

    def run(self, script, *args):
        result = subprocess.run([str(self.bin / "sh"), str(self.mod / script), *args], env=self.env,
                                capture_output=True, text=True, timeout=60)
        if result.returncode:
            raise AssertionError(f"{script} {args}: {result.returncode}\n{result.stdout}\n{result.stderr}")
        return result.stdout

    def step(self):
        self.run("controller.sh", "--once")
        return json.loads((self.data / "run/state.json").read_text())

    def report(self, *args):
        return json.loads(self.run("report.sh", *args))

    def events(self):
        return [event["text"] for event in self.report("events", "50")]


class PowerModeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.phone = FakePhone(Path(self.tmp.name))
        # Retained v1.0 settings: upgrade must keep the previous 80/75 policy.
        self.phone.report("set", "CHARGE_STOP", "80", "CHARGE_RESUME", "75")

    def tearDown(self):
        self.phone.close()
        self.tmp.cleanup()

    def save_switch(self):
        write(self.phone.data / "switch", "class/power_supply/battery/input_suspend|0|1\n")

    def test_a_hot_processor_alone_does_not_cap_the_cpu(self):
        # v2.8 compared the processor (about 50 °C at rest on rothko) with 42 °C and capped the CPU
        # almost all the time. Since v2.9 the modes follow the phone body (owner 2026-10-24).
        self.phone.set_temp(60.0)
        self.phone.set_body(38.0)
        for _ in range(3):
            state = self.phone.step()
        self.assertEqual((state["level"], state["big"], state["main"], state["body"]), (0, 100, 600, 380))
        self.assertEqual(self.phone.caps(), {"policy0": 2000000, "policy4": 3000000, "policy7": 3250000})

    def test_balanced_steps_the_cpu_down_and_back_up(self):
        self.phone.set_temp(65.0)                                         # the processor works
        self.phone.set_body(41.5)
        state = self.phone.step()
        self.assertEqual((state["mode"], state["limit"], state["level"], state["big"]), ("seimbang", 41, 1, 90))
        self.assertEqual(self.phone.caps(), {"policy0": 2000000, "policy4": 2700000, "policy7": 2900000})
        # The body cools slowly: three checks to see what the step did, then the next step.
        self.assertEqual([self.phone.step()["big"] for _ in range(3)], [90, 90, 80])
        self.assertEqual(self.phone.caps()["policy4"], 2400000)
        for _ in range(2):
            self.phone.step()
        self.phone.set_body(41.1)                                         # cooling already: no step
        self.assertEqual(self.phone.step()["level"], 2)
        self.phone.set_body(40.5)                                         # just under the limit: gentle steps only
        self.assertEqual(self.phone.step()["level"], 2)
        self.phone.set_body(39.9)                                         # not yet 1.5 °C under: hold
        self.assertEqual(self.phone.step()["level"], 2)
        self.phone.set_body(39.4)
        self.assertEqual([self.phone.step()["level"] for _ in range(3)], [2, 2, 1])   # three cool checks
        self.assertEqual(self.phone.caps()["policy4"], 2700000)
        events = self.phone.events()
        self.assertIn("Badan HP turun ke 39.4 °C: CPU besar 90%, kecil 100%", events[0])
        self.assertTrue(any("Badan HP 41.5 °C (batas 41 °C): CPU besar 90%, kecil 100%" in event for event in events))

    def test_smooth_steps_big_cores_first_little_cores_last(self):
        # Owner 2026-10-24, "as smooth as possible": from 1 °C under the limit only two gentle steps.
        self.phone.set_temp(65.0)
        self.phone.set_body(40.2)
        levels = [self.phone.step()["level"] for _ in range(12)]
        self.assertEqual(max(levels), 2)
        # At the limit: the big cores go down to 60 %, then the little cores to 90 % and 80 %.
        self.phone.set_body(43.0)
        caps = []
        for _ in range(20):
            state = self.phone.step()
            caps.append((state["big"], state["little"]))
        self.assertEqual(sorted(set(caps), reverse=True), [(70, 100), (60, 100), (60, 90), (60, 80)])
        self.assertEqual(caps[-1], (60, 80))
        self.assertEqual(self.phone.caps(), {"policy0": 1500000, "policy4": 1500000, "policy7": 1200000})

    def test_an_idle_processor_is_not_lowered(self):
        # Heat from charging, the room or an idle phone: a lower CPU cap does not cool it, and a cap kept
        # from then would only slow the next use (owner 2026-10-24).
        self.phone.set_body(43.5)
        self.phone.set_temp(52.0)
        self.assertEqual([self.phone.step()["level"] for _ in range(6)], [0] * 6)
        self.phone.set_temp(66.0)                                         # the processor works: steps
        self.assertEqual([self.phone.step()["level"] for _ in range(5)], [1, 1, 1, 2, 2])
        self.phone.set_temp(55.0)                                         # idle again: speed comes back
        levels = [self.phone.step()["level"] for _ in range(6)]
        self.assertEqual(levels, [2, 2, 1, 1, 1, 0])
        state = self.phone.step()
        self.assertEqual((state["busy"], state["big"], state["little"]), (0, 100, 100))

    def test_processor_brake_in_every_mode(self):
        self.phone.set_body(36.0)
        for mode in ("game", "seimbang", "hemat"):
            self.phone.report("mode", mode)
            self.phone.set_temp(50.0)
            start = self.phone.step()["big"]
            self.phone.set_temp(95.5)
            levels = [self.phone.step()["level"] for _ in range(2)]   # every check, no waiting
            self.assertEqual(levels, [1, 2], mode)
            state = self.phone.step()
            self.assertEqual((state["brake"], state["big"]), (1, start - 30), mode)
            self.assertIn("Rem darurat: prosesor 95.5 °C ≥ 95 °C: CPU besar", self.phone.events()[0])
            self.phone.set_temp(91.0)                                     # not yet 5 °C under the brake
            self.assertEqual(self.phone.step()["level"], 3)
        self.phone.set_temp(70.0)
        self.assertEqual([self.phone.step()["level"] for _ in range(3)], [3, 3, 2])

    def test_without_a_body_sensor_the_battery_is_used(self):
        self.phone.set_temp(60.0)
        self.phone.set_battery(50, "Discharging", 43.0)
        state = self.phone.step()
        self.assertEqual((state["body"], state["level"]), (430, 1))
        status = self.phone.report("status")
        self.assertEqual((status["body"], status["body_from"], status["brake"]), (430, "battery", 95))
        self.phone.set_body(39.0)
        (self.phone.monitor / "run/sensors.tsv").unlink()                # the 2-second sensor snapshot
        status = self.phone.report("status")
        self.assertEqual((status["body"], status["body_from"]), (390, "skin"))

    def test_v28_temperatures_do_not_carry_over(self):
        # A v2.8 config: its TARGET_TEMP and GAME_LIMIT were processor thresholds.
        write(self.phone.data / "config", "MODE=game\nTARGET_TEMP=44\nGAME_LIMIT=48\nCHARGE_STOP=80\nCHARGE_RESUME=75\n"
                                          "CHARGE_THERMAL=0\nINTERVAL=15\n")
        config = self.phone.report("status")["config"]
        self.assertEqual((config["mode"], config["TARGET_TEMP"], config["GAME_LIMIT"], config["CHARGE_STOP"], config["INTERVAL"]),
                         ("game", 41, 44, 80, 15))
        self.assertEqual(config["CHARGE_THERMAL"], 0)                      # kept as saved
        self.assertEqual(self.phone.report("set", "TARGET_TEMP", "44"), {"ok": 1})
        self.assertIn("CTRL_VER=3", (self.phone.data / "config").read_text())
        config = self.phone.report("status")["config"]
        self.assertEqual((config["TARGET_TEMP"], config["GAME_LIMIT"], config["CHARGE_RESUME"]), (44, 44, 75))

    def test_saver_and_game(self):
        self.assertEqual(self.phone.report("mode", "hemat"), {"ok": 1})
        self.phone.set_temp(65.0)
        self.phone.set_body(35.0)
        state = self.phone.step()
        self.assertEqual((state["limit"], state["big"], state["little"]), (39, 60, 80))
        self.assertEqual(self.phone.caps(), {"policy0": 1500000, "policy4": 1500000, "policy7": 1200000})
        self.phone.set_body(39.0)                                         # Hemat steps down from its own cap
        self.assertEqual(self.phone.step()["big"], 50)
        self.phone.report("mode", "game")
        self.phone.set_body(42.5)
        state = self.phone.step()
        self.assertEqual((state["limit"], state["big"], state["boost"]), (44, 100, 1))
        self.assertEqual(self.phone.caps(), {"policy0": 2000000, "policy4": 3000000, "policy7": 3250000})
        self.assertEqual((self.phone.cpuctl / "top-app/cpu.uclamp.min").read_text().strip(), "20")
        self.phone.set_body(44.0)                                         # Performa's limit on the phone body
        self.assertEqual(self.phone.step()["big"], 90)
        self.phone.report("mode", "seimbang")
        self.assertEqual(self.phone.step()["boost"], 0)
        self.assertEqual((self.phone.cpuctl / "top-app/cpu.uclamp.min").read_text().strip(), "0.00")
        self.assertEqual((self.phone.monitor / "modes.tsv").read_text().split()[1::2], ["hemat", "game", "seimbang"])
        self.assertIn("Mode: Kernel Default", self.phone.events()[:2])

    def test_charge_limit(self):
        self.save_switch()
        self.phone.set_battery(81, "Charging", 33.0)
        self.assertEqual(self.phone.step()["charge_off"], "batas")
        self.assertEqual(self.phone.node("input_suspend"), "1")
        self.assertIn("Baterai 81%: cas dihentikan, lanjut di 75%", self.phone.events()[0])
        self.phone.set_battery(76, "Discharging", 33.0)
        self.assertEqual(self.phone.step()["charge_off"], "batas")
        self.phone.set_battery(76, "Charging", 33.0)                      # turned back on by a replug
        write(self.phone.battery / "input_suspend", "0\n")
        self.phone.step()
        self.assertEqual(self.phone.node("input_suspend"), "1")
        self.phone.set_battery(75, "Discharging", 33.0)
        self.assertEqual(self.phone.step()["charge_off"], "")
        self.assertEqual(self.phone.node("input_suspend"), "0")
        self.assertIn("Cas dilanjutkan (baterai 75%", self.phone.events()[0])

    def test_battery_heat_and_monitor_cause(self):
        self.save_switch()
        self.phone.set_body(36.0)   # a hot battery pauses charging; the CPU follows the phone body
        self.phone.set_battery(50, "Charging", 42.5)
        # Default (CHARGE_THERMAL=0, owner 2026-10-24): HyperCharge and the phone manage charging heat.
        self.assertEqual(self.phone.report("status")["config"]["CHARGE_THERMAL"], 0)
        self.assertEqual(self.phone.step()["charge_off"], "")
        self.assertEqual(self.phone.node("input_suspend"), "0")
        # Opted in, the battery threshold and the Kernel Default heat pause apply.
        self.assertEqual(self.phone.report("set", "CHARGE_THERMAL", "1"), {"ok": 1})
        self.phone.start_recorder()
        self.assertEqual(self.phone.step()["charge_off"], "baterai")
        self.phone.set_battery(50, "Discharging", 39.5)
        self.assertEqual(self.phone.step()["charge_off"], "baterai")     # resumes only at 39 °C
        self.phone.set_battery(50, "Discharging", 39.0)
        self.assertEqual(self.phone.step()["charge_off"], "")
        # Cogan Thermal Monitor says charging heats the phone: Seimbang pauses charging.
        self.phone.set_battery(50, "Charging", 35.0)
        self.phone.set_body(43.0)
        self.phone.set_temp(65.0)                                         # and the processor works
        self.phone.monitor_report("Cas cepat")
        state = self.phone.step()
        self.assertEqual((state["charge_off"], state["source"], state["cause"]), ("panas", "monitor", "Cas cepat"))
        self.assertEqual(state["level"], 0)                               # pausing the charger comes first
        self.assertIn("Badan HP 43.0 °C karena cas: cas dijeda sampai 38 °C", self.phone.events()[0])
        # The pause gets three checks; a body still hot after that brings the CPU in.
        self.assertEqual([self.phone.step()["level"] for _ in range(3)], [0, 0, 1])
        self.phone.set_body(37.5)
        self.assertEqual(self.phone.step()["charge_off"], "")
        # Another cause (a game) is handled by the CPU, not by stopping the charger.
        self.phone.set_body(43.0)
        self.phone.monitor_report("Grafis berat: Mobile Legends")
        state = self.phone.step()
        self.assertEqual((state["charge_off"], state["level"] > 0), ("", True))
        # A stale report is ignored.
        self.phone.monitor_report("Cas cepat", age=600)
        self.assertEqual(self.phone.step()["source"], "sensor")
        # Opting out again releases the module's own heat pause at the next check.
        self.phone.set_body(38.0)
        self.phone.set_battery(50, "Charging", 43.0)
        self.assertEqual(self.phone.step()["charge_off"], "baterai")
        self.assertEqual(self.phone.report("set", "CHARGE_THERMAL", "0"), {"ok": 1})
        self.assertEqual(self.phone.step()["charge_off"], "")
        self.assertEqual(self.phone.node("input_suspend"), "0")

    def test_failsafe_and_switch_off(self):
        self.save_switch()
        self.phone.set_battery(90, "Charging", 44.0)
        self.assertEqual(self.phone.step()["charge_off"], "batas")      # heat alone pauses only when opted in
        self.phone.set_battery(12, "Discharging", 44.0)                   # nearly empty: always charge
        self.assertEqual(self.phone.step()["charge_off"], "")
        self.phone.set_battery(90, "Charging", 30.0)
        self.assertEqual(self.phone.report("set", "CHARGE_CTRL", "0"), {"ok": 1})
        self.assertEqual(self.phone.step()["charge_off"], "")
        self.assertEqual(self.phone.node("input_suspend"), "0")

    def test_settings_are_validated(self):
        self.assertEqual(self.phone.report("set", "CHARGE_STOP", "85", "CHARGE_RESUME", "80", "TARGET_TEMP", "40"), {"ok": 1})
        config = self.phone.report("status")["config"]
        self.assertEqual((config["CHARGE_STOP"], config["CHARGE_RESUME"], config["TARGET_TEMP"], config["mode"]), (85, 80, 40, "seimbang"))
        for args in (("CHARGE_RESUME", "90"), ("MODE", "turbo"), ("TARGET_TEMP", "99"), ("GAME_LIMIT", "55"), ("CTRL_VER", "1"),
                     ("INTERVAL", "1;reboot"), ("FOO", "1")):
            self.assertEqual(self.phone.report("set", *args)["ok"], 0, args)
        self.assertEqual(self.phone.report("status")["config"]["CHARGE_RESUME"], 80)
        text = (self.phone.data / "config").read_text()
        self.assertNotIn("reboot", text)
        self.assertNotIn("turbo", text)

    def test_status(self):
        keys = ("installed", "running", "fresh", "stalled", "cause", "app")
        self.phone.monitor_report("Aplikasi berat: Instagram", app="Instagram")
        status = self.phone.report("status")
        self.assertEqual((status["running"], status["main"], status["switch"], status["state"]), (0, 400, "", None))
        self.assertEqual((status["body"], status["body_from"]), (300, "battery"))   # no phone body sensor here
        self.assertEqual(status["gpu"], {"devfreq": [], "ged": {"cur": -1, "upbound": -1, "levels": -1}, "gpufreqv2": 0})
        self.assertEqual(status["battery"], {"level": 50, "status": "charging", "temp": 300, "current": 1000})
        # v2.8: a report without a running recorder is not used.
        self.assertEqual({k: status["monitor"][k] for k in keys},
                         {"installed": 0, "running": 0, "fresh": 0, "stalled": 0, "cause": "", "app": ""})
        self.assertEqual([p["name"] for p in status["policies"]], ["policy0", "policy4", "policy7"])
        self.phone.start_recorder()
        monitor = self.phone.report("status")["monitor"]
        self.assertEqual({k: monitor[k] for k in keys}, {"installed": 1, "running": 1, "fresh": 1, "stalled": 0,
                                                         "cause": "Aplikasi berat: Instagram", "app": "Instagram"})
        self.assertEqual(monitor["pid"], self.phone.recorder.pid)

    def test_gpu_nodes_are_reported_and_never_written(self):
        mali = self.phone.sys / "class/devfreq/13000000.mali"
        for name, value in {"cur_freq": "850000000", "max_freq": "1300000000", "min_freq": "265000000",
                            "available_frequencies": "1300000000 1100000000 850000000 265000000"}.items():
            write(mali / name, value + "\n")
        write(self.phone.sys / "class/devfreq/ufshc/max_freq", "1\n")       # not a GPU
        write(self.phone.sys / "kernel/ged/hal/current_freqency", "850000\n")
        before = {path: path.read_text() for path in self.phone.sys.rglob("*") if path.is_file()}
        self.phone.set_body(44.0)
        for _ in range(4):
            self.phone.step()
        gpu = self.phone.report("status")["gpu"]
        self.assertEqual(gpu["devfreq"], [{"name": "13000000.mali", "cur": 850000000, "max": 1300000000, "min": 265000000,
                                           "steps": 4, "writable": 1}])
        self.assertEqual(gpu["ged"]["cur"], 850000)
        for path in (mali / "max_freq", mali / "min_freq", self.phone.sys / "kernel/ged/hal/current_freqency"):
            self.assertEqual(path.read_text(), before[path])

    def test_hyperos_thermal_state_is_reported_and_never_written(self):
        self.assertEqual(self.phone.report("status")["hyperos"], {"present": 0})
        # HyperOS's own thermal_message nodes (owner's phone, 24 Oct 2026: board_sensor_temp 40613).
        message = self.phone.sys / "class/thermal/thermal_message"
        for name, value in {"board_sensor_temp": "40613", "sconfig": "10", "temp_state": "0", "cpu_limits": "cpu7 2800000",
                            "modem_limit": "0", "thermal_max_brightness": "4095"}.items():
            write(message / name, value + "\n")
        before = {path: path.read_text() for path in message.iterdir()}
        (self.phone.monitor / "run/sensors.tsv").unlink()                # the 2-second sensor snapshot
        status = self.phone.report("status")
        self.assertEqual(status["hyperos"], {"present": 1, "board": 406, "sconfig": "10", "temp_state": "0",
                                             "cpu_limits": "cpu7 2800000", "modem_limit": "0", "wifi_limit": "",
                                             "max_brightness": "4095", "video_mode": ""})
        # Every live read carries it too, so the card stays when the page reopens (owner 2026-10-24:
        # "nanti ada nanti ilang").
        self.assertEqual(self.phone.report("live")["hyperos"], status["hyperos"])
        write(message / "cpu_limits", 'cpu7 "2800000"\tx\\y\n')                  # quoted and escaped as JSON
        self.assertEqual(self.phone.report("live")["hyperos"]["cpu_limits"], 'cpu7 "2800000"\tx\\y')
        write(message / "cpu_limits", "cpu7 2800000\n")
        # The board temperature joins the phone body group: the controller reads it like a skin sensor.
        self.assertEqual((status["body"], status["body_from"]), (406, "skin"))
        self.phone.set_temp(65.0)
        self.phone.set_body(39.0)
        state = self.phone.step()
        self.assertEqual((state["body"], state["level"]), (406, 1))       # within 1 °C of 41: a gentle step
        self.phone.set_body(41.5)                                         # HyperOS's number wins (v2.9.1)
        self.assertEqual(self.phone.step()["body"], 406)
        self.assertEqual({path: path.read_text() for path in message.iterdir()}, before)

    def test_start_and_stop_put_everything_back(self):
        self.save_switch()
        self.phone.report("set", "INTERVAL", "5")
        self.phone.set_temp(60.0)
        self.phone.set_body(46.0)
        self.phone.set_battery(85, "Charging", 33.0)
        status = self.phone.report("start")
        try:
            self.assertEqual(status["running"], 1)
            deadline = time.time() + 10
            while time.time() < deadline and self.phone.node("input_suspend") != "1":
                time.sleep(0.1)
            self.assertEqual(self.phone.node("input_suspend"), "1")
            self.assertLess(self.phone.caps()["policy4"], 3000000)
            self.assertEqual(self.phone.report("start")["running"], 1)
        finally:
            started = time.time()
            stopped = self.phone.report("stop")
        self.assertLess(time.time() - started, 4)                         # the controller wakes up for TERM
        self.assertEqual(stopped["running"], 0)
        self.assertEqual(self.phone.caps(), {"policy0": 2000000, "policy4": 3000000, "policy7": 3250000})
        self.assertEqual(self.phone.node("input_suspend"), "0")
        self.assertEqual((self.phone.monitor / "modes.tsv").read_text().split()[-1], "none")
        self.assertIn("Cogan Smart · Power berhenti", self.phone.events()[0])


class SwitchDetectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        # input_suspend exists but does nothing here; battery_charging_enabled really stops charging.
        self.phone = FakePhone(Path(self.tmp.name), charger_switch=("battery_charging_enabled", "0"))
        self.phone.report("set", "CHARGE_STOP", "80", "CHARGE_RESUME", "75")

    def tearDown(self):
        self.phone.unplug()
        self.tmp.cleanup()

    def test_detect_from_webui(self):
        result = self.phone.report("detect")
        self.assertEqual((result["ok"], result["switch"]), (1, "class/power_supply/battery/battery_charging_enabled"))
        self.assertEqual(result["tried"], [
            {"node": "class/power_supply/battery/input_suspend", "result": "tidak_berpengaruh"},
            {"node": "class/power_supply/battery/battery_charging_enabled", "result": "ok"},
        ])
        self.assertEqual((self.phone.node("input_suspend"), self.phone.node("battery_charging_enabled")), ("0", "1"))

    def test_detected_on_first_need(self):
        self.phone.set_battery(85, "Charging", 33.0)
        state = self.phone.step()
        self.assertEqual(state["charge_off"], "batas")
        self.assertEqual(self.phone.node("battery_charging_enabled"), "0")
        self.assertEqual(self.phone.report("status")["switch"], "class/power_supply/battery/battery_charging_enabled")
        self.assertTrue(any("Saklar cas ditemukan" in event for event in self.phone.events()))

    def test_not_charging(self):
        self.phone.unplug()
        self.phone.set_battery(50, "Discharging", 30.0)
        result = self.phone.report("detect")
        self.assertEqual(result["ok"], 0)
        self.assertIn("Colokkan charger", result["error"])


class PackageTests(unittest.TestCase):
    def test_zip(self):
        with tempfile.TemporaryDirectory() as out:
            result = subprocess.run([sys.executable, str(ROOT / "scripts/package_module.py"), str(MODULE), out],
                                    capture_output=True, text=True, check=True)
            with zipfile.ZipFile(result.stdout.strip()) as archive:
                modes = {info.filename: (info.external_attr >> 16) & 0o777 for info in archive.infolist()}
        self.assertEqual(modes["power/controller.sh"], 0o755)
        self.assertEqual(modes["power/power.awk"], 0o644)
        self.assertIn("webroot/index.html", modes)
        html = (MODULE / "webroot/index.html").read_text()
        self.assertIn("/data/adb/modules/cogan_smart/power/report.sh", html)


if __name__ == "__main__":
    unittest.main()
