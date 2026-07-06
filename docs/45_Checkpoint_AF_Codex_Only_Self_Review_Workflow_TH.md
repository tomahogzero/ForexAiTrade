# Checkpoint AF: Codex-Only Self-Review Workflow

วันที่จัดทำ: 2026-07-07

## สถานะของ Checkpoint นี้

Checkpoint AF เป็นงานเอกสารเท่านั้น

ไม่ได้รัน MT5, ไม่ได้รัน Strategy Tester, ไม่ได้ spawn `terminal64.exe`, ไม่ได้แก้ EA/source code, ไม่ได้แก้ presets, ไม่ได้ optimize, ไม่ได้เพิ่ม lot/risk และไม่ได้ claim profitability

## เป้าหมาย

ลด dependency ต่อ GPT/browser review สำหรับงานที่ความเสี่ยงต่ำ และให้ Codex ทำงานต่อเนื่องได้มากขึ้นภายใน repo โดยไม่ส่ง private project context ไป browser ภายนอก

แนวทางนี้เรียกว่า:

`Codex-first / GPT-optional`

หมายความว่า Codex สามารถทำงานเองครบวงจรในบางประเภท PR ได้ แต่ยังต้องรักษา guardrails ของ ForexAiTrade ทุกข้อ

## เหตุผลที่ต้องมี Workflow นี้

ที่ผ่านมา GPT review ผ่าน browser ถูก block เมื่อ Codex พยายามส่ง repo/private project context ไป ChatGPT โดยตรง

ดังนั้น workflow ใหม่ต้อง:

- ให้ Codex self-review ได้
- ลดการ copy/paste ให้ผู้ใช้
- ไม่ต้องส่งข้อมูล repo ไป external browser
- ยังป้องกัน source/preset/MT5/risk changes ที่อาจอันตราย
- ยังคง explicit approval สำหรับการรัน MT5

## Agent Roles ภายใน Codex

บทบาทเหล่านี้เป็น logical roles ใน workflow เดียว ไม่ได้หมายความว่าต้องมี process แยกจริงเสมอไป

### Builder Role

ทำงานตาม checkpoint:

- สร้าง branch/worktree
- แก้ docs/scripts/tools ตาม scope
- ไม่ขยาย scope เอง
- ไม่รัน MT5 ถ้าไม่ได้รับอนุมัติ
- ไม่แตะ EA/source หรือ presets ถ้า checkpoint ห้ามไว้

### Reviewer Role

ตรวจหลัง Builder ทำเสร็จ:

- diff ตรง scope หรือไม่
- มี forbidden artifacts หรือไม่
- มี source/preset change หรือไม่
- มี optimization/risk/profitability claim หรือไม่
- มี MT5 execution หรือ process action หรือไม่
- wording ของเอกสาร overclaim หรือไม่

### Release Role

ทำงานหลัง review ผ่าน:

- stage เฉพาะไฟล์ที่เกี่ยวข้อง
- commit
- push branch
- เปิด PR
- auto-merge เฉพาะประเภทที่ได้รับอนุญาต
- ไม่ merge PR ที่มีความเสี่ยงสูงโดยไม่มี approval

## ประเภท PR และ Merge Policy

### Tier 0: Docs / Memory / Research Plan Only

ตัวอย่าง:

- `docs/`
- `docs/ai/`
- research idea/specification docs
- GPT request docs
- checkpoint status docs
- no code, no runner, no preset, no MT5 execution

Codex สามารถ:

- self-review
- เปิด PR
- mark ready
- merge เองได้

เงื่อนไข:

- diff ต้องเป็น docs-only หรือ research-plan-only
- ไม่มี `MQL5/`
- ไม่มี `presets/`
- ไม่มี `scripts/`
- ไม่มี `tools/`
- ไม่มี MT5 run
- ไม่มี optimization
- ไม่มี lot/risk increase
- ไม่มี profitability claim

### Tier 1: Runner / Tool Plan Only

ตัวอย่าง:

- เอกสารวางแผน runner
- report path plan
- artifact collection plan
- no script/code change

Codex สามารถ self-review และ auto-merge ได้ ถ้าเป็น docs-only จริง

### Tier 2: Script / Tool / Runner Code Change

ตัวอย่าง:

- PowerShell runner change
- Python parser/scoring/report tool change
- artifact collection script change

Codex สามารถทำ branch/PR/self-review ได้ แต่ auto-merge ต้องระวังมากขึ้น

Codex merge ได้เองเฉพาะเมื่อผู้ใช้ให้ approval เฉพาะ checkpoint นั้น หรือ workflow ในอนาคตกำหนดชัดว่า allowed

ขั้นต่ำต้องตรวจ:

- no MT5 run
- no terminal spawn
- no broad `Stop-Process`
- no bulk kill `terminal64.exe`
- runner stops only PID it starts
- no source/preset change
- syntax check ผ่านถ้าเป็น Python/PowerShell
- artifact audit ผ่าน

### Tier 3: EA / MQL5 Source Change

ตัวอย่าง:

- `MQL5/Experts/`
- `MQL5/Include/`
- strategy module
- RiskManager
- RegimeDetector

Codex ห้าม auto-merge เองโดย default

ต้องมี:

