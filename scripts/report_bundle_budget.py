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


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("--manifest")
    argp.add_argument("--budget")
    argp.add_argument("--dir")
    argp.add_argument("--format", choices=("text", "json"), default="text")
    args = argp.parse_args()
    assets = []
    if args.manifest:
        assets = load_manifest(args.manifest)
    elif args.dir and os.path.isdir(args.dir):
        assets = from_dir(args.dir)
    if not assets:
        print("error: no asset data — pass --manifest <json> or --dir <build dir>")
        return 2
    budget = {"route_budget_k": 170, "third_party_k": 60, "font_k": 60}
    if args.budget:
        with open(args.budget, "r", encoding="utf-8") as handle:
            budget.update(json.load(handle))
    k = 1024.0

    def group(pred):
        return sum(a["gzip"] or a["bytes"] for a in assets if pred(a["path"]))

    vendor = group(lambda p: "vendor" in p or "node_modules" in p or os.path.basename(p).startswith(("react", "vue")))
    routes = group(lambda p: JS.search(p) and "vendor" not in p)
    fonts = group(FONT)
    css = group(CSS)
    heavy = [a for a in assets if (a["gzip"] or a["bytes"]) > budget["route_budget_k"] * k and JS.search(a["path"])]
    findings = []
    if vendor > budget["third_party_k"] * k:
        findings.append("third-party JS %.0fk > budget %dk" % (vendor / k, budget["third_party_k"]))
    if routes > budget["route_budget_k"] * k:
        findings.append("route JS %.0fk > budget %dk" % (routes / k, budget["route_budget_k"]))
    if fonts > budget["font_k"] * k:
        findings.append("fonts %.0fk > budget %dk" % (fonts / k, budget["font_k"]))
    for a in heavy:
        findings.append("single chunk over budget: %s (%.0fk)" % (a["path"], (a["gzip"] or a["bytes"]) / k))
    imgs = [a for a in assets if IMG.search(a["path"])]
    if imgs and budget.get("hero_image_k"):
        biggest = max(imgs, key=lambda a: a["gzip"] or a["bytes"])
        if (biggest["gzip"] or biggest["bytes"]) > budget["hero_image_k"] * k:
            findings.append("largest image %s over %dk" % (biggest["path"], budget["hero_image_k"]))
    summary = {"assets": len(assets), "route_js_k": round(routes / k, 1),
               "vendor_js_k": round(vendor / k, 1), "css_k": round(css / k, 1),
               "fonts_k": round(fonts / k, 1)}
    if args.format == "json":
        print(json.dumps({"summary": summary, "budget": budget, "findings": findings},
                         ensure_ascii=False))
        return 1 if findings else 0
    print("bundle: %d assets | route_js=%.0fk vendor=%.0fk css=%.0fk fonts=%.0fk" % (
        summary["assets"], summary["route_js_k"], summary["vendor_js_k"],
        summary["css_k"], summary["fonts_k"]))
    return emit(findings)


if __name__ == "__main__":
    sys.exit(main())
