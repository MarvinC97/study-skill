"""V6.2 deep-study quality contracts.

Deterministic checks establish traceability and reject obvious under-splitting
and shallow content. Semantic sufficiency still requires a genuine isolated
host reviewer; a JSON receipt alone cannot prove a reviewer actually read it.
"""
from __future__ import annotations
import re
import hashlib
import json

ATOMIC_KINDS={"concept","mechanism","decision","algorithm","comparison",
              "experiment","failure_case","boundary","reflection"}
REVIEW_DIMENSIONS=("mechanism","causal_reasoning","worked_example",
                   "conditions_and_limits","assessment_fairness","source_fidelity")
EXPERIMENT_FACETS=("purpose","setup","controls","results","limitations")


def clean(value):
    return re.sub(r"\s+"," ",value).strip() if isinstance(value,str) else ""


def substantial(value,minimum=32):
    return len(clean(value))>=minimum


def source_contains(source,quote):
    # A short section heading may be the entire span; require the whole quote
    # rather than demanding more characters than the original source contains.
    original=clean(source);excerpt=clean(quote)
    return len(excerpt)>=min(12,len(original)) and excerpt in original


def experiment_markers(source):
    # Author's quoted experiment headings, not incidental prose references.
    return set(re.findall(r"(?m)^\s*>\s*\*\*\s*实验\s*(\d+\s*[-–]\s*\d+)",source))


def reflection_numbers(source):
    section=re.split(r"(?m)^#{2,3}\s*思考题\s*$",source,maxsplit=1)
    if len(section)<2:return set()
    text=re.split(r"(?m)^#{1,2}\s+",section[1],maxsplit=1)[0]
    return {int(x) for x in re.findall(r"(?m)^\s*(\d{1,2})[.、]\s+\S",text)}


