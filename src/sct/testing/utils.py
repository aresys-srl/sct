# SPDX-FileCopyrightText: Aresys S.r.l. <info@aresys.it>
# SPDX-License-Identifier: MIT

"""Testing framework cli utilities."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table

from sct.cli.common import supports_unicode
from sct.configuration.logger import sct_logger

console = Console()


def safe_rule_printing(title: str, fallback_title: str) -> None:
    """Print a Rich rule, falling back to ASCII when Unicode is unsupported."""
    console.rule(title if supports_unicode() else fallback_title)


def summary_results(results: dict) -> bool:
    """Summary of tests results.

    Parameters
    ----------
    results : dict
        results coming from run_test function

    Returns
    -------
    bool
        True if all tests are passed, else False
    """
    tests_num = sum(len(tests) for tests in results.values())
    passed_tests = sum(sum(tests.values()) for tests in results.values())
    failed_tests = tests_num - passed_tests
    outcome = passed_tests == tests_num

    if supports_unicode():
        passed = "✔ PASS"
        failed = "✖ FAIL"
        title = "📊 Test Summary"
    else:
        passed = "PASS"
        failed = "FAIL"
        title = "Test Summary"

    if outcome:
        status = f"[bold green]{passed} {passed_tests}/{tests_num}[/bold green]"
    elif passed_tests == 0:
        status = f"[bold red]{failed} {failed_tests}/{tests_num}[/bold red]"
    else:
        status = (
            f"[bold green]{passed} {passed_tests}/{tests_num}[/bold green]"
            f"   [bold red]{failed} {failed_tests}/{tests_num}[/bold red]"
        )

    console.rule(f"[bold cyan]{title}[/bold cyan]   {status}")

    for sensor_name, sensor_results in results.items():
        try:
            print_dict_as_table(title=sensor_name, data=sensor_results)
        except Exception:
            print(f"Sensor: {sensor_name}\n")
            for test_name, test_result in sensor_results.items():
                print(f"{test_name}: {'PASS' if test_result else 'FAIL'}")

    if outcome:
        sct_logger.success("INTEGRATION TESTS: PASS")
    else:
        sct_logger.fail("INTEGRATION TESTS: FAIL")

    return outcome


def print_dict_as_table(data: dict, title: str = "Data"):
    """Printing summary results by sensor as a Rich Table."""
    table = Table(title=title, header_style="bold #C6A0F6")
    table.add_column("Test Name", style="bold")
    table.add_column("Status", style="bold")

    console.print("")

    for test_name, test_result in data.items():
        table.add_row(str(test_name), status_to_color(test_result))

    console.print(table)


def status_to_color(value: bool) -> str:
    """Return colored test status."""
    symbol = "✔" if supports_unicode() else ""
    status = "PASS" if value else "FAIL"
    color = "#40A02B" if value else "#E74C3C"

    return f"[{color}]{symbol} {status}[/{color}]"
