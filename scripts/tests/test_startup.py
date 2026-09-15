from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


SCRIPT = Path(__file__).resolve().parents[1] / "start-sledtrace.py"
spec = importlib.util.spec_from_file_location("sledtrace_startup", SCRIPT)
startup = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = startup
spec.loader.exec_module(startup)


class StartupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        (self.repo / "collector/go").mkdir(parents=True)
        vite = self.repo / "dashboard/web/node_modules/vite/bin/vite.js"
        vite.parent.mkdir(parents=True)
        vite.touch()
        self.environ = patch.dict(os.environ, {}, clear=True)
        self.environ.start()
        self.addCleanup(self.environ.stop)
        self.settings = startup.configure(self.repo, [])

    def process(self, code=None):
        proc = Mock()
        proc.pid = 12345
        proc.poll.return_value = code
        return proc

    def test_defaults_align_collector_dashboard_and_origins(self):
        self.assertEqual(self.settings.collector_url, "http://127.0.0.1:4319")
        self.assertEqual(self.settings.env["VITE_SLEDTRACE_API_URL"], self.settings.collector_url)
        self.assertIn(self.settings.dashboard_url, self.settings.env["SLEDTRACE_ALLOWED_ORIGINS"])

    def test_custom_ports_and_legacy_address(self):
        os.environ["RAGLENS_COLLECTOR_ADDR"] = ":14319"
        settings = startup.configure(self.repo, ["--dashboard-port", "15173"])
        self.assertEqual(settings.collector_url, "http://127.0.0.1:14319")
        self.assertEqual(settings.dashboard_url, "http://127.0.0.1:15173")
        self.assertIn(":15173", settings.env["SLEDTRACE_ALLOWED_ORIGINS"])

    def test_preferred_address_and_explicit_client_configuration_win(self):
        os.environ.update(SLEDTRACE_COLLECTOR_ADDR="[::]:14319", RAGLENS_COLLECTOR_ADDR=":1",
                          VITE_RAGLENS_API_URL="https://example.test", SLEDTRACE_ALLOWED_ORIGINS="https://example.test")
        settings = startup.configure(self.repo, [])
        self.assertEqual(settings.collector_url, "http://[::1]:14319")
        self.assertEqual(settings.env["VITE_SLEDTRACE_API_URL"], "https://example.test")
        self.assertEqual(settings.env["SLEDTRACE_ALLOWED_ORIGINS"], "https://example.test")

    def test_invalid_address_is_actionable(self):
        for address in ("localhost", "localhost:0", "localhost:99999", "http://localhost:4319", "user:pass@localhost:4319", "localhost:4319/path"):
            with self.subTest(address=address), patch.dict(os.environ, SLEDTRACE_COLLECTOR_ADDR=address):
                with self.assertRaisesRegex(startup.StartupError, "host:port"):
                    startup.configure(self.repo, [])

    def test_invalid_port_and_timeout(self):
        for args in (["--dashboard-port", "0"], ["--startup-timeout", "nan"], ["--startup-timeout", "0"]):
            with self.subTest(args=args), self.assertRaises(startup.StartupError):
                startup.configure(self.repo, args)

    def test_missing_executable_fails_before_spawning_services(self):
        for missing in ("go", "node", startup.npm_command()):
            with self.subTest(missing=missing), patch.object(startup.shutil, "which", side_effect=lambda name: None if name == missing else name), patch.object(startup, "start_process") as spawn:
                with self.assertRaisesRegex(startup.StartupError, "Missing executable"):
                    startup.preflight(self.settings)
                spawn.assert_not_called()

    def test_node_version_and_missing_dependencies(self):
        with patch.object(startup.shutil, "which", side_effect=lambda name: name), patch.object(startup.subprocess, "run") as run:
            run.return_value.stdout = "v20.0.0"
            with self.assertRaisesRegex(startup.StartupError, "Node.js 22"):
                startup.preflight(self.settings)
            run.return_value.stdout = "v22.0.0"
            (self.repo / "dashboard/web/node_modules/vite/bin/vite.js").unlink()
            with self.assertRaisesRegex(startup.StartupError, "npm ci"):
                startup.preflight(self.settings)

    def test_port_conflict_does_not_close_existing_listener(self):
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            listener.listen()
            port = listener.getsockname()[1]
            with self.assertRaisesRegex(startup.StartupError, "--dashboard-port"):
                startup.check_port("127.0.0.1", port, "Dashboard")
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                pass

    def test_socket_error_is_locale_independent(self):
        error = OSError(10048, "localized operating-system text")
        with patch.object(error, "winerror", 10048, create=True):
            self.assertEqual(startup.format_socket_error(error), "socket error 10048")

    def test_healthy_services_must_identify_themselves(self):
        response = Mock(status=200)
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        with patch.object(startup.urllib.request, "build_opener") as factory:
            factory.return_value.open.return_value = response
            for body, collector, expected in (
                (b'{"status":"ok","service":"sledtrace-collector"}', True, True),
                (b'{"status":"ok"}', True, False),
                (b'[]', True, False),
                (b'invalid json', True, False),
                (b'<title>SledTrace</title>', False, True),
                (b'<title>Another app</title>', False, False),
            ):
                response.read.return_value = body
                self.assertEqual(startup.probe_service("http://127.0.0.1", collector)[0], expected)

    def test_timeout_identifies_unhealthy_service_and_address(self):
        processes = [("Collector", self.process()), ("Dashboard", self.process())]
        with patch.object(startup, "probe_service", return_value=(False, "HTTP 503")), patch.object(startup.time, "monotonic", side_effect=[0, 61]):
            with self.assertRaisesRegex(startup.StartupError, "4319/health.*503.*5173"):
                startup.wait_until_ready(self.settings, processes)

    def test_readiness_waits_for_both_services(self):
        with patch.object(startup, "probe_service", side_effect=[(True, "ready"), (False, "starting"), (True, "ready")]) as probe, patch.object(startup.time, "sleep"), contextlib.redirect_stdout(io.StringIO()):
            startup.wait_until_ready(self.settings, [("Collector", self.process()), ("Dashboard", self.process())])
            self.assertEqual(probe.call_count, 3)

    def test_even_zero_exit_is_a_startup_failure(self):
        with self.assertRaisesRegex(startup.StartupError, "Dashboard exited with code 0"):
            startup.ensure_running([("Dashboard", self.process(0))])

    def run_main(self, starts, readiness=None, supervision=None):
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(startup, "configure", return_value=self.settings), patch.object(startup, "preflight", return_value={"go": "go", startup.npm_command(): "npm"}), patch.object(startup, "start_process", side_effect=starts) as spawn, patch.object(startup, "wait_until_ready", side_effect=readiness), patch.object(startup, "supervise", side_effect=supervision), patch.object(startup, "stop_processes") as stop, contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            code = startup.main([])
        return code, output.getvalue(), errors.getvalue(), spawn, stop

    def test_second_launch_failure_cleans_up_first_service(self):
        collector = self.process()
        code, output, errors, _, stop = self.run_main([collector, startup.StartupError("npm failed")])
        self.assertEqual(code, 1)
        self.assertIn("npm failed", errors)
        self.assertNotIn("SledTrace ready", output)
        stop.assert_called_once_with([("Collector", collector)])

    def test_readiness_failure_cleans_both_services_and_does_not_claim_ready(self):
        collector, dashboard = self.process(), self.process()
        code, output, _, _, stop = self.run_main([collector, dashboard], startup.StartupError("health timeout"))
        self.assertEqual(code, 1)
        self.assertNotIn("SledTrace ready", output)
        stop.assert_called_once_with([("Collector", collector), ("Dashboard", dashboard)])

    def test_interrupt_after_ready_restores_signals_and_cleans_both_services(self):
        previous = signal.getsignal(signal.SIGTERM)
        code, output, _, spawn, stop = self.run_main([self.process(), self.process()], supervision=KeyboardInterrupt())
        self.assertEqual(code, 130)
        self.assertIn("SledTrace ready. Open http://127.0.0.1:5173", output)
        self.assertIn("--strictPort", spawn.call_args_list[1].args[0])
        self.assertEqual(len(stop.call_args.args[0]), 2)
        self.assertEqual(signal.getsignal(signal.SIGTERM), previous)

    def test_service_exit_after_ready_fails_and_cleans_peer(self):
        code, _, errors, _, stop = self.run_main([self.process(), self.process()], supervision=startup.StartupError("Dashboard exited"))
        self.assertEqual(code, 1)
        self.assertIn("Dashboard exited", errors)
        self.assertEqual(len(stop.call_args.args[0]), 2)


class ProcessTreeTests(unittest.TestCase):
    def test_cleanup_stops_real_wrapper_and_listener_child(self):
        with socket.socket() as reservation:
            reservation.bind(("127.0.0.1", 0))
            port = reservation.getsockname()[1]
        child = f"import socket,time; s=socket.socket(); s.bind(('127.0.0.1',{port})); s.listen(); time.sleep(120)"
        parent = f"import subprocess,sys,time; subprocess.Popen([sys.executable,'-c',{child!r}]); time.sleep(120)"
        proc = startup.start_process([sys.executable, "-c", parent], SCRIPT.parent, os.environ.copy())
        processes = [("test service", proc)]
        try:
            deadline = time.monotonic() + 10
            while True:
                try:
                    with socket.create_connection(("127.0.0.1", port), timeout=0.1):
                        break
                except OSError:
                    if time.monotonic() >= deadline:
                        self.fail("test child never started listening")
                    time.sleep(0.05)
            startup.stop_processes(processes)
            self.assertIsNotNone(proc.poll())
            with self.assertRaises(OSError):
                socket.create_connection(("127.0.0.1", port), timeout=0.2)
        finally:
            startup.stop_processes(processes)


if __name__ == "__main__":
    unittest.main()