def validate_deep_inventory(source,plan):
    if plan.get("mode")!="study-d":return []
    issues=[];spans={x["id"]:x for x in source.get("segments",[])}
    points={p.get("lp_id"):p for p in plan.get("points",[])}
    items=plan.get("source_inventory")
    if not isinstance(items,list) or not items:
        return ["G2 missing full atomic source_inventory"]
    ids=set();mapping={};exp_items=set()
    for item in items:
        if not isinstance(item,dict):
            issues.append("G2 malformed inventory item");continue
        iid=item.get("id");sid=item.get("span_id");kind=item.get("kind")
        if not iid or iid in ids:issues.append("G2 duplicate/missing inventory ID "+str(iid));continue
        ids.add(iid);mapping[iid]=item
        if sid not in spans:issues.append(iid+" unknown source span");continue
        if kind not in ATOMIC_KINDS:issues.append(iid+" invalid atomic kind")
        if not substantial(item.get("title"),5) or not substantial(item.get("objective"),15):
            issues.append(iid+" lacks focused title and observable objective")
        if not source_contains(spans[sid]["text"],item.get("source_quote")):
            issues.append(iid+" lacks an exact, substantial source quote")
        if kind=="experiment":
            marker=clean(item.get("experiment_id")).replace("–","-").replace(" ","")
            if not marker:issues.append(iid+" experiment_id missing")
            else:exp_items.add(marker)
    used=[]
    for point in plan.get("points",[]):
        pid=point.get("lp_id")
        refs=point.get("inventory_ids")
        if not isinstance(refs,list) or len(refs)!=1:
            issues.append(str(pid)+" contains zero or multiple independent inventory items; split into atomic LPs")
            continue
        iid=refs[0];used.append(iid)
        if iid not in mapping:issues.append(str(pid)+" references unknown atomic inventory item "+str(iid))
        elif mapping[iid].get("span_id") not in point.get("source_span_ids",[]):
            issues.append(str(pid)+" inventory item is disconnected from LP source span")
        if iid in mapping and point.get("kind")!=mapping[iid].get("kind"):
            issues.append(str(pid)+" LP kind disagrees with atomic inventory kind; experiments require experiment review")
        for fact in point.get("required_facts",[]):
            sid=fact.get("span_id")
            if sid not in spans or not source_contains(spans[sid]["text"],fact.get("source_quote")):
                issues.append(str(pid)+" fact "+str(fact.get("id"))+" lacks an exact source evidence quote")
    if ids!=set(used):
        issues.append("G2 inventory-to-LP coverage mismatch; missing="+str(sorted(ids-set(used)))+
                      " repeated="+str(sorted({x for x in used if used.count(x)>1})))
    referenced_spans={i.get("span_id") for i in items if isinstance(i,dict)}
    if set(spans)-referenced_spans:
        issues.append("G2 source spans lack atomic inventory: "+str(sorted(set(spans)-referenced_spans)))
    markers={m.replace("–","-").replace(" ","") for m in experiment_markers(source.get("text",""))}
    if markers-exp_items:
        issues.append("G2 experiments omitted from atomic inventory: "+str(sorted(markers-exp_items)))
    coverage=plan.get("experiment_coverage",[])
    bymarker={}
    for item in coverage if isinstance(coverage,list) else []:
        marker=clean(item.get("experiment_id")).replace("–","-").replace(" ","")
        if marker in bymarker:issues.append("G2 duplicate experiment coverage "+marker)
        bymarker[marker]=item
        if not item.get("lp_ids") or not set(item.get("lp_ids",[])).issubset(points):
            issues.append("G2 invalid experiment LP mapping "+marker)
        else:
            if not any(points[lp].get("kind")=="experiment" and any(
                 inventory.get("id") in points[lp].get("inventory_ids",[]) and
                 clean(inventory.get("experiment_id")).replace("–","-").replace(" ","")==marker
                 for inventory in items if isinstance(inventory,dict)) for lp in item["lp_ids"]):
                issues.append("G2 experiment register must map to an experiment-specific atomic LP "+marker)
        facets=item.get("facets",{})
        for facet in EXPERIMENT_FACETS:
            d=facets.get(facet,{})
            if d.get("status")=="source_provided":
                quotes=d.get("source_quotes",[])
                if not isinstance(quotes,list) or not quotes or not all(
                    any(source_contains(sp["text"],q) for sp in spans.values()) for q in quotes):
                    issues.append("G2 unsupported experiment facet "+marker+"/"+facet)
            elif d.get("status")=="not_in_source":
                if not substantial(d.get("reason"),18):
                    issues.append("G2 unsubstantiated source gap "+marker+"/"+facet)
            else:issues.append("G2 experiment facet unreviewed "+marker+"/"+facet)
    if markers!=set(bymarker):
        issues.append("G2 experiment register differs from source headings: "+str(sorted(markers^set(bymarker))))
    reflections=reflection_numbers(source.get("text",""))
    mapping=plan.get("reflection_coverage",[])
    bynum={}
    for item in mapping if isinstance(mapping,list) else []:
        number=item.get("number")
        if number in bynum:issues.append("G2 duplicate reflection "+str(number))
        bynum[number]=item
        if not item.get("lp_ids") or not set(item.get("lp_ids",[])).issubset(points):
            issues.append("G2 reflection lacks valid teaching LP "+str(number))
        if not substantial(item.get("assessment_plan"),20):
            issues.append("G2 reflection lacks assessment mapping "+str(number))
    if reflections!=set(bynum):
        issues.append("G2 reflection question coverage mismatch: "+str(sorted(reflections^set(bynum))))
    return issues


