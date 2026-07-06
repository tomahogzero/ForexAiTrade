# Checkpoint AF: Codex-Only Self-Review Workflow

วันที่จัดทำ: 2026-07-07

## สถานะของ Checkpoint นี้

Checkpoint AF เป็นงานเอกสารเท่านั้น

ไม่ได้รัน MT5, ไม่ได้รัน Strategy Tester, ไม่ได้ spawn `terminal64.exe`, ไม่ได้แก้ EA/source code, ไม่ได้แก้ presets, ไม่ได้ optimize, ไม่ได้เพิ่ม lot/risk และไม่ได้ claim profitability

## เป้าหมาย

ลดการพึ่งพา GPT browser review สำหรับงานที่มีความเสี่ยงต่ำ และให้ Codex ทำงานใน repo ได้เร็วขึ้นโดยยังรักษา guardrails ของ ForexAiTrade

แนวคิดหลัก:

- Codex ทำงานหลักเองใน repo
- Codex ทำ self-review ด้วย checklist ที่บังคับ
- Codex auto-merge ได้เฉพาะงานความเสี่ยงต่ำที่กำหนดไว้
- งานที่เกี่ยวกับ MT5 execution, EA/source, presets, risk, optimization, หรือ live/demo trading ยังต้องขอ approval จากผู้ใช้

## Logical Agents ภายใน Codex

นี่ไม่ใช่ external agent และไม่ใช่ GPT browser

เป็นบทบาทการทำงานภายใน Codex เพื่อให้ตรวจงานเป็นขั้นตอน:

### 1. Builder Agent

หน้าที่:

- สร้าง branch/worktree
- แก้ไฟล์ตาม checkpoint
- จำกัด scope ให้แคบ
- ไม่แตะไฟล์นอกงาน
- ไม่รัน MT5 ถ้า checkpoint ไม่อนุญาต

### 2. Safety Reviewer Agent

หน้าที่:

- ตรวจ diff ว่าอยู่ใน scope
- ตรวจว่าไม่มี forbidden artifacts
- ตรวจว่าไม่มี profitability claim
- ตรวจว่าไม่มี lot/risk increase
- ตรวจว่าไม่มี source/preset change ถ้า checkpoint ห้ามไว้
- ตรวจว่า execution status แยกจาก strategy performance

### 3. Release Agent

หน้าที่:

- stage เฉพาะไฟล์ที่จำเป็น
- commit ด้วย message ที่ตรง checkpoint
- push branch
- เปิด PR
- auto-merge เฉพาะ PR ที่เข้าเงื่อนไข Codex-only safe merge

## PR ประเภทที่ Codex Auto-Merge ได้

Codex สามารถ self-review และ auto-merge ได้เมื่อครบทุกเงื่อนไข:

- เป็น docs-only หรือ research-plan-only
- ไม่เปลี่ยน `MQL5/`
- ไม่เปลี่ยน `presets/`
- ไม่เปลี่ยน risk defaults
- ไม่รัน MT5
- ไม่รัน Strategy Tester
- ไม่ spawn `terminal64.exe`
- ไม่ optimize
- ไม่เพิ่ม lot/risk
- ไม่ claim profitability
- ไม่มี `.ex5`, `.pyc`, `__pycache__/`, `.zip`, `.agents/`
- PR body ระบุ guardrails ครบ
- Codex self-review = `PASS`

ตัวอย่างที่ auto-merge ได้:

- checkpoint documentation
- diagnosis plan
- approval plan
- research-plan-only document
- GPT request file
- project memory update

## PR ที่ Codex ห้าม Auto-Merge

ต้องรอผู้ใช้ review หรือ approval เพิ่มถ้ามีอย่างใดอย่างหนึ่ง:

- แก้ `MQL5/`
- แก้ `presets/`
- แก้ runner/script ที่อาจกระทบ MT5 execution
- แก้ tools ที่เปลี่ยน scoring/classification สำคัญ
- มี compile requirement
- มี MT5 run หรือ Strategy Tester run
- มี research result จากการรันจริง
- มี report/status ที่ต้องตีความจาก execution
- มี risk setting, lot setting, stop-loss, take-profit, trailing, strategy behavior
- มี optimization
- มี live/demo/forward test

กรณี Checkpoint AC เป็นตัวอย่างที่ไม่ควร auto-merge เพราะมี MT5 execution จริง แม้เอกสารผลลัพธ์จะถูกต้องก็ตาม

## Codex Self-Review Checklist

ก่อน auto-merge Codex ต้องตอบ checklist นี้:

1. Changed files อยู่ใน scope หรือไม่
2. มี `MQL5/` change หรือไม่
3. มี `presets/` change หรือไม่
4. มี `scripts/` หรือ `tools/` change ที่กระทบ execution หรือ scoring หรือไม่
5. มี MT5 run หรือ Strategy Tester run หรือไม่
6. มี optimization หรือ parameter tuning หรือไม่
7. มี lot/risk increase หรือไม่
8. มี martingale/grid/recovery lot logic หรือไม่
9. มี profitability claim หรือไม่
10. มี forbidden artifacts staged หรือไม่
11. PR body ระบุ compile/MT5/artifact audit/guardrails ครบหรือไม่
12. ถ้าเป็น docs-only จริง Codex self-review result เป็น `PASS` หรือไม่

ถ้าข้อใดไม่ชัดเจน ให้จัดเป็น `NEEDS_USER_REVIEW`

## Review Result Labels

ใช้ label ภายใน response:

- `CODEX_SELF_REVIEW_PASS`
- `NEEDS_USER_REVIEW`
- `NEEDS_FIX`
- `BLOCKED_BY_GUARDRAIL`

ห้ามใช้ `PASS` แบบคลุมเครือถ้า scope มี execution หรือ risk impact

## Auto-Merge Flow

สำหรับ docs-only safe PR:

1. Fetch `origin/main`
2. สร้าง clean worktree จาก `origin/main`
3. ทำ checkpoint docs
4. ตรวจ artifact audit
5. เปิด Draft PR
6. ทำ Codex self-review
7. ถ้า `CODEX_SELF_REVIEW_PASS` และเข้าเงื่อนไข auto-merge ให้ mark ready แล้ว merge
8. Fetch ยืนยัน `origin/main`
9. สรุป handoff

## งานที่ยังต้อง Explicit User Approval

ยังต้องมี approval phrase จากผู้ใช้สำหรับ:

- MT5 execution
- Strategy Tester execution
- retry ที่เกี่ยวกับ tester
- runner change ที่จะถูกใช้รันจริง
- source/preset changes
- optimization
- risk/lot increase
- live/demo/forward test
- cleanup/delete/stash/revert ไฟล์ที่อาจเป็นของผู้ใช้

## Guardrails

Codex-only workflow ไม่ได้ลด guardrails เดิม

ยังคงห้าม:

- เปิด live trading default
- optimize โดยไม่ได้รับอนุญาต
- เพิ่ม lot/risk เพื่อให้ผลดูดี
- claim profitability
- martingale
- uncontrolled grid recovery
- recovery lot multiplication
- bypass RiskManager
- force broker minimum lot ถ้าผิด risk budget
- kill unrelated `terminal64.exe`

## ผลลัพธ์ที่คาดหวัง

หลัง Checkpoint AF merge แล้ว งานเอกสาร/แผนความเสี่ยงต่ำจะเดินเร็วขึ้น โดยไม่ต้องส่งข้อมูลไป GPT browser และไม่ติด policy export context

งานที่มีผลกับระบบจริงยังคงต้องผ่าน review/approval ที่เข้มเหมือนเดิม

