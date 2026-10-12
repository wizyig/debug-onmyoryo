from __future__ import annotations

import json
import os
import pathlib
import sys
from dataclasses import dataclass

import yaml


@dataclass(slots=True)
class GateResult:
    name: str
    passed: bool
    message: str


class CoverageGate:
    def __init__(
        self,
        policy_file: str = "config/coverage_policy.yaml",
        coverage_file: str = "artifacts/coverage.json",
        previous_file: str = "artifacts/previous_coverage.json",
    ):
        with open(policy_file, encoding="utf-8") as f:
            self.policy = yaml.safe_load(f)
        with open(coverage_file, encoding="utf-8") as f:
            self.coverage = json.load(f)
        self.previous = {}
        previous_path = pathlib.Path(previous_file)
        if previous_path.exists():
            with open(previous_file, encoding="utf-8") as f:
                self.previous = json.load(f)

    @property
    def mode(self) -> str:
        configured = self.policy["coverage"].get("mode", "full")
        return os.getenv("COVERAGE_MODE", configured)

    def global_gate(self) -> GateResult:
        current = float(self.coverage["global"])
        minimum = float(self.policy["coverage"]["global"]["minimum"])
        return GateResult(
            name="Global Gate",
            passed=current >= minimum,
            message=f"{current:.2f}% (required {minimum:.2f}%)",
        )

    def module_gate(self) -> GateResult:
        failures = []
        modules = self.policy["coverage"].get("modules", {})
        actual_modules = self.coverage.get("modules", {})
        for module, threshold in modules.items():
            actual = float(actual_modules.get(module, 0.0))
            if actual < threshold:
                failures.append(f"{module}: {actual:.2f}% < {threshold:.2f}%")
        return GateResult(
            name="Module Gate",
            passed=not failures,
            message="All modules passed" if not failures else "\n".join(failures),
        )

    def pr_changed_files_gate(self) -> GateResult:
        failures = []
        changed = self.coverage.get("changed_files", {})
        for file_name, data in changed.items():
            actual = float(data["coverage"])
            required = float(data["required"])
            if actual < required:
                failures.append(f"{file_name}: {actual:.2f}% < {required:.2f}%")
        return GateResult(
            name="Changed Files Gate",
            passed=not failures,
            message="All changed files passed" if not failures else "\n".join(failures),
        )

    def regression_gate(self) -> GateResult:
        if not self.previous:
            return GateResult(name="Regression Gate", passed=True, message="No baseline")
        allowed = float(self.policy["coverage"]["global"]["allowed_regression"])
        current = float(self.coverage["global"])
        previous = float(self.previous["global"])
        drift = current - previous
        return GateResult(
            name="Regression Gate",
            passed=drift >= allowed,
            message=f"Drift {drift:+.2f}% (limit {allowed:+.2f}%)",
        )

    def selected_gates(self):
        if self.mode == "pr":
            return [self.global_gate, self.pr_changed_files_gate, self.regression_gate]
        return [self.global_gate, self.module_gate, self.pr_changed_files_gate, self.regression_gate]

    def run_all(self):
        return [gate() for gate in self.selected_gates()]

    def build_report(self, results, report_file="artifacts/coverage-report.md"):
        lines = ["<!-- DEBUG-ONMYORYO-COVERAGE -->", "", "# Coverage Report", ""]
        lines.append(f"Mode: {self.mode}")
        lines.append(f"Global: {float(self.coverage['global']):.2f}%")
        lines.append("")
        lines.append("## Gates")
        lines.append("")
        for result in results:
            icon = "✅" if result.passed else "❌"
            lines.append(f"{icon} {result.name}")
            lines.append(f"  - {result.message}")
        lines.append("")
        lines.append("## Module Coverage")
        lines.append("")
        modules = self.coverage.get("modules", {})
        for name, value in sorted(modules.items()):
            lines.append(f"- {name}: {float(value):.2f}%")
        pathlib.Path(report_file).parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def run(self) -> int:
        results = self.run_all()
        self.build_report(results)
        failed = [r for r in results if not r.passed]
        return 1 if failed else 0


def main():
    gate = CoverageGate()
    return gate.run()


if __name__ == "__main__":
    sys.exit(main())