def validate_authored_teaching(points,draft):
    issues=[]
    if not isinstance(draft,dict):return ["G3 draft must be a JSON object"]
    records=draft.get("teaching_evidence")
    if not isinstance(records,list):
        issues.append("G3 missing authored teaching_evidence; source callouts cannot substitute")
        records=[]
    byid={p["lp_id"]:p for p in points}
    shared=draft.get("shared_teaching") if len(points)>1 else None
    if shared is not None:
        if not isinstance(shared,dict) or set(shared.get("lp_ids",[]))!=set(byid):
            issues.append("G3 shared teaching must cover exactly the grouped LPs")
            shared=None
    seen=set()
    for record in records:
        if not isinstance(record,dict):
            issues.append("G3 malformed teaching record");continue
        pid=record.get("lp_id")
        if pid not in byid or pid in seen:
            issues.append("G3 unknown/repeated teaching LP "+str(pid));continue
        seen.add(pid)
        base=shared or record
        if shared and not substantial(record.get("lp_connection"),70):
            issues.append("G3 "+pid+" lacks an authored connection to the shared lesson")
        if not substantial(base.get("core_explanation"),120):
            issues.append("G3 "+pid+" core explanation too shallow")
        steps=base.get("causal_steps",[])
        if (not isinstance(steps,list) or len(steps)<2 or
            any(not substantial(x,35) for x in steps) or
            len(set(map(clean,steps)))!=len(steps)):
            issues.append("G3 "+pid+" lacks distinct, explained causal steps")
        worked=base.get("worked_example",{})
        if not isinstance(worked,dict):worked={}
        for key,minimum in (("scenario",40),("input",25),("outcome",30),("why",65)):
            if not substantial(worked.get(key),minimum):
                issues.append("G3 "+pid+" incomplete worked example: "+key)
        example_steps=worked.get("reasoning_steps",[])
        if not isinstance(example_steps,list) or len(example_steps)<2 or any(
                not substantial(x,28) for x in example_steps):
            issues.append("G3 "+pid+" lacks step-by-step example reasoning")
        for key in ("conditions","limitations"):
            blocks=base.get(key,[])
            if not isinstance(blocks,list) or not blocks or any(
                    not substantial(x,30) for x in blocks):
                issues.append("G3 "+pid+" missing meaningful "+key)
        facts=byid[pid].get("required_facts",[])
        details=record.get("fact_explanations",[])
        if not isinstance(details,list):details=[]
        IDs=[x.get("fact_id") for x in details if isinstance(x,dict)]
        if len(IDs)!=len(set(IDs)) or set(IDs)!={f["id"] for f in facts}:
            issues.append("G3 "+pid+" lacks one original explanation per source fact")
        for entry in details:
            if not isinstance(entry,dict):continue
            f=next((f for f in facts if f["id"]==entry.get("fact_id")),None)
            if f is None:continue
            value=clean(entry.get("explanation"))
            if not substantial(value,75):
                issues.append("G3 "+pid+" fact "+f["id"]+" explanation too short")
            if value==clean(f.get("text")):
                issues.append("G3 "+pid+" fact "+f["id"]+" merely repeats source")
        if byid[pid].get("kind")=="experiment":
            experiment=record.get("experiment",{})
            for key in EXPERIMENT_FACETS:
                if not substantial(experiment.get(key) if isinstance(experiment,dict) else "",55):
                    issues.append("G3 "+pid+" experimental method/result missing: "+key)
    if seen!=set(byid):issues.append("G3 missing LP teaching records "+str(sorted(set(byid)-seen)))
    if not substantial(draft.get("checkpoint",{}).get("rubric"),35):
        issues.append("G3 checkpoint requires reasoning rubric, beyond answer key")
    return issues


def shared_teaching_texts(record):
    texts=[clean(record.get("core_explanation"))]
    for field in ("causal_steps","conditions","limitations"):
        texts.extend(clean(x) for x in record.get(field,[]) if isinstance(x,str))
    ex=record.get("worked_example",{})
    if isinstance(ex,dict):
        texts.extend(clean(ex.get(key)) for key in ("scenario","input","outcome","why"))
        texts.extend(clean(x) for x in ex.get("reasoning_steps",[]) if isinstance(x,str))
    return texts


def authored_text(draft):
    """Only tutor-authored explanations; excludes automatic rendered source callouts."""
    texts=[clean(draft.get("intro"))]
    shared=draft.get("shared_teaching")
    if isinstance(shared,dict):texts.extend(shared_teaching_texts(shared))
    for section in draft.get("sections",[]):
        if isinstance(section,dict):texts.append(clean(section.get("text")))
    for item in draft.get("teaching_evidence",[]):
        if not isinstance(item,dict):continue
        texts.append(clean(item.get("core_explanation")))
        texts.append(clean(item.get("lp_connection")))
        for key in ("causal_steps","conditions","limitations"):
            texts.extend(clean(x) for x in item.get(key,[]) if isinstance(x,str))
        ex=item.get("worked_example",{})
        if isinstance(ex,dict):
            texts.extend(clean(ex.get(k)) for k in ("scenario","input","outcome","why"))
            texts.extend(clean(x) for x in ex.get("reasoning_steps",[]) if isinstance(x,str))
        for f in item.get("fact_explanations",[]):
            if isinstance(f,dict):texts.append(clean(f.get("explanation")))
        exp=item.get("experiment",{})
        if isinstance(exp,dict):texts.extend(clean(exp.get(k)) for k in EXPERIMENT_FACETS)
    return texts


