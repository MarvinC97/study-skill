#!/usr/bin/env python3
"""Source-anchored two-page review preview for chapter 8.
All text is generated from a human-reviewed content contract; no model API is used.
This is an acceptance sample, not an autonomous full-chapter completion claim.
"""
from pathlib import Path
import json,html,math,re,hashlib
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'examples'/'chapter8-preview'
BASE='https://github.com/bojieli/ai-agent-book/blob/main/book/chapter8.md'
SHA='38eb64bf45b9e844b6bdbcbedfc61b9dcc12244b'

def E(s):return html.escape(str(s),quote=True)

def fact(fid,title,desc,extra=''):
    return {'id':fid,'title':title,'desc':desc,'extra':extra}

PAGES=[
  {'id':'P001','idx':1,'title':'四阶段地图：模型到底学了什么？', 'subtitle':'预训练、Mid-training、SFT、RL：四种不同的训练信号',
   'goal':'学会从“知识缺口、回答协议、任务反馈”判断适合哪个阶段，明确它们共享的基础与各自的边界。',
   'source_section':'从预训练到 RL：四阶段全景／表8-1及本章开篇',
   'lead':'同一个模型可以接受不同类型的训练。阶段之间的关键区别，是使用的数据、优化目标，以及最终希望提高的行为。',
   'facts':[
      fact('CH08-P01-F01','Pre-training（预训练）','输入大量原始文本，训练模型根据前文预测下一个 token。它主要建立通用语言规律、世界知识和初步推理能力。','使用海量原始数据；训练与计算成本通常最高。'),
      fact('CH08-P01-F02','Mid-training（中期训练／继续预训练）','在已有基座上继续用目标语言、领域文档、代码或长上下文能力数据进行语言建模，补齐特定分布上的知识与基础能力。','通常仍采用 Next Token Prediction，并混入保留数据来缓解对旧能力的遗忘。'),
      fact('CH08-P01-F03','SFT（Supervised Fine-Tuning，监督微调）','把用户输入与理想回答组成示范对。模型学习在这类输入下怎样回答，重点塑造格式、风格、指令遵循与工作流程。','通常对回答 token 计算训练损失；Loss Masking 将在后续独立页面展开。'),
      fact('CH08-P01-F04','RL（Reinforcement Learning，强化学习）','模型在任务或环境里生成行为，获得奖励信号，再更新策略，增大高奖励行为出现的概率。','前提是奖励能可靠反映目标，且模型能够探索出有价值的行为。'),
      fact('CH08-P01-F05','四个阶段都在调整参数','在这里讨论的训练阶段中，学习信号最终用于更新模型参数。它们针对的是不同的目标分布或行为目标。','RAG 是检索外部资料再提供给模型的方式；通常不会因一次检索就修改模型参数。'),
      fact('CH08-P01-F06','常见顺序与跳过条件','常见路径是 Pre-training → Mid-training → SFT → RL。具体项目按已有基础能力与目标决定，部分阶段可以跳过。','有些基座已能可靠输出结构化格式并产生成功轨迹，可以直接开展 RL；只需要固定格式的任务可能使用 SFT 就够。'),
      fact('CH08-P01-F07','“SFT 记忆、RL 泛化”有实验条件','本章的 GeneralPoints 与 V-IRL 对照实验里，有限示范的 SFT 更易过拟合，RL 在特定分布变化上表现更好。','这是实验观察的概括；SFT 也能泛化，RL 也可能因奖励或环境偏差而过拟合。'),
      fact('CH08-P01-F08','数据与环境决定训练反馈质量','Mid-training 语料、SFT 示范质量、RL 环境与奖励设计决定模型接收到什么学习信号。','PPO、GRPO 等算法的选择属于后续学习点；算法无法自动弥补错误的训练数据和反馈。'),
   ],
   'micro':[
      ('模型读过大量文字，为什么还可能不会按指定 JSON 回答？','预训练主要学习文本中的语言模式；SFT 可以用明确的输入—理想输出示范强化 JSON 格式与回答协议。'),
      ('企业知识库经常更新，应该优先把所有新事实训练进参数吗？','对需要经常更新、可追溯的事实，通常先考虑 RAG。Mid-training 更适合规模大、相对稳定且需要形成基础表征的领域知识。'),
      ('一个模型偶尔能完成任务，但 RL 的奖励设计很差，会自动变可靠吗？','奖励不忠实或环境不可靠时，RL 可能强化捷径或错误行为。应先检查奖励、环境和成功轨迹。'),
   ],
   'check':{'question':'某企业 Agent 已能理解内部术语和调用工具，但返回 JSON 常常不符合固定 schema。最先考虑哪类改进？',
            'options':['继续扩大通用 Pre-training','用高质量示范进行 SFT，并结合 schema 验证','直接让 RL 优化一个无法解析的输出'], 'correct':1,
            'success':'正确。当前缺口是可执行的输出协议；SFT 示范与程序化 schema 校验能直接针对它。',
            'failure':'先定位缺口：知识已经具备，问题在稳定格式。优先建立格式示范与校验，再决定是否需要更高成本的训练。'},
  },
  {'id':'P002','idx':2,'title':'Next Token Prediction：Loss 怎样推动参数更新？','subtitle':'从“模型猜下一个 token”到概率、损失和梯度',
   'goal':'能够按顺序解释上下文、预测概率、目标 token、Loss 和参数更新，并说明这个演示的限制。',
   'source_section':'从预训练到 RL：四阶段全景 → 预训练在做什么：预测下一个词',
   'lead':'模型每一步会根据当前上下文，为词表中的候选 token 分配概率。训练通过目标 token 与预测概率的差距形成学习信号。',
   'facts':[
      fact('CH08-P02-F01','Context（上下文）是本次预测的输入','例如输入“中国的首都是”，模型根据这段前文计算下一个 token 的条件概率。','这与整段对话的 Context Window 概念相关，但这里强调的是预测发生时的前缀。'),
      fact('CH08-P02-F02','Token 是模型预测的单位','Next Token Prediction（NTP）预测的是下一个 token；token 可能是字、词的一部分或其他分词片段。','“预测下一个词”是便于入门的说法。'),
      fact('CH08-P02-F03','输出是概率分布','在给定上下文时，模型会为词表中的各候选 token 分配概率，所有候选概率的总和为 1。','示意值例如：北京 0.12，上海 0.28，其他合计 0.60。真实分词和分布由模型决定。'),
      fact('CH08-P02-F04','训练需要目标 token','训练样本给出实际接续的目标 token；例如这次示例中的目标是“北京”。','训练对照目标计算 Loss，不是只看模型最终选出的最高概率候选。'),
      fact('CH08-P02-F05','Loss 衡量预测与目标的差距','对于单个目标 token，交叉熵的一项可以写成 Loss = −log p(target)。目标概率越小，该项 Loss 越大。','这里展示单 token 的简化计算；实际训练通常跨多个 token 聚合。'),
      fact('CH08-P02-F06','参数更新改变模型的未来概率','训练通过 Loss 求梯度，再由优化器更新模型参数。理想情况下，相似上下文中目标 token 的预测概率逐步增大。','单次更新可能同时影响其他上下文；学习率、数据与模型结构决定实际变化。'),
      fact('CH08-P02-F07','Mid-training 与 SFT 也常用 NTP','Mid-training 继续语言建模，通常对大量文档 token 计算 Loss；SFT 使用输入—理想输出示范，常对回答 token 计算 Loss。','Loss Masking 将不应计入损失的输入 token 屏蔽；RL 的优化信号则来自奖励目标。'),
      fact('CH08-P02-F08','Loss 下降不等于稳定能力','某个目标 token 更容易预测，是局部训练现象；模型能否稳定回答新问题，还取决于数据覆盖、上下文变化、评估分布与采样。','必须用独立测试与不同表述检验模型是否真正掌握相关规律。'),
   ],
   'micro':[
      ('模型猜错时，训练系统到底知道什么？','系统有上下文、真实目标 token、模型给这个目标的概率。它用这些信息计算 Loss，再产生用于参数更新的梯度。'),
      ('“北京”当前不是概率最高的候选，训练就完全没有方向吗？','依然有方向。目标 token 已明确，交叉熵利用它当前的预测概率提供连续的损失信号；概率越低，该样本损失越高。'),
      ('Loss 下降一次，能证明模型真正理解中国地理吗？','不能。这说明模型在训练样本的目标预测上有所改善；是否形成可迁移知识，需要不同问法、不同上下文和留出数据的评估。'),
   ],
   'check':{'question':'同一上下文的目标 token 是“北京”。两次预测分别给它概率 0.1 和 0.7。按 −log p(target) 计算，哪个判断正确？',
            'options':['p=0.1 的 Loss 更小','p=0.7 的 Loss 更小','两者 Loss 完全相同'], 'correct':1,
            'success':'正确。−log(0.7)≈0.357，小于 −log(0.1)≈2.303；目标概率越大，这一项损失越小。',
            'failure':'用单目标交叉熵检查：Loss = −log p(target)。当目标概率增加，Loss 下降。'},
  }
]