- explicit checkpoint scope
- compile requirement
- compile result 0 errors / 0 warnings ถ้า compile ได้
- guardrail review
- no live trading default
- no martingale/grid/recovery lot multiplication
- no RiskManager bypass

### Tier 4: Preset Change

ตัวอย่าง:

- `presets/`
- tester/research/sanity `.set`

Codex ห้าม auto-merge เองโดย default ถ้า preset อาจเปิด trading หรือเปลี่ยน risk

ต้องตรวจ:

- `InpRequireStrategyTester=true` สำหรับ tester presets
- `InpDemoSafeMode=true`
- no risk increase unless explicitly approved
- no live/demo forward approval implied

### Tier 5: MT5 / Strategy Tester Execution

Codex ห้ามรันเองโดย default

ต้องมี approval phrase ชัดเจนจากผู้ใช้ทุกครั้ง เช่น:

```text
Approved to execute Checkpoint <X> one-run diagnostic with symbol <SYMBOL> timeframe <TF> date range YYYY-MM-DD to YYYY-MM-DD using verified artifact paths.
```

ข้อจำกัด:

- one run only ถ้า approval ระบุ one run
- ไม่ optimize
- ไม่ demo/live/forward test
- ไม่ kill unrelated terminal
- stop เฉพาะ process ที่ Codex start เอง
- ถ้า artifact หาย ต้องจัดเป็น partial/inconclusive ตามหลักฐาน

## Self-Review Checklist

ก่อน merge เอง Codex ต้องตรวจ:

```text
1. git diff --name-only origin/main..HEAD
2. ตรวจว่าไฟล์อยู่ใน allowed scope
3. ตรวจว่าไม่มี MQL5/presets/scripts/tools ถ้าเป็น Tier 0/1
4. ตรวจ forbidden artifacts:
   - .ex5
   - .pyc
   - __pycache__/
   - .zip
   - .agents/
   - temp/cache/log files
5. ตรวจ wording:
   - no profitability claim
   - no demo/live approval
   - no risk increase
   - no optimization claim ถ้าไม่ได้อนุญาต
6. ตรวจ current-status / task memory สอดคล้องกับ checkpoint ล่าสุด
7. เปิด PR พร้อม guardrail confirmation
8. ถ้าเข้า auto-merge tier ให้ mark ready แล้ว merge
```

## Auto-Merge Rule

หลัง Checkpoint AF merge แล้ว Codex สามารถ auto-merge ได้สำหรับ:

- Tier 0 docs/memory/research-plan-only
- Tier 1 runner-plan-only ที่ไม่มี code/script change

โดยไม่ต้อง GPT review ถ้า self-review ผ่าน

Codex ต้องไม่ auto-merge สำหรับ:

- MQL5 source change
- preset change
- script/runner code change ที่กระทบ execution safety
- MT5 run artifact PR
- PR ที่มี optimization/risk/performance claim
- PR ที่ Codex ไม่มั่นใจว่า scope ปลอดภัย

ถ้าไม่แน่ใจ ให้ classify เป็น `NEEDS_USER_REVIEW`

## GPT Review Policy ใหม่

GPT review เป็น optional ไม่ใช่ mandatory สำหรับ Tier 0/1

ใช้ GPT เฉพาะเมื่อ:

- ผู้ใช้ขอ
- Codex self-review ไม่มั่นใจ
- PR มี policy/strategy/risk ambiguity
- เป็น decision ที่อาจเปลี่ยนทิศทาง research สำคัญ

ห้าม Codex ส่ง private repo context ไป ChatGPT browser เองถ้า environment policy block

ถ้าต้องใช้ GPT:

- Codex เตรียม prompt ให้ผู้ใช้ copy เอง
- หรือใช้ public PR link ที่ผู้ใช้ส่งเอง
- ผู้ใช้ส่งผล `PASS` / `NEEDS_FIX` กลับมา

## Sleep Mode / Overnight Work

ถ้าผู้ใช้บอกให้ Codex ทำงานต่อระหว่างไม่อยู่:

Codex ทำได้เฉพาะ:

- docs-only
- research-plan-only
- static analysis
- parser/report tool ที่ไม่รัน MT5 ถ้าได้รับอนุญาตใน checkpoint
- GitHub PR workflow ตาม tier policy

Codex ต้องหยุดและรอผู้ใช้ถ้า:

- ต้องรัน MT5
- ต้องเปลี่ยน EA/source
- ต้องเพิ่ม risk
- ต้อง optimize
- ต้องแก้ preset ที่อาจเปิด trading
- พบ blocker ที่อาจทำให้เกิดการลบ/kill process/เปลี่ยน environment

## Guardrails

- No live trading default
- No MT5 run without explicit approval
- No Strategy Tester run without explicit approval
- No optimization unless explicitly allowed
- No lot/risk increase
- No profitability claim
- No martingale
- No uncontrolled grid
- No recovery lot multiplication
- No RiskManager bypass
- No forced broker minimum lot
- No unrelated `terminal64.exe` kill

## ผลของ Checkpoint AF

Checkpoint AF ไม่ได้อนุมัติการรัน MT5

Checkpoint AF อนุมัติเฉพาะ workflow governance สำหรับ Codex self-review และ auto-merge ในกลุ่มงานเอกสาร/แผนความเสี่ยงต่ำเท่านั้น