def dimension_text(draft,dimension):
    """Reviewer quotation must come from the type of teaching it assesses."""
    records=[x for x in draft.get("teaching_evidence",[]) if isinstance(x,dict)]
    shared=draft.get("shared_teaching")
    if isinstance(shared,dict):records=[shared]+records
    if dimension=="assessment_fairness":
        ck=draft.get("checkpoint",{})
        return [clean(ck.get("rubric"))] if isinstance(ck,dict) else []
    texts=[]
    for record in records:
        if dimension=="mechanism":texts.append(clean(record.get("core_explanation")))
        elif dimension=="causal_reasoning":
            texts.extend(clean(x) for x in record.get("causal_steps",[]) if isinstance(x,str))
        elif dimension=="worked_example":
            ex=record.get("worked_example",{})
            if isinstance(ex,dict):
                texts.extend(clean(ex.get(k)) for k in ("scenario","input","outcome","why"))
                texts.extend(clean(x) for x in ex.get("reasoning_steps",[]) if isinstance(x,str))
        elif dimension=="conditions_and_limits":
            for k in ("conditions","limitations"):
                texts.extend(clean(x) for x in record.get(k,[]) if isinstance(x,str))
        elif dimension=="source_fidelity":
            texts.extend(clean(x.get("explanation")) for x in record.get("fact_explanations",[]) if isinstance(x,dict))
        elif dimension=="experiment_methods":
            ex=record.get("experiment",{})
            if isinstance(ex,dict):
                texts.extend(clean(ex.get(k)) for k in EXPERIMENT_FACETS)
    return texts


def scoped_digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode("utf-8")).hexdigest()


def review_batch_scope(source,plan,lp_ids):
    """Stable across unrelated page edits; source and LP content changes invalidate."""
    by_lp={p["lp_id"]:p for p in plan["points"]}
    inventory={x["id"]:x for x in plan.get("source_inventory",[])}
    spans={x["id"]:x for x in source["segments"]}
    return scoped_digest({
        "source_sha256":source["source_sha256"],
        "learning_points":[by_lp[x] for x in sorted(lp_ids)],
        "inventory":[inventory[i] for x in sorted(lp_ids)
                     for i in by_lp[x].get("inventory_ids",[])],
        "source_spans":[spans[i] for i in sorted({
            sid for x in lp_ids for sid in by_lp[x].get("source_span_ids",[])})]
    })


def review_page_scope(source,plan,page):
    by_lp={p["lp_id"]:p for p in plan["points"]}
    return scoped_digest({"source_sha256":source["source_sha256"],
        "page":page,"points":[by_lp[x] for x in page.get("lp_ids",[])]})