CSS=r'''
:root{--bg:#f3f6f8;--paper:#fff;--ink:#112639;--mute:#556b7d;--line:#d6e0e8;--blue:#235bc0;--blue2:#eaf0fd;--mint:#e7f5f0;--orange:#fff1d8;--shadow:0 12px 42px #13283e0d}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.74 system-ui,-apple-system,"Segoe UI",Arial,sans-serif}main{max-width:1120px;margin:auto;padding:23px 20px 72px}h1{font-size:clamp(36px,5.2vw,63px);line-height:1.16;letter-spacing:-.045em;margin:14px 0}h2{font-size:clamp(24px,3vw,31px);line-height:1.26;margin:0 0 17px}h3{margin:0 0 8px;font-size:19px}p{margin:9px 0 13px}a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}button,input{font:inherit}button{cursor:pointer}.top{display:flex;justify-content:space-between;gap:16px;align-items:center;color:var(--mute);font-size:13px;font-weight:700;padding:10px 0 18px}.tag{display:inline-block;border:1px solid #c4d3e2;border-radius:999px;padding:4px 12px;background:#fff}.hero{border:1px solid var(--line);border-radius:26px;padding:38px 39px;background:var(--paper);box-shadow:var(--shadow)}.kicker{color:var(--blue);font-size:12px;font-weight:850;letter-spacing:.12em}.subtitle{font-size:21px;color:var(--mute);max-width:850px}.goal{margin-top:25px;padding:17px 19px;background:var(--blue2);border-radius:15px;border-left:4px solid var(--blue)}.bar{height:6px;width:100%;border-radius:10px;background:#dce7f3;margin-top:27px;overflow:hidden}.bar b{display:block;height:100%;width:5.4%;background:var(--blue)}.section{margin-top:24px;background:var(--paper);border:1px solid var(--line);border-radius:23px;padding:28px 32px;box-shadow:var(--shadow)}.intro{font-size:19px;color:var(--mute)}.eyebrow{color:var(--blue);font-size:12px;font-weight:800;letter-spacing:.11em;margin-bottom:8px}.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.stage{border:1px solid var(--line);border-radius:16px;padding:19px 16px;background:#f8fbff;display:flex;flex-direction:column;gap:8px}.stage .step{font-size:12px;font-weight:800;color:var(--blue)}.stage strong{font-size:20px}.stage small{font-size:13px;color:var(--mute)}.stage .pill{font-size:12px;margin-top:auto;background:#e4edfb;padding:5px 9px;border-radius:8px}.data-table{width:100%;border-collapse:collapse;font-size:14px}.data-table th,.data-table td{text-align:left;padding:12px 10px;border-bottom:1px solid var(--line);vertical-align:top}.data-table th{background:#f0f5fb;color:#39576c;font-size:12px}.fact{margin-top:16px;padding:17px 19px;border:1px solid var(--line);border-radius:14px;background:#fbfcfd}.fact h3{font-size:18px}.fact p{margin:5px 0}.fact .edge{font-size:14px;color:var(--mute);margin-top:11px;padding-left:13px;border-left:3px solid #97b3ce}.flow{display:flex;flex-wrap:wrap;gap:9px;align-items:center}.flow .node{padding:14px;border-radius:12px;border:1px solid var(--line);background:#f0f5fc;font-weight:700}.flow .arrow{color:var(--blue);font-size:26px}.q{border:1px solid #d6e4da;border-radius:14px;margin-top:13px;background:#f7fbf8;padding:12px 16px}.q summary{cursor:pointer;font-weight:750;outline-offset:4px}.q .answer{border-left:3px solid #298260;margin:13px 0 4px;padding:10px 13px;background:#e8f5ed;border-radius:5px}.note{padding:18px 20px;border-radius:16px;background:var(--orange);margin-top:15px}.demo{border:1px solid #a6bed9;border-radius:16px;background:#f0f6fd;padding:22px}.seg{display:flex;flex-wrap:wrap;gap:8px;margin:13px 0 18px}.seg button,.check button,.reset{border:1px solid #b9cbdc;background:#fff;border-radius:11px;color:var(--ink);padding:10px 15px}.seg button.active{background:#2459b8;color:#fff;border-color:#2459b8}.demo-output{background:#fff;border:1px solid var(--line);border-radius:13px;padding:19px;min-height:115px}.check button{display:block;margin:9px 0;width:100%;text-align:left}.check button:hover,.seg button:hover,.reset:hover{box-shadow:0 0 0 2px #8fb2e7}.feedback{min-height:30px;margin-top:10px;font-weight:750}.checkpoint{border-left:5px solid #edb04e}.formula{font:700 27px/1.5 ui-monospace,Consolas,monospace;color:#174e88;text-align:center;padding:14px;background:#ecf3fc;border-radius:12px}.slider-row{display:flex;align-items:center;gap:15px;margin:18px 0}.slider-row input{flex:1;min-width:120px;accent-color:#2459b8}.prob{display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin:14px 0}.prob div{min-width:0;padding:13px 9px;text-align:center;border-radius:9px;background:#dae9fa;white-space:normal}.prob .target{background:#acd7c6}.stat{font-size:31px;font-weight:850;color:#1b6892}.hint{color:var(--mute);font-size:14px}.foot{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-top:30px;border-top:1px solid var(--line);padding-top:23px}.source{font-size:13px;color:var(--mute)}.noscript{display:block;padding:13px 18px;border-left:3px solid #e2a742;background:#fff5df;margin-top:14px}.compact{font-size:15px}.dark{--bg:#131d27;--paper:#1a2936;--ink:#f0f6fb;--mute:#afc0ce;--line:#3c5060;--blue:#99beff;--blue2:#1c3552;--mint:#193c35;--orange:#473622;--shadow:none}.dark .stage,.dark .fact,.dark .q{background:#20313e}.dark .node,.dark .formula,.dark .demo{background:#20384f}.dark .demo-output,.dark .seg button,.dark .check button,.dark .reset,.dark .tag{background:#253849;color:#f0f6fb}.dark .data-table th{background:#263e50;color:#eaf3fc}.dark .q .answer{background:#1d493b}.dark .prob div{background:#28445f}.dark .prob .target{background:#255b4b}
@media(max-width:850px){main{padding:14px 12px 42px}.grid4{grid-template-columns:1fr 1fr}.hero,.section{padding:21px 19px}.data-table{font-size:13px}.data-table th,.data-table td{padding:9px 5px}}@media(max-width:520px){.grid4{grid-template-columns:1fr}.hero{border-radius:19px}.section{border-radius:18px}h1{font-size:36px}.subtitle{font-size:18px}.prob{grid-template-columns:1fr}.top{font-size:12px}.slider-row{flex-wrap:wrap}.foot{flex-direction:column;align-items:flex-start}}
'''
JS=r'''
const root=document.body;
document.querySelector('#theme').addEventListener('click',()=>{root.classList.toggle('dark');});
document.querySelectorAll('.check button[data-index]').forEach(b=>b.addEventListener('click',()=>{const section=b.closest('.check'),ok=Number(b.dataset.index)===Number(section.dataset.correct),feedback=section.querySelector('.feedback');feedback.textContent=ok?section.dataset.success:section.dataset.failure;feedback.style.color=ok?'#218260':'#b15b24';}));
document.querySelector('#reset').addEventListener('click',()=>{document.querySelectorAll('details.q').forEach(x=>x.open=false);document.querySelectorAll('.feedback').forEach(x=>x.textContent='');if(window.resetDemo)window.resetDemo();});
'''

