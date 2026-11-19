"""Study 6.6: direct author-written HTML, one final review, real browser QA.

For a *new* direct-html-v1 course the Codex/DSH host writes the entire lesson
as HTML. Python verifies provenance, real review evidence and the rendered
artifact; it does not prescribe teaching sections or assemble text cards.
Existing V3.5 / V6.5 content and learner state stay untouched.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
from html.parser import HTMLParser
from pathlib import Path

CONTRACT = "direct-html-v1"
REVIEW_DIMENSIONS = frozenset((
    "source_fidelity", "explanation_depth", "teaching_sequence",
    "visual_pedagogy", "assessment_fairness",
))
PAGE_ID = re.compile(r"^[A-Za-z0-9_-]{1,90}$")


class DirectPageError(ValueError):
    pass


def sha(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def hash_json(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True))


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save(path, value):
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    temp = dest.with_suffix(dest.suffix + ".tmp")
    temp.write_bytes(json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8"))
    temp.replace(dest)


def locations(workspace, page_id):
    if not PAGE_ID.fullmatch(str(page_id)):
        raise DirectPageError("invalid page ID")
    w = Path(workspace)
    return (w / "authored-pages" / (page_id + ".html"),
            w / "reviews" / "html" / (page_id + ".json"),
            w / "reports" / "html" / (page_id + ".json"))


class PageReader(HTMLParser):
    """Structural checks only. Semantic sufficiency is an actual review task."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tag_stack = []
        self.in_script = 0
        self.hidden_stack = []
        self.headings = []
        self.visible_text = []
        self.head_text = []
        self.checkpoints = []
        self.script_src = []
        self.external = []
        self.has_body = False
        self.has_main = False
        self.has_html = False
        self.has_viewport = False
        self.tags = []
        self.current_heading = False
        self.in_details = 0
        self.main_open = 0
        self.main_visible_text = 0
        self.first_critical = None
        self.exercises = 0
        self.reveals = 0
        self.links = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        at = dict(attrs)
        self.tags.append(tag)
        if tag == "html": self.has_html = True
        if tag == "body": self.has_body = True
        if tag == "main": self.has_main = True; self.main_open += 1
        if tag == "meta" and at.get("name") == "viewport":
            self.has_viewport = True
        if tag == "details": self.in_details += 1
        if tag in ("script",):
            self.in_script += 1
            if at.get("src"): self.script_src.append(at["src"])
        if tag in ("iframe", "object", "embed"):
            self.external.append(tag)
        if tag == "h1": self.current_heading = True
        if tag in ("img",): self.images.append(at)
        if tag == "a": self.links.append(at.get("href", ""))
        if tag == "form": self.exercises += 1
        if tag in ("button", "input", "select", "textarea"): self.checkpoints.append(tag)
        if tag in ("details", "summary"): self.reveals += 1
        if tag == "link" and at.get("rel") == "stylesheet" and at.get("href", "").startswith(("http://", "https://")):
            self.external.append("external stylesheet")
        self.tag_stack.append(tag)

    def handle_endtag(self, tag):
        if tag == "script" and self.in_script:
            self.in_script -= 1
        if tag == "main" and self.main_open:
            self.main_open -= 1
        if tag == "details" and self.in_details:
            self.in_details -= 1
        if tag == "h1": self.current_heading = False
        if tag in self.tag_stack:
            i = len(self.tag_stack) - 1 - self.tag_stack[::-1].index(tag)
            self.tag_stack = self.tag_stack[:i]

    def handle_data(self, data):
        if self.in_script:
            return
        value = data.strip()
        if not value: return
        if self.current_heading: self.headings.append(value)
        self.visible_text.append(value)
        if self.main_open and not self.in_details:
            self.main_visible_text += len(value)
        if self.first_critical is None and self.main_open:
            self.first_critical = "detail" if self.in_details else "visible"


def inspect_html(path):
    file = Path(path)
    if not file.is_file(): return ["authored HTML file is missing"]
    if file.suffix.lower() != ".html": return ["the authored lesson must be an HTML file"]
    text = file.read_text(encoding="utf-8")
    p = PageReader()
    p.feed(text)
    problems = []
    if not p.has_html or not p.has_body or not p.has_main:
        problems.append("HTML requires html, body and main content")
    if not p.headings:
        problems.append("learning page needs one visible h1 explaining the topic")
    if not p.has_viewport:
        problems.append("missing responsive viewport meta")
    if p.main_visible_text < 110:
        problems.append("core learning explanation is absent or concealed in disclosures")
    if p.first_critical == "detail":
        problems.append("primary teaching must be visible before any optional disclosure")
    if p.script_src or p.external:
        problems.append("self-contained lesson cannot load third-party scripts/embeds")
    if any(tag in ("iframe", "object", "embed") for tag in p.tags):
        problems.append("untrusted embeds are forbidden")
    if any(img.get("src", "").lower().startswith(("javascript:", "data:text/html")) for img in p.images):
        problems.append("unsafe image source")
    for href in p.links:
        if href.lower().startswith("javascript:"):
            problems.append("unsafe javascript link")
    if "<script" in text.lower() and re.search(r"\b(?:eval\s*\(|new\s+Function\s*\()", text):
        problems.append("dynamic script evaluation is not allowed")
    # Deliberately NO fixed block count, page length target, diagram kind,
    # mandatory game, or exercise count. All are teaching decisions.
    return sorted(set(problems))


