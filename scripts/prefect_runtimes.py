#!/usr/bin/env python3
import argparse
import json
import os
from datetime import datetime, timezone
from typing import Any
from urllib import error, request


def parse_iso8601(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)


def post_json(url: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url=url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req) as response:
        content = response.read().decode("utf-8")
    data = json.loads(content)
    if not isinstance(data, list):
        raise ValueError(f"Unexpected API response type: {type(data)}")
    return data


def post_json_all_pages(
    url: str,
    base_payload: dict[str, Any],
    page_limit: int = 200,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    offset = 0

    while True:
        payload = dict(base_payload)
        payload["limit"] = page_limit
        payload["offset"] = offset
        page = post_json(url, payload)
        rows.extend(page)
        if len(page) < page_limit:
            break
        offset += page_limit

    return rows


def get_json(url: str) -> dict[str, Any]:
    req = request.Request(url=url, method="GET")
    with request.urlopen(req) as response:
        content = response.read().decode("utf-8")
    data = json.loads(content)
    if not isinstance(data, dict):
        raise ValueError(f"Unexpected API response type: {type(data)}")
    return data


def runtime_seconds(start_time: str | None, end_time: str | None) -> float | None:
    if not start_time:
        return None
    start_dt = parse_iso8601(start_time)
    end_dt = parse_iso8601(end_time) if end_time else datetime.now(timezone.utc)
    return (end_dt - start_dt).total_seconds()


class FlowNameResolver:
    def __init__(self, api_url: str):
        self.api_url = api_url.rstrip("/")
        self._flow_name_by_id: dict[str, str] = {}
        self._flow_run_flow_id_by_id: dict[str, str] = {}
        self._flow_run_name_by_id: dict[str, str] = {}

    def _get_flow_name_by_id(self, flow_id: str | None) -> str:
        if not flow_id:
            return ""
        if flow_id in self._flow_name_by_id:
            return self._flow_name_by_id[flow_id]
        data = get_json(f"{self.api_url}/flows/{flow_id}")
        name = str(data.get("name", ""))
        self._flow_name_by_id[flow_id] = name
        return name

    def _get_flow_run_data(self, flow_run_id: str | None) -> dict[str, Any]:
        if not flow_run_id:
            return {}

        needs_fetch = (
            flow_run_id not in self._flow_run_flow_id_by_id
            or flow_run_id not in self._flow_run_name_by_id
        )
        if needs_fetch:
            data = get_json(f"{self.api_url}/flow_runs/{flow_run_id}")
            self._flow_run_flow_id_by_id[flow_run_id] = str(data.get("flow_id", ""))
            self._flow_run_name_by_id[flow_run_id] = str(data.get("name", ""))

        return {
            "flow_id": self._flow_run_flow_id_by_id.get(flow_run_id, ""),
            "name": self._flow_run_name_by_id.get(flow_run_id, ""),
        }

    def _get_flow_id_by_flow_run_id(self, flow_run_id: str | None) -> str:
        data = self._get_flow_run_data(flow_run_id)
        return str(data.get("flow_id", ""))

    def get_flow_run_name_by_id(self, flow_run_id: str | None) -> str:
        data = self._get_flow_run_data(flow_run_id)
        return str(data.get("name", ""))

    def resolve_for_row(self, kind: str, row: dict[str, Any]) -> str:
        if kind == "flow":
            return self._get_flow_name_by_id(str(row.get("flow_id", "")))

        if kind == "task":
            flow_id = str(row.get("flow_id", ""))
            if not flow_id:
                flow_run_id = str(row.get("flow_run_id", ""))
                flow_id = self._get_flow_id_by_flow_run_id(flow_run_id)
            return self._get_flow_name_by_id(flow_id)

        return ""


def print_flow_runs(rows: list[dict[str, Any]], resolver: FlowNameResolver) -> int:
    print("FLOW RUNS")
    print("-" * 140)
    print(
        f"{'flow_name':30} {'run_name':35} {'state':12} {'duration_s':12} {'start_time':25}"
    )
    print("-" * 140)

    shown = 0
    for row in rows:
        run_name = str(row.get("name", ""))
        flow_name = resolver.resolve_for_row("flow", row)
        state = ""
        state_obj = row.get("state")
        if isinstance(state_obj, dict):
            state = str(state_obj.get("type", ""))
        start_time = row.get("start_time")
        end_time = row.get("end_time")
        duration = runtime_seconds(start_time, end_time)
        if duration is None:
            continue
        start_txt = str(start_time or "")
        print(
            f"{flow_name[:30]:30} {run_name[:35]:35} {state[:12]:12} {duration:12.2f} {start_txt[:25]:25}"
        )
        shown += 1

    if shown == 0:
        print("No runs with start_time found.")
    print()
    return shown


def print_task_runs_for_selected_run(
    run_name: str,
    rows: list[dict[str, Any]],
    resolver: FlowNameResolver,
) -> int:
    print(f"TASK RUNS FOR FLOW RUN: {run_name}")
    print("-" * 150)
    print(
        f"{'flow_name':30} {'flow_run_name':35} {'task_run_name':35} {'state':12} {'duration_s':12} {'start_time':25}"
    )
    print("-" * 150)

    shown = 0
    for row in rows:
        task_name = str(row.get("name", ""))
        flow_run_id = str(row.get("flow_run_id", ""))
        flow_run_name = str(row.get("flow_run_name", ""))
        if not flow_run_name:
            flow_run_name = resolver.get_flow_run_name_by_id(flow_run_id)
        flow_name = resolver.resolve_for_row("task", row)
        state = ""
        state_obj = row.get("state")
        if isinstance(state_obj, dict):
            state = str(state_obj.get("type", ""))
        start_time = row.get("start_time")
        end_time = row.get("end_time")
        duration = runtime_seconds(start_time, end_time)
        if duration is None:
            continue
        start_txt = str(start_time or "")
        print(
            f"{flow_name[:30]:30} {flow_run_name[:35]:35} {task_name[:35]:35} {state[:12]:12} {duration:12.2f} {start_txt[:25]:25}"
        )
        shown += 1

    if shown == 0:
        print("No task runs with start_time found for this flow run.")
    print()
    return shown


def get_flow_runs(api_url: str) -> list[dict[str, Any]]:
    payload = {"sort": "START_TIME_DESC"}
    return post_json_all_pages(f"{api_url}/flow_runs/filter", payload)


def get_task_runs_for_flow_run_ids(
    api_url: str,
    flow_run_ids: list[str],
) -> list[dict[str, Any]]:
    if not flow_run_ids:
        return []

    payload = {
        "sort": "EXPECTED_START_TIME_DESC",
        "flow_run_filter": {"id": {"any_": flow_run_ids}},
    }

    id_set = set(flow_run_ids)

    try:
        rows = post_json_all_pages(f"{api_url}/task_runs/filter", payload)
    except error.HTTPError as exc:
        # Fallback for API variants that do not support flow_run_filter schema.
        if exc.code != 422:
            raise
        rows = post_json_all_pages(
            f"{api_url}/task_runs/filter",
            {"sort": "EXPECTED_START_TIME_DESC"},
        )

    # Some API variants may ignore filter keys silently; enforce the selection client-side.
    return [r for r in rows if str(r.get("flow_run_id", "")) in id_set]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Show Prefect flow runs or task runs for one specific flow run name."
    )
    parser.add_argument(
        "--run",
        help="Flow run name. If set, show task runs for the selected flow run name.",
    )
    args = parser.parse_args()

    api_url = os.getenv("PREFECT_API_URL", "http://127.0.0.1:4200/api").rstrip("/")
    resolver = FlowNameResolver(api_url)

    try:
        flow_runs = get_flow_runs(api_url)

        if not args.run:
            print_flow_runs(flow_runs, resolver)
            return 0

        selected = [r for r in flow_runs if str(r.get("name", "")) == args.run]
        if not selected:
            print(f"No flow run found with name: {args.run}")
            return 0

        flow_run_ids = [str(r.get("id", "")) for r in selected if str(r.get("id", ""))]
        task_runs = get_task_runs_for_flow_run_ids(api_url, flow_run_ids)
        print_task_runs_for_selected_run(args.run, task_runs, resolver)
    except error.HTTPError as exc:
        details = ""
        try:
            details = exc.read().decode("utf-8")
        except Exception:
            details = ""
        print(f"HTTP error from Prefect API: {exc.code} {exc.reason}")
        if details:
            print(details)
        return 1
    except error.URLError as exc:
        print(f"Could not connect to Prefect API: {exc.reason}")
        return 1
    except Exception as exc:
        print(f"Error while reading runtimes: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