STAGE_DEMO=r'''
<section class="section" id="interactive"><div class="eyebrow">TRY IT · 预测 → 操作 → 观察 → 解释</div><h2>改变任务缺口，训练选择怎样变化？</h2>
<p>先判断：问题出在领域知识、输出协议，还是可验证任务的成功率？点击场景观察推荐的优先排查方向。</p>
<div class="demo"><div class="seg" role="group" aria-label="切换训练场景">
<button type="button" class="active" data-scenario="domain">缺少领域基础</button><button type="button" data-scenario="format">JSON 格式不稳定</button><button type="button" data-scenario="policy">偶尔成功但成功率低</button></div>
<div class="demo-output" id="scenario-output" aria-live="polite"><h3>优先排查：领域基础 / 资料检索</h3><p>知识缺口涉及大量稳定领域知识时，考虑 Mid-training；经常更新、需要引用的资料优先考虑 RAG。</p><p class="hint">这是教学决策示意。真实选择还取决于数据量、基模能力和成本。</p></div></div>
<p class="compact"><b>三种条件对照（关闭脚本也可阅读）：</b>领域知识缺失 → Mid-training / RAG；固定 JSON 输出不稳 → SFT / schema 验证；成功轨迹已存在且奖励可验证 → 评估 RL。</p></section>
'''
STAGE_SCRIPT=r'''
const variants={domain:['优先排查：领域基础 / 资料检索','知识缺口涉及大量稳定领域知识时，考虑 Mid-training；经常更新、需要引用的资料优先考虑 RAG。'],format:['优先排查：SFT / schema 验证','模型已有知识，但无法稳定遵守 JSON 协议。先用高质量示范与程序化校验建立可靠格式。'],policy:['优先排查：奖励与环境，再评估 RL','已有非零成功率且奖励能可靠衡量结果，RL 才可能有效提高高质量策略的概率。']};
window.resetDemo=()=>pick('domain');function pick(key){document.querySelectorAll('[data-scenario]').forEach(b=>b.classList.toggle('active',b.dataset.scenario===key));const x=variants[key];document.querySelector('#scenario-output').innerHTML='<h3>'+x[0]+'</h3><p>'+x[1]+'</p><p class="hint">教学决策示意，不是对项目的自动诊断。</p>';}
document.querySelectorAll('[data-scenario]').forEach(b=>b.addEventListener('click',()=>pick(b.dataset.scenario)));
'''
LOSS_DEMO=r'''
<section class="section" id="interactive"><div class="eyebrow">TRY IT · 规则计算模拟</div><h2>拖动概率，观察 Loss 怎样变化</h2>
<p>假设目标 token 是“北京”。先预测：把目标概率从 0.10 调到 0.70，Loss 应该变大还是变小？</p>
<div class="demo"><label for="p-slider"><b>模型给“北京”的概率 p</b></label><div class="slider-row"><input id="p-slider" type="range" min="5" max="95" value="12" step="1" aria-label="北京的预测概率"><output id="p-display">0.12</output></div>
<div class="prob" aria-label="三个分组候选概率示意"><div class="target">北京<br><strong id="p-beijing">12%</strong></div><div>上海<br><strong id="p-shanghai">22%</strong></div><div>其他候选<br><strong id="p-other">66%</strong></div></div>
<div class="formula">Loss = −ln(p)</div><p>当前单 token Loss：<span id="loss" class="stat">2.120</span></p><p class="hint" id="loss-note" aria-live="polite">目标概率低，Loss 较高。</p></div>
<p class="compact"><b>固定对照：</b>p=0.10 → Loss≈2.303；p=0.70 → Loss≈0.357。这里只执行交叉熵的数学计算，没有模型、优化器或梯度更新。</p></section>
'''
LOSS_SCRIPT=r'''
const slider=document.querySelector('#p-slider');function update(){const p=Number(slider.value)/100,sh=(1-p)*.25,other=(1-p)*.75;document.querySelector('#p-display').textContent=p.toFixed(2);document.querySelector('#p-beijing').textContent=(p*100).toFixed(0)+'%';document.querySelector('#p-shanghai').textContent=(sh*100).toFixed(1)+'%';document.querySelector('#p-other').textContent=(other*100).toFixed(1)+'%';document.querySelector('#loss').textContent=(-Math.log(p)).toFixed(3);document.querySelector('#loss-note').textContent=p>=.5?'目标概率较高，对应的 Loss 较低。':'目标概率较低，对应的 Loss 较高。';}
slider.addEventListener('input',update);window.resetDemo=()=>{slider.value='12';update()};update();
'''

