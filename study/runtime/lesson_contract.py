"""Study V6.4 — validated pre-render lesson-design and review contract.

The connected Codex/DSH host writes the design and delegates the independent
review. This module is deterministic: it never calls a language model.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

SCHEMA = "lesson-design-v1"
KINDS = {"concept", "mechanism", "algorithm", "math", "experiment",
         "failure_case", "comparison", "decision"}
VISUALS = {"text", "process", "decision", "comparison", "experiment",
           "timeline", "math", "concept_map"}
MOVE_KINDS = {"intuition", "mechanism", "worked_example", "boundary"}
CHECKS = {"objective", "causal_explanation", "visual_fit", "example",
          "checkpoint_transfer", "source_fidelity"}


class LessonContractError(ValueError):
    pass


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def meaningful(value, minimum=12):
    return isinstance(value, str) and len(" ".join(value.split())) >= minimum


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def design_paths(workspace, page_id):
    root = Path(workspace)
    return (root / "lesson-specs" / (page_id + ".json"),
            root / "reviews" / "design" / (page_id + ".json"))


def validate_spec(spec, page, points, source):
    """A planning check, not a semantic accuracy claim."""
    problems = []
    if not isinstance(spec, dict):
        return ["lesson specification must be a JSON object"]
    pid = page.get("page_id")
    if spec.get("schema_version") != SCHEMA:
        problems.append("lesson specification requires schema_version=lesson-design-v1")
    if spec.get("page_id") != pid:
        problems.append("lesson specification page_id differs from approved plan")
    lp_ids = set(page.get("lp_ids", []))
    if (not isinstance(spec.get("lp_ids"), list) or
            len(spec["lp_ids"]) != len(lp_ids) or set(spec["lp_ids"]) != lp_ids):
        problems.append("lesson specification LP set must match page exactly")
    kind = spec.get("lesson_kind")
    if kind not in KINDS:
        problems.append("lesson_kind must identify a supported teaching form")
    for key in ("objective", "central_question", "insight", "misconception"):
        if not meaningful(spec.get(key), 14):
            problems.append("lesson specification lacks a concrete " + key)
    source_fact_ids = {f["id"] for p in points for f in p.get("required_facts", [])}
    declared = spec.get("source_fact_ids", [])
    if not isinstance(declared, list) or set(declared) != source_fact_ids:
        problems.append("lesson specification must reference all and only page facts")
    if len(declared) != len(set(declared)):
        problems.append("lesson specification repeats fact IDs")
    moves = spec.get("teaching_moves")
    if not isinstance(moves, list):
        problems.append("teaching_moves must be a list")
        moves = []
    actual = [m.get("kind") for m in moves if isinstance(m, dict)]
    if (len(moves) != 4 or set(actual) != MOVE_KINDS or
            len(set(actual)) != len(actual)):
        problems.append("teach intuition, causal mechanism, worked example and boundary once each")
    covered = set()
    for m in moves:
        if not isinstance(m, dict):
            problems.append("malformed teaching move")
            continue
        if not meaningful(m.get("focus"), 15):
            problems.append("teaching move needs a concrete learning purpose")
        refs = m.get("fact_ids", [])
        if not isinstance(refs, list) or set(refs)-source_fact_ids:
            problems.append("teaching move refers to unapproved source facts")
        covered.update(refs if isinstance(refs, list) else [])
    if covered != source_fact_ids:
        problems.append("teaching moves do not account for every required fact")
    visual = spec.get("visual")
    if not isinstance(visual, dict):
        problems.append("explicit teaching visual decision required")
        visual = {}
    vkind = visual.get("kind")
    if vkind not in VISUALS:
        problems.append("visual.kind must be a supported meaningful representation")
    if not meaningful(visual.get("purpose"), 20):
        problems.append("visual.purpose must explain what relationship the visual teaches")
    if kind in {"mechanism","algorithm","math","experiment","failure_case"} and vkind == "text":
        problems.append("complex mechanism/experiment/failure lesson needs a causal representation")
    if vkind in {"process", "decision", "timeline", "concept_map"}:
        nodes = visual.get("nodes", [])
        edges = visual.get("edges", [])
        if not isinstance(nodes, list) or len(nodes) < 2:
            problems.append("visual needs at least two informative nodes")
            nodes = []
        ids = [x.get("id") for x in nodes if isinstance(x, dict)]
        if len(ids) != len(nodes) or len(set(ids)) != len(ids):
            problems.append("visual node IDs invalid or repeated")
        for n in nodes:
            if not isinstance(n,dict) or not meaningful(n.get("label"),2) or not meaningful(n.get("meaning"),12):
                problems.append("visual node lacks explanatory meaning")
        if not isinstance(edges,list) or not edges:
            problems.append("visual requires labelled relationships")
        else:
            for e in edges:
                if (not isinstance(e,dict) or e.get("from") not in ids or
                    e.get("to") not in ids or not meaningful(e.get("label"),4)):
                    problems.append("visual edge must connect valid nodes and explain relationship")
        if vkind == "timeline" and visual.get("first_error_id") not in ids:
            problems.append("failure timeline must identify the first wrong step")
    if vkind in {"comparison", "experiment"}:
        columns, rows = visual.get("columns"), visual.get("rows")
        if (not isinstance(columns,list) or len(columns)<2 or
            not isinstance(rows,list) or len(rows)<2 or
            any(not isinstance(row,list) or len(row)!=len(columns) for row in rows)):
            problems.append("comparison/experiment requires comparable columns and at least two rows")
    if vkind == "math":
        if not meaningful(visual.get("formula"),5) or not isinstance(visual.get("variables"),dict) or len(visual["variables"])<1:
            problems.append("math visual needs formula and variable meanings")
    checkpoint = spec.get("checkpoint")
    if not isinstance(checkpoint,dict):
        problems.append("lesson checkpoint specification missing")
        checkpoint = {}
    for key in ("question","changed_condition","expected_reasoning","rubric"):
        if not meaningful(checkpoint.get(key),18):
            problems.append("checkpoint needs a concrete "+key)
    check_facts = checkpoint.get("fact_ids", [])
    if not isinstance(check_facts,list) or not set(check_facts).issubset(source_fact_ids) or not check_facts:
        problems.append("checkpoint must target verifiable source facts")
    if kind=="experiment" and vkind=="experiment":
        if not meaningful(visual.get("data_provenance"),18):
            problems.append("experiment diagram must identify actual data source or explicitly mark fictional example")
    # Avoid hardcoded page count / visual counts as a proxy for learning quality.
    return sorted(set(problems))


def validate_design_review(review, spec, page, points, source, plan_hash):
    """Reject a forged-shaped/obsolete review; true independence is host enforced."""
    errors = []
    if not isinstance(review,dict):
        return ["independent lesson-design review missing"]
    if review.get("review_mode") != "isolated_host_agent":
        errors.append("real isolated reviewer context required")
    author, reviewer=review.get("writer_context_id"), review.get("reviewer_context_id")
    if not reviewer or not author or author==reviewer:
        errors.append("reviewer must differ from lesson author context")
    if review.get("contract") != SCHEMA:
        errors.append("design review contract mismatch")
    if review.get("page_id") != page.get("page_id"):
        errors.append("design review page identity mismatch")
    if review.get("plan_sha256") != plan_hash:
        errors.append("design review plan changed")
    if review.get("source_sha256") != source.get("source_sha256"):
        errors.append("design review source changed")
    if review.get("lesson_spec_sha256") != digest(spec):
        errors.append("design review is stale after lesson specification changed")
    if review.get("approved") is not True or review.get("issues"):
        errors.append("design review rejected")
    facts={f["id"] for p in points for f in p["required_facts"]}
    if set(review.get("checked_fact_ids", [])) != facts:
        errors.append("design reviewer did not inspect all page facts")
    checks=review.get("checks",[])
    if not isinstance(checks,list):
        checks=[]
    if len(checks)!=len(CHECKS) or {a.get("dimension") for a in checks if isinstance(a,dict)}!=CHECKS:
        errors.append("design review must cover all six quality dimensions")
    for item in checks:
        if not isinstance(item,dict) or item.get("passed") is not True or not meaningful(item.get("reason"),32):
            errors.append("design reviewer must give specific explanation for each dimension")
    return sorted(set(errors))


def verify_ready(workspace, plan, page, source, points):
    """Return (spec, digest) after both design and review; fail closed."""
    spec_path, review_path=design_paths(workspace,page["page_id"])
    if not spec_path.is_file():
        raise LessonContractError("missing Lesson Specification: "+str(spec_path))
    spec=read(spec_path)
    errors=validate_spec(spec,page,points,source)
    if errors:
        raise LessonContractError("G3 lesson design invalid: "+"; ".join(errors[:12]))
    if not review_path.is_file():
        raise LessonContractError("missing independent lesson-design review: "+str(review_path))
    review=read(review_path)
    errors=validate_design_review(review,spec,page,points,source,digest(plan))
    if errors:
        raise LessonContractError("G3 lesson design review invalid: "+"; ".join(errors[:12]))
    return spec,digest(spec)


def validate_draft_alignment(spec, draft):
    issues=[]
    if draft.get("checkpoint",{}).get("question") != spec.get("checkpoint",{}).get("question"):
        issues.append("rendered checkpoint must match reviewed transfer question")
    if not set(spec.get("lp_ids",[])).issubset({r.get("lp_id") for r in draft.get("teaching_evidence",[]) if isinstance(r,dict)}):
        issues.append("draft misses design-specified LP teaching")
    if draft.get("lesson_kind") and draft["lesson_kind"] != spec["lesson_kind"]:
        issues.append("draft lesson kind differs from approved teaching design")
    return issues
