#!/usr/bin/env python3
"""report_bundle_budget: asset budget gate from a manifest (leaf 9/5).

Reads a JSON/text manifest of emitted assets (name, type, bytes, gzip bytes) —
or a build output directory — and compares against a budget file. Never
invents sizes: with no manifest and no directory it exits 2 with guidance.

Manifest JSON: {"assets":[{"path":"app.js","bytes":412000,"gzip":120000}]}
Budget  JSON: {"route_budget_k":170,"third_party_k":60,"font_k":60,
               "max_blocking_scripts":2,"lazy_img_required":true}

Usage: python -B scripts/report_bundle_budget.py --manifest m.json
        [--budget b.json] [--dir dist] [--format text|json]
Exit code: 0 within budget, 1 over budget, 2 inputs missing.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys

from _common import emit

DEFAULTS = {"route_budget_k": 170, "third_party_k": 60,
            "font_k": 60, "hero_image_k": 0}

JS = re.compile(r"\.js$", re.I)
CSS = re.compile(r"\.css$", re.I)
FONT = re.compile(r"\.(woff2?|ttf|eot)$", re.I)
IMG = re.compile(r"\.(png|jpe?g|webp|avif|gif|svg)$", re.I)


def load_manifest(path):
    with open(path, "r", encoding="utf-8") as handle:
        doc = json.load(handle)
    items = doc.get("assets", doc if isinstance(doc, list) else [])
    out = []
    for i in items:
        out.append({"path": str(i.get("path", i.get("name", "?"))),
                    "bytes": int(i.get("bytes", i.get("size", 0))),
                    "gzip": int(i.get("gzip", i.get("gzipBytes", 0)) or 0)})
    return out


def from_dir(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ("node_modules", ".git")]
        for name in filenames:
            full = os.path.join(dirpath, name)
            if name.endswith((".js", ".css", ".html", ".png", ".jpg", ".jpeg",
                              ".webp", ".avif", ".svg", ".woff", ".woff2")):
                size = os.path.getsize(full)
                out.append({"path": os.path.relpath(full, root), "bytes": size,
                            "gzip": 0})
    return out


def size(item):
    return item["gzip"] or item["bytes"]


def vendor_like(path):
    base = os.path.basename(path)
    return ("vendor" in path or "node_modules" in path
            or base.startswith(("react", "vue", "lodash", "moment")))


def audit(assets, budget):
    """Sum sizes per class and compare with the budget (never invents sizes)."""
    k = 1024.0

    def total(match=None, pred=None):
        out = 0
        for a in assets:
            path = a["path"]
            if match is not None and not match.search(path):
                continue
            if pred is not None and not pred(path):
                continue
            out += size(a)
        return out

    routes = total(match=JS, pred=lambda p: not vendor_like(p))
    vendor = total(pred=vendor_like)
    fonts = total(match=FONT)
    css = total(match=CSS)
    cap = budget["route_budget_k"] * k
    findings = []
    if vendor > budget["third_party_k"] * k:
        findings.append("third-party JS %.0fk > budget %dk"
                        % (vendor / k, budget["third_party_k"]))
    if routes > cap:
        findings.append("route JS %.0fk > budget %dk"
                        % (routes / k, budget["route_budget_k"]))
    if fonts > budget["font_k"] * k:
        findings.append("fonts %.0fk > budget %dk"
                        % (fonts / k, budget["font_k"]))
    for a in assets:
        if JS.search(a["path"]) and size(a) > cap:
            findings.append("single chunk over budget: %s (%.0fk)"
                            % (a["path"], size(a) / k))
    findings += image_gate(assets, budget, k)
    summary = {"assets": len(assets), "route_js_k": round(routes / k, 1),
               "vendor_js_k": round(vendor / k, 1), "css_k": round(css / k, 1),
               "fonts_k": round(fonts / k, 1)}
    return summary, findings


def image_gate(assets, budget, k):
    if not budget.get("hero_image_k"):
        return []
    imgs = [a for a in assets if IMG.search(a["path"])]
    if not imgs:
        return []
    biggest = max(imgs, key=size)
    if size(biggest) > budget["hero_image_k"] * k:
        return ["largest image %s over %dk"
                % (biggest["path"], budget["hero_image_k"])]
    return []


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("--manifest")
    argp.add_argument("--budget")
    argp.add_argument("--dir")
    argp.add_argument("--format", choices=("text", "json"), default="text")
    args = argp.parse_args()
    assets = load_assets(args)
    if not assets:
        print("error: no asset data — pass --manifest <json> or --dir <build dir>")
        return 2
    budget = dict(DEFAULTS)
    if args.budget:
        with open(args.budget, "r", encoding="utf-8") as handle:
            budget.update(json.load(handle))
    summary, findings = audit(assets, budget)
    if args.format == "json":
        print(json.dumps({"summary": summary, "budget": budget,
                          "findings": findings}, ensure_ascii=False))
        return 1 if findings else 0
    print("bundle: %d assets | route_js=%.0fk vendor=%.0fk css=%.0fk fonts=%.0fk"
          % (summary["assets"], summary["route_js_k"], summary["vendor_js_k"],
             summary["css_k"], summary["fonts_k"]))
    return emit(findings)


def load_assets(args):
    if args.manifest:
        return load_manifest(args.manifest)
    if args.dir and os.path.isdir(args.dir):
        return from_dir(args.dir)
    return []


if __name__ == "__main__":
    sys.exit(main())