def factblock(f):
    return f'''<article class="fact" data-fact-id="{E(f['id'])}"><h3>{E(f['title'])}</h3><p>{E(f['desc'])}</p><p class="edge">条件与边界：{E(f['extra'])}</p></article>'''

def qblocks(page):
    return ''.join(f'<details class="q"><summary>点击思考 · {E(q)}</summary><div class="answer">{E(a)}</div></details>' for q,a in page['micro'])

def ck(page):
    c=page['check']; buttons=''.join(f'<button type="button" data-index="{i}">{E(opt)}</button>' for i,opt in enumerate(c['options']))
    return f'''<section class="section checkpoint check" data-correct="{c['correct']}" data-success="{E(c['success'])}" data-failure="{E(c['failure'])}"><div class="eyebrow">CHECKPOINT · 判断机制</div><h2>你能独立判断吗？</h2><p>{E(c['question'])}</p>{buttons}<p class="feedback" aria-live="polite"></p><p class="hint">选择后显示反馈；点击和阅读不自动记录为“已掌握”。</p></section>'''

def pagebody(page):
    if page['idx']==1:
      stages=[('01','Pre-training','海量原始文本','建立语言、知识和初步推理','NTP / 通用基础'),('02','Mid-training','目标领域与能力语料','补齐领域知识、语言和长上下文能力','继续 NTP'),('03','SFT','输入—理想输出示范','建立回答格式、风格与流程协议','目标回答的监督'),('04','RL','任务、环境与奖励','强化能得到高奖励的行为策略','最大化期望奖励')]
      diagram='<div class="grid4">'+''.join(f'<div class="stage"><span class="step">{a}</span><strong>{b}</strong><small>{c}</small><p>{d}</p><span class="pill">{e}</span></div>' for a,b,c,d,e in stages)+'</div>'
      table='''<table class="data-table"><thead><tr><th>阶段</th><th>直接训练信号</th><th>学到什么</th><th>相对代价</th></tr></thead><tbody><tr><td>Pre-training</td><td>原始文本的下一个 token</td><td>通用能力基础</td><td>通常极高</td></tr><tr><td>Mid-training</td><td>目标语料中的 token</td><td>领域和基础能力</td><td>中到高</td></tr><tr><td>SFT</td><td>示范的回答 token</td><td>回答协议和流程</td><td>通常相对较低</td></tr><tr><td>RL</td><td>任务反馈与奖励</td><td>更高奖励的行为策略</td><td>通常较高且需要环境</td></tr></tbody></table>'''
      first=f'<section class="section"><div class="eyebrow">MENTAL MODEL · 四阶段地图</div><h2>同一个模型，四类不同的学习任务</h2>{diagram}<p class="hint">这是一张典型能力开发路径图。四个阶段均可能更新模型参数，但具体项目可以跳过不必要的阶段。</p></section>'
      second=f'<section class="section"><div class="eyebrow">SOURCE-ANCHORED DETAILS</div><h2>每个阶段具体改变什么？</h2>{"".join(factblock(f) for f in page["facts"][:4])}</section>'
      third=f'<section class="section"><div class="eyebrow">CONDITIONS & BOUNDARIES</div><h2>为什么不能把四个阶段当成必经关卡？</h2>{"".join(factblock(f) for f in page["facts"][4:])}<div class="note"><b>判断顺序：</b>先用评估定位失败原因，再决定是数据、Prompt / Harness、RAG、SFT 还是 RL。阶段选择服务于具体能力缺口。</div></section>'
      return first+second+f'<section class="section"><h2>把训练信号放在同一张表里</h2>{table}</section>'+STAGE_DEMO+third
    first='''<section class="section"><div class="eyebrow">ONE TRAINING STEP · 先看链路</div><h2>一次预测如何变成训练信号</h2><div class="flow"><span class="node">上下文</span><span class="arrow">→</span><span class="node">候选 token 概率</span><span class="arrow">→</span><span class="node">目标 token</span><span class="arrow">→</span><span class="node">Loss</span><span class="arrow">→</span><span class="node">梯度与参数更新</span></div><p class="hint">箭头表示本例计算和训练步骤的先后／数据依赖，不代表模型只输出一个确定答案。</p><div class="note"><strong>例子：</strong>输入“中国的首都是”。训练样本的目标 token 是“北京”。模型当前可能把概率更高地分配给别的候选，但目标仍用于计算 Loss。</div></section>'''
    second=f'<section class="section"><div class="eyebrow">MECHANISM · 逐步拆开</div><h2>五个环节分别负责什么？</h2>{"".join(factblock(f) for f in page["facts"][:6])}</section>'
    third=f'<section class="section"><div class="eyebrow">BOUNDARIES & TRANSFER</div><h2>这套机制如何连接到 Mid-training 与 SFT？</h2>{"".join(factblock(f) for f in page["facts"][6:])}</section>'
    return first+second+LOSS_DEMO+third