def _page_and_facts(plan, page_id):
    page = next((x for x in plan.get("pages", []) if x.get("page_id") == page_id), None)
    if page is None: raise DirectPageError("unknown page in approved route")
    points = {p["lp_id"]: p for p in plan["points"]}
    ids = page.get("lp_ids", [])
    if not ids or any(x not in points for x in ids):
        raise DirectPageError("page refers to missing LP source evidence")
    facts = {f["id"] for pid in ids for f in points[pid].get("required_facts", [])}
    return page, facts


def validate_review(workspace, plan, source, page_id):
    authored, review_path, _ = locations(workspace, page_id)
    issues = inspect_html(authored)
    if issues: raise DirectPageError("G3 invalid authored HTML: " + "; ".join(issues))
    if not review_path.is_file():
        raise DirectPageError("G4 REVIEW_PENDING: independent review of the actual HTML is missing")
    review = read(review_path)
    _, fact_ids = _page_and_facts(plan, page_id)
    checks = review.get("checks", [])
    if not isinstance(checks, list): checks = []
    expected = {
        "contract": CONTRACT, "page_id": page_id,
        "source_sha256": source["source_sha256"],
        "plan_sha256": hash_json(plan), "html_sha256": sha(authored.read_bytes()),
    }
    problems = []
    for key, val in expected.items():
        if review.get(key) != val: problems.append("stale/mismatched final review: " + key)
    if review.get("review_mode") != "isolated_host_agent":
        problems.append("independent host review must actually be delegated")
    if (not review.get("writer_context_id") or not review.get("reviewer_context_id")
            or review["writer_context_id"] == review["reviewer_context_id"]):
        problems.append("author/reviewer contexts must be distinct")
    if review.get("approved") is not True or review.get("issues"):
        problems.append("final reviewer rejected the lesson")
    if set(review.get("checked_fact_ids", [])) != fact_ids:
        problems.append("final review did not verify each required LP fact")
    if len(checks) != len(REVIEW_DIMENSIONS) or {
        x.get("dimension") for x in checks if isinstance(x, dict)
    } != REVIEW_DIMENSIONS:
        problems.append("final review must assess five educational criteria")
    for check in checks:
        if (not isinstance(check, dict) or check.get("passed") is not True
                or not str(check.get("reason", "")).strip()):
            problems.append("review verdict missing page-specific explanation")
    if problems: raise DirectPageError("G4 rejected: " + "; ".join(problems))
    return authored, review