def validate_batch_plan_review(review,source,plan,cache=None):
    """Efficient G2: full deterministic coverage, bounded review batches and
    focused scrutiny only for risky LPs/combined pages.
    Verified hashes enable safe reuse of unchanged reviewer work.
    """
    issues=[];cache=cache or {"batches":{},"pages":{}}
    by_lp={p["lp_id"]:p for p in plan["points"]}
    pages={p["page_id"]:p for p in plan["pages"]}
    included=[];seen_scopes=[]
    supplied=review.get("batch_audits",[])
    if not isinstance(supplied,list):supplied=[]
    for audit in supplied:
        if not isinstance(audit,dict):issues.append("G2 malformed review batch");continue
        ids=audit.get("lp_ids",[])
        if not isinstance(ids,list) or not ids or len(ids)>12 or len(set(ids))!=len(ids) or set(ids)-set(by_lp):
            issues.append("G2 invalid or oversized review batch");continue
        digest=review_batch_scope(source,plan,ids)
        if audit.get("scope_sha256")!=digest or audit.get("approved") is not True or audit.get("issues"):
            issues.append("G2 failed/stale batch review "+str(audit.get("batch_id")));continue
        if not substantial(audit.get("reason"),45):
            issues.append("G2 review batch needs a substantive explanation")
        included.extend(ids);seen_scopes.append(digest)
    reusable=review.get("reuse_batch_sha256",[])
    if not isinstance(reusable,list):reusable=[]
    for d in reusable:
        item=cache.get("batches",{}).get(d)
        if not isinstance(item,dict) or item.get("scope_sha256")!=d or not item.get("lp_ids"):
            issues.append("G2 batch reuse has no previously accepted matching receipt");continue
        ids=item["lp_ids"]
        if not set(ids).issubset(by_lp) or review_batch_scope(source,plan,ids)!=d:
            issues.append("G2 cached batch is stale");continue
        included.extend(ids);seen_scopes.append(d)
    if len(included)!=len(set(included)) or set(included)!=set(by_lp):
        issues.append("G2 review batches must cover each LP exactly once")
    if len(seen_scopes)!=len(set(seen_scopes)):
        issues.append("G2 review batch receipt duplicated")
    risk={p["lp_id"] for p in plan["points"] if p.get("kind") in
          ("algorithm","experiment","failure_case","boundary")}
    audits=review.get("risk_audits",[])
    if not isinstance(audits,list):audits=[]
    if {a.get("lp_id") for a in audits if isinstance(a,dict)}!=risk or len(audits)!=len(risk):
        issues.append("G2 risk LP audits incomplete: "+str(sorted(risk)))
    for a in audits:
        if not isinstance(a,dict):continue
        if a.get("needs_split") is True or a.get("atomic") is not True or not substantial(a.get("reason"),45):
            issues.append("G2 unresolved risky LP atomicity "+str(a.get("lp_id")))
    grouped={p["page_id"]:p for p in plan["pages"] if len(p["lp_ids"])>1}
    audit_pages=review.get("page_audits",[])
    if not isinstance(audit_pages,list):audit_pages=[]
    reviewed_pages={}
    for a in audit_pages:
        if not isinstance(a,dict):issues.append("G2 malformed grouped-page audit");continue
        pid=a.get("page_id")
        if pid not in grouped or pid in reviewed_pages:
            issues.append("G2 invalid/duplicate grouped page "+str(pid));continue
        page=grouped[pid];d=review_page_scope(source,plan,page)
        if a.get("scope_sha256")!=d or a.get("coherent") is not True or a.get("needs_split") is not False or not substantial(a.get("reason"),45):
            issues.append("G2 grouped-page coherence audit failed "+str(pid))
        reviewed_pages[pid]=d
    reuse_pages=review.get("reuse_page_sha256",[])
    if not isinstance(reuse_pages,list):reuse_pages=[]
    for d in reuse_pages:
        a=cache.get("pages",{}).get(d)
        if not isinstance(a,dict):issues.append("G2 grouped page reuse missing");continue
        pid=a.get("page_id")
        if pid not in grouped or review_page_scope(source,plan,grouped[pid])!=d or pid in reviewed_pages:
            issues.append("G2 grouped page reuse stale/duplicate "+str(pid));continue
        reviewed_pages[pid]=d
    if set(reviewed_pages)!=set(grouped):
        issues.append("G2 all grouped pages need independent coherence checks")
    markers={m.replace("–","-").replace(" ","") for m in experiment_markers(source.get("text",""))}
    if set(review.get("experiment_ids_checked",[]))!=markers:
        issues.append("G2 experiment register review incomplete")
    reflections=reflection_numbers(source.get("text",""))
    if set(review.get("reflection_numbers_checked",[]))!=reflections:
        issues.append("G2 reflection register review incomplete")
    inventory={x["id"] for x in plan.get("source_inventory",[])}
    if set(review.get("checked_inventory_ids",[]))!=inventory:
        issues.append("G2 inventory ID review incomplete")
    return issues