def render(page):
    previous='index.html' if page['idx']==1 else '01-four-training-stages.html'
    nxt='02-next-token-prediction.html' if page['idx']==1 else 'index.html'
    n=page['idx'];pct=n/37*100
    nav=f'''<footer class="foot"><a href="{previous}">← 上一页 / 目录</a><a href="{nxt}">下一页 / 目录 →</a></footer>'''
    head=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(page['title'])} · Study V6</title><style>{CSS}</style></head><body><main><div class="top"><span>AI AGENT BOOK · CHAPTER 08 · PAGE {n:02d} / 37 (规划版)</span><button id="theme" type="button" class="tag" aria-label="切换深浅色主题">切换主题</button></div><header class="hero"><div class="kicker">STUDY-D · SOURCE GROUNDED · PAGE {n:02d}</div><h1>{E(page['title'])}</h1><p class="subtitle">{E(page['subtitle'])}</p><div class="goal"><strong>学完你应该能做到：</strong>{E(page['goal'])}</div><div class="bar"><b style="width:{pct:.2f}%"></b></div><p class="source">来源：<a href="{BASE}" target="_blank" rel="noopener noreferrer">《AI Agent Book》Chapter 8</a> → {E(page['source_section'])} ｜原始 Git blob SHA：{SHA[:12]}… ｜ 本样例覆盖第一页和第二页的指定学习范围</p></header><section class="section"><div class="eyebrow">WHY</div><h2>先建立问题意识</h2><p class="intro">{E(page['lead'])}</p></section>'''
    questions=f'<section class="section"><div class="eyebrow">HIDDEN QUESTIONS · 先想再点</div><h2>三个小问题，把原理连接起来</h2>{qblocks(page)}</section>'
    foot=f'''<section class="section"><div class="eyebrow">REMEMBER</div><h2>回到最核心的理解</h2><p>{E(page['goal'])}</p><p class="hint">来源锚点保留在 Content Contract；本页的事实与解释经逐项静态比对和浏览器交互检查。没有运行真实模型训练。</p><button id="reset" class="reset" type="button">重置本页互动与答题反馈</button></section>{nav}</main><script>{JS}{STAGE_SCRIPT if n==1 else LOSS_SCRIPT}</script></body></html>'''
    return head+pagebody(page)+questions+ck(page)+foot

def build():
  OUT.mkdir(parents=True,exist_ok=True)
  manifest={'version':'6.0-preview','source':BASE,'git_blob_sha':SHA,'scope':'Chapter 8 pages 1-2 only; no complete chapter outline verification',
    'authoring':'model-authored content contract; offline render. Live Manager/worker API calls not executed.',
    'page_count':2,'pages':[]}
  for page in PAGES:
    name='01-four-training-stages.html' if page['idx']==1 else '02-next-token-prediction.html'
    text=render(page);(OUT/name).write_text(text,encoding='utf-8')
    manifest['pages'].append({'page_id':page['id'],'file':name,'required_fact_ids':[x['id'] for x in page['facts']], 'source_section':page['source_section'],'sha256':hashlib.sha256(text.encode()).hexdigest()})
  overview='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Study V6 · 第八章前两页验收目录</title><style>'''+CSS+'''</style><main><header class="hero"><div class="kicker">STUDY V6 · REVIEW SAMPLE</div><h1>第八章 · 前两页</h1><p class="subtitle">按用户确认的大纲生成的两页真实教学内容；其余课程尚未生成。</p></header><section class="section"><h2>当前验收范围</h2><p><a href="01-four-training-stages.html">01 · 四阶段地图：预训练、Mid-training、SFT、RL</a></p><p><a href="02-next-token-prediction.html">02 · Next Token Prediction、Loss 与参数更新</a></p></section></main></html>'''
  (OUT/'index.html').write_text(overview,encoding='utf-8')
  (OUT/'content-contract.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
  return manifest
if __name__=='__main__':
  print(json.dumps(build(),ensure_ascii=False,indent=2))