def browser_check(path, *, check_interactions=True):
    """Run on actual authored bytes. Browsers are validators, not lesson designers."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise DirectPageError("G5 NOT_RUN: Playwright is unavailable")
    html_text = Path(path).read_text(encoding="utf-8")
    errors, viewports = [], []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for width in (390, 1280):
            tab = browser.new_page(viewport={"width": width, "height": 850})
            scripts = []
            tab.on("pageerror", lambda error: scripts.append(str(error)))
            tab.set_content(html_text, wait_until="load")
            if tab.locator("h1").count() < 1 or tab.locator("main").count() < 1:
                errors.append("missing visible page content")
            elif not tab.locator("main").is_visible():
                errors.append("main teaching content is hidden")
            if tab.evaluate("document.documentElement.scrollWidth > innerWidth + 3"):
                errors.append("horizontal overflow at " + str(width))
            if tab.locator("main").evaluate("(el)=>el.getBoundingClientRect().height") < 80:
                errors.append("insufficient main content")
            if scripts: errors.append("JS error at " + str(width) + ": " + str(scripts[:2]))
            # For genuinely interactive pages, test native disclosure and
            # keyboard access. A simple concept page needs no forced buttons.
            if check_interactions and tab.locator("details summary").count():
                summary = tab.locator("details summary").first
                summary.focus()
                tab.keyboard.press("Enter")
                if not summary.evaluate("(el)=>el.parentElement.open"):
                    errors.append("keyboard disclosure failed")
            viewports.append(width)
            tab.close()
        browser.close()
    if errors: raise DirectPageError("G5 browser QA rejected: " + "; ".join(errors))
    return {"passed": True, "browser_executed": True,
            "viewports": viewports, "html_sha256": sha(Path(path).read_bytes()),
            "test_scope": "readability, responsive overflow, JS errors, accessible native disclosure"}


def check_page(workspace, plan, source, page_id, *, require_browser=True):
    file, review = validate_review(workspace, plan, source, page_id)
    qa_path = locations(workspace, page_id)[2]
    current_hash = sha(file.read_bytes())
    qa = read(qa_path) if qa_path.is_file() else None
    if not qa or qa.get("html_sha256") != current_hash or qa.get("passed") is not True:
        if require_browser:
            qa = browser_check(file)
            save(qa_path, qa)
        else:
            qa = {"passed": False, "browser_executed": False,
                  "status": "NOT_RUN", "html_sha256": current_hash}
    return {"page_id": page_id, "file": str(file.resolve()), "sha256": current_hash,
            "reviewed": True, "browser": qa}


def prepare_standard(workspace, plan, source, page):
    w = Path(workspace)
    result = check_page(w, plan, source, page["page_id"])
    output = w / "published" / (page["page_id"] + ".html")
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(result["file"], output)
    return {**result, "file": str(output.resolve()), "sha256": sha(output.read_bytes())}


def prepare_deep(workspace, plan, source, host):
    """Stage exactly the next approved deep page, never rewriting delivered pages."""
    w = Path(workspace)
    if plan.get("mode") != "study-d" or plan.get("render_contract") != CONTRACT:
        raise DirectPageError("direct deep staging requires direct-html-v1 Study-D")
    if not (w / "frozen-plan.json").is_file():
        raise DirectPageError("frozen plan required")
    if hash_json(read(w / "plan.json")) != hash_json(plan):
        raise DirectPageError("plan has changed after approval")
    approved = read(w / "reviews" / "plan-review.json")
    owner = read(w / "owner-outline-approval.json")
    digest = hash_json(plan)
    if approved.get("approved") is not True or approved.get("plan_sha256") != digest:
        raise DirectPageError("independently approved current plan required")
    if owner.get("approved") is not True or owner.get("plan_sha256") != digest:
        raise DirectPageError("explicit Study-D outline approval required")
    ledger_path = w / "reports" / "page-receipts.json"
    ledger = read(ledger_path) if ledger_path.is_file() else {
        "source_sha256": source["source_sha256"], "plan_sha256": digest, "pages": []}
    if (ledger.get("source_sha256") != source["source_sha256"]
            or ledger.get("plan_sha256") != digest):
        raise DirectPageError("staged page ledger does not match the approved source")
    queue_path = w / "delivery-queue.json"
    queue = read(queue_path) if queue_path.is_file() else {
        "cursor": 0, "files": ["index.html"], "one_link_per_turn": True}
    if queue.get("cursor", 0) < len(queue["files"]) and ledger["pages"]:
        raise DirectPageError("previous staged page still awaits confirmed delivery")
    index = len(ledger["pages"])
    if index >= len(plan["pages"]):
        return {"finished_authoring": True, "pages": index}
    page = plan["pages"][index]
    result = check_page(w, plan, source, page["page_id"])
    output_dir = w / "published"
    output_dir.mkdir(parents=True, exist_ok=True)
    result_file = output_dir / (page["page_id"] + ".html")
    shutil.copy2(result["file"], result_file)
    # Index is generated from approved plan, not from the teaching content.
    index_parts = ["<!doctype html><html lang='zh-CN'><meta charset='utf-8'>",
                   "<meta name='viewport' content='width=device-width,initial-scale=1'>",
                   "<title>Study-D · 课程导航</title><main><h1>Study-D · 课程导航</h1>"]
    for i, item in enumerate(plan["pages"]):
        label = html.escape(item.get("title", item["page_id"]))
        if i <= index:
            index_parts.append(f"<p><a href='{item['page_id']}.html'>{label}</a></p>")
        else:
            index_parts.append(f"<p>{label}（待学习）</p>")
    index_parts.append("</main></html>")
    (output_dir / "index.html").write_bytes("".join(index_parts).encode("utf-8"))
    ledger["pages"].append({
        "page_id": page["page_id"], "file": result_file.name,
        "lp_ids": page["lp_ids"], "html_sha256": result["sha256"],
        "review_contract": CONTRACT})
    save(ledger_path, ledger)
    queue["files"].append(result_file.name)
    save(queue_path, queue)
    state = host.state(w)
    for gate in ("G3_CONTENT", "G4_REVIEW", "G5_BROWSER"):
        state.setdefault("gates", {})[gate] = {
            "ok": index + 1 == len(plan["pages"]),
            "status": "ACCEPTED" if index + 1 == len(plan["pages"]) else "PARTIAL_VERIFIED",
            "issues": [], "evidence": str(ledger_path)}
        state.setdefault("verification", {})[gate] = state["gates"][gate]["status"]
    state.setdefault("gates", {})["G6_DELIVERY"] = {
        "ok": False, "status": "PREPARED", "issues": [],
        "evidence": str(queue_path)}
    state.setdefault("verification", {})["G6_DELIVERY"] = "PREPARED"
    host.save(w, state)
    return {"page_id": page["page_id"], "file": str(result_file.resolve()),
            "reviewed": True, "browser_pass": True, "pages_staged": index + 1,
            "total_pages": len(plan["pages"]), "awaiting_delivery_confirmation": True,
            "sha256": result["sha256"]}