def validate_plan_review_audits(review,source,plan,cache=None):
    if plan.get("mode")!="study-d":return []
    if review.get("review_contract")=="g2-batched-v3":
        return validate_batch_plan_review(review,source,plan,cache)
    if any(len(page.get("lp_ids",[]))>1 for page in plan.get("pages",[])):
        return ["G2 grouped Study-D pages require batched-v3 page coherence review"]
    issues=[];inventory=plan.get("source_inventory",[]);points=plan.get("points",[])
    inv={x["id"] for x in inventory if isinstance(x,dict) and x.get("id")}
    pointids={p["lp_id"] for p in points}
    audits=review.get("atomicity_audits",[])
    if not isinstance(audits,list) or {x.get("lp_id") for x in audits if isinstance(x,dict)}!=pointids or len(audits)!=len(pointids):
        issues.append("G2 independent atomicity verdict missing for one or more LPs")
    for a in audits if isinstance(audits,list) else []:
        if (a.get("atomic") is not True or a.get("needs_split") is not False or
            not substantial(a.get("reason"),50)):
            issues.append("G2 LP has no substantiated independent atomicity approval "+str(a.get("lp_id")))
    per_span=review.get("span_audits",[])
    if (not isinstance(per_span,list) or len(per_span)!=len(source.get("segments",[])) or
        {x.get("span_id") for x in per_span if isinstance(x,dict)}!={x["id"] for x in source.get("segments",[])}):
        issues.append("G2 independent source span semantic audit incomplete")
    for a in per_span if isinstance(per_span,list) else []:
        if (a.get("complete") is not True or a.get("missing_inventory_ids") or
            not substantial(a.get("reason"),45)):
            issues.append("G2 source span inventory has unreviewed omissions "+str(a.get("span_id")))
    reviewed=set(review.get("checked_inventory_ids",[]))
    if reviewed!=inv:issues.append("G2 reviewer did not check every atomic inventory item")
    markers={m.replace("–","-").replace(" ","") for m in experiment_markers(source.get("text",""))}
    em=review.get("experiment_audits",[])
    if len(em)!=len(markers) or {x.get("experiment_id") for x in em}!=markers or any(
            x.get("complete") is not True or not substantial(x.get("reason"),35) for x in em):
        issues.append("G2 experiment design/results/limits not independently reviewed")
    reflection=reflection_numbers(source.get("text",""))
    rm=review.get("reflection_audits",[])
    if len(rm)!=len(reflection) or {x.get("number") for x in rm}!=reflection or any(
            x.get("mapped") is not True or not substantial(x.get("reason"),35) for x in rm):
        issues.append("G2 reflection exercises not independently mapped")
    return issues


def validate_compact_content_review(entry,points,draft,source):
    """A short source/fact ledger plus one substantive review per dimension.
    Risky cases still require their own focused reviewer explanation.
    """
    issues=[];spans={x["id"]:x for x in source.get("segments",[])}
    factmap={f["id"]:f for p in points for f in p.get("required_facts",[])}
    authored={}
    for record in draft.get("teaching_evidence",[]):
        if not isinstance(record,dict):continue
        for item in record.get("fact_explanations",[]):
            if isinstance(item,dict):authored[item.get("fact_id")]=clean(item.get("explanation"))
    checks=entry.get("fact_checks",[])
    if not isinstance(checks,list):checks=[]
    if len(checks)!=len(factmap) or {a.get("fact_id") for a in checks if isinstance(a,dict)}!=set(factmap):
        issues.append("G4 compact source/fact audit incomplete")
    for check in checks:
        if not isinstance(check,dict):continue
        fid=check.get("fact_id")
        if fid not in factmap:continue
        f=factmap[fid];sid=f.get("span_id")
        if (check.get("grounded") is not True or check.get("explained") is not True or
            check.get("source_span_id")!=sid or sid not in spans or
            clean(check.get("source_quote"))!=clean(f.get("source_quote")) or
            not source_contains(spans[sid]["text"],check.get("source_quote"))):
            issues.append("G4 source fidelity failed for "+fid)
        quote=clean(check.get("draft_quote"))
        if not substantial(quote,35) or quote not in authored.get(fid,""):
            issues.append("G4 missing tutor-authored fact evidence for "+fid)
    dimensions=entry.get("quality_dimensions",[])
    needed=set(REVIEW_DIMENSIONS)
    if any(p.get("kind")=="experiment" for p in points):needed.add("experiment_methods")
    if not isinstance(dimensions,list):dimensions=[]
    if len(dimensions)!=len(needed) or {d.get("dimension") for d in dimensions if isinstance(d,dict)}!=needed:
        issues.append("G4 compact pedagogical dimension review incomplete")
    for a in dimensions:
        if not isinstance(a,dict):continue
        quote=clean(a.get("draft_quote"))
        if (a.get("passed") is not True or not substantial(a.get("reason"),45) or
            not substantial(quote,35) or
            not any(quote in x for x in dimension_text(draft,a.get("dimension")))):
            issues.append("G4 weak dimension audit "+str(a.get("dimension")))
    risky={p["lp_id"] for p in points if p.get("kind") in
           ("experiment","algorithm","failure_case","boundary")}
    audits=entry.get("risk_audits",[])
    if not isinstance(audits,list):audits=[]
    if len(audits)!=len(risky) or {a.get("lp_id") for a in audits if isinstance(a,dict)}!=risky:
        issues.append("G4 risk-specific semantic review missing")
    for a in audits:
        if not isinstance(a,dict):continue
        if a.get("passed") is not True or not substantial(a.get("reason"),50):
            issues.append("G4 risky LP review missing concrete evidence "+str(a.get("lp_id")))
    return issues


def validate_content_review_audits(entry,points,draft,source):
    if entry.get("review_contract")=="g4-compact-v3":
        return validate_compact_content_review(entry,points,draft,source)
    issues=[];source_spans={x["id"]:x for x in source.get("segments",[])}
    factmap={f["id"]:f for p in points for f in p.get("required_facts",[])}
    actual=authored_text(draft)
    facts=entry.get("fact_audits",[])
    if not isinstance(facts,list) or len(facts)!=len(factmap) or {
            a.get("fact_id") for a in facts if isinstance(a,dict)}!=set(factmap):
        issues.append("G4 missing independent per-fact semantic audit")
    for a in facts if isinstance(facts,list) else []:
        if not isinstance(a,dict):continue
        f=factmap.get(a.get("fact_id"))
        if not f:continue
        if a.get("grounded") is not True or a.get("explained") is not True:
            issues.append("G4 fact not grounded and explained "+a["fact_id"])
        sid=f.get("span_id")
        if (a.get("source_span_id")!=sid or sid not in source_spans or
            clean(a.get("source_quote"))!=clean(f.get("source_quote")) or
            not source_contains(source_spans[sid]["text"],a.get("source_quote"))):
            issues.append("G4 fact source quotation invalid "+a["fact_id"])
        quote=clean(a.get("draft_quote"))
        if not substantial(quote,35) or not any(quote in text for text in actual):
            issues.append("G4 fact lacks authored explanation quote "+a["fact_id"])
        if not substantial(a.get("reason"),45):
            issues.append("G4 fact audit lacks reason "+a["fact_id"])
    dimensions=entry.get("quality_dimensions",[])
    required=set(REVIEW_DIMENSIONS)
    if any(p.get("kind")=="experiment" for p in points):
        required.add("experiment_methods")
    if not isinstance(dimensions,list) or len(dimensions)!=len(required) or {
            x.get("dimension") for x in dimensions if isinstance(x,dict)}!=required:
        issues.append("G4 independent pedagogical rubric dimensions incomplete")
    for dimension in dimensions if isinstance(dimensions,list) else []:
        if not isinstance(dimension,dict):continue
        quote=clean(dimension.get("draft_quote"))
        if (dimension.get("passed") is not True or
            not substantial(dimension.get("reason"),45) or
            not substantial(quote,35) or
            not any(quote in text for text in dimension_text(draft,dimension.get("dimension")))):
            issues.append("G4 unsupported quality dimension "+str(dimension.get("dimension")))
    return issues
