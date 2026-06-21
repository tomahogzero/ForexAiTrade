# GitHub Workflow สำหรับ ForexAiTrade

เอกสารนี้อธิบาย workflow สำหรับการทำงานบน GitHub repo ของ ForexAiTrade

Repository:

`https://github.com/tomahogzero/ForexAiTrade.git`

## Main Branch

`main` เป็น source of truth สำหรับ source code, docs, presets, scripts, tools และ selected research summaries ที่ผ่าน review แล้ว

ไม่ควร commit ไฟล์ binary/cache/temp เช่น:

- `.ex5`
- `.pyc`
- `__pycache__/`
- `.zip`
- `.agents/`
- machine-specific `.env`
- terminal/tester temp/cache files

## Branch สำหรับ Checkpoint

งาน checkpoint ควรทำบน branch แยก เช่น:

`research/checkpoint-l-price-action-fibo-spec`

หลังทำงานเสร็จควรเปิด Pull Request ก่อน merge เข้า `main`

ห้าม commit เข้า `main` โดยตรง เว้นแต่ผู้ใช้สั่งชัดเจน

## Strategy Idea Workflow

New strategy ideas ต้องเริ่มจาก specification branch ก่อน implementation

Specification branch ต้องมี:

- strategy concept
- measurable rule translation
- safety checklist
- research comparison plan
- explicit guardrails
- statement ว่ายังไม่มี implementation และยังไม่ใช่ profitability claim

Strategy implementation PR ต้องแนบ:

- research plan
- safety checklist
- symbol-profile separation ถ้ากลยุทธ์อาจใช้หลาย instrument
- train/validation/out-of-sample result
- annualized return
- max drawdown
- Calmar ratio
- profit factor
- trade count
- artifact audit

Price Action/Fibo/Grid-like strategy ต้องพิสูจน์อย่างชัดเจนว่า:

- ไม่ใช่ martingale
- ไม่ใช่ uncontrolled grid
- ไม่มี recovery lot multiplication
- ไม่มี unlimited scale-in
- ทุก order มี hard stop loss
- ไม่ bypass RiskManager หรือ safety gates

ถ้ากลยุทธ์ตั้งใจใช้กับ Gold เช่น GOLD# หรือ GOLDm# ต้องมี risk-budget review แยกก่อนเสมอ และห้าม reuse EURUSD parameters โดยอัตโนมัติ

## Annual Target Framework

Annual target framework เป็นส่วนหนึ่งของการประเมินผลวิจัย ไม่ใช่คำสัญญาว่าระบบจะทำกำไรในอนาคต

PR ใดที่อ้างว่า performance ดีขึ้น ต้องแนบข้อมูลอย่างน้อย:

- validation result
- out-of-sample result
- annualized return
- max drawdown
- Calmar ratio
- profit factor
- trade count
- artifact audit
- statement ว่านี่ไม่ใช่ proof of future profitability

ห้ามใช้ train-only result เพื่อ approve candidate และห้ามเพิ่ม lot/risk เพื่อทำให้ annual return ดูดีขึ้น

## สิ่งที่ควรใส่ใน Pull Request

PR ควรมี:

- summary ของ checkpoint
- changed files list
- RunId ที่เกี่ยวข้อง ถ้ามี
- compile status ถ้ามี MQL5 change
- artifact audit ว่าไม่มี `.ex5`, `.pyc`, `__pycache__`, nested zip
- research result/recommendation
- คำยืนยันว่าไม่มี optimization, ไม่มี new strategy implementation, ไม่มี profitability claim ถ้า checkpoint ไม่อนุญาต

## Suggested Commands

```powershell
git status
git checkout main
git pull origin main
git checkout -b research/checkpoint-l-price-action-fibo-spec
git add AGENTS.md .gitignore README.md docs scripts tools presets research MQL5
git commit -m "checkpoint-l: add price action fibo research specification"
git push -u origin research/checkpoint-l-price-action-fibo-spec
```

## Checkpoint M Skeleton PR Rule

Strategy skeleton PR เช่น `research/checkpoint-m-price-action-fibo-skeleton` ต้องยืนยันว่า:

- skeleton ถูกปิดไว้เป็น default
- ไม่มี active trade signal
- ไม่มี pending order implementation
- ไม่มี optimization
- ไม่มี lot/risk increase
- ไม่มี profitability claim
- compile log แนบไว้เมื่อมี MQL5 source change
- implementation ยังไม่ถือว่า approve demo/live forward test

## Clean Review Zip

หลัง checkpoint เสร็จ ถ้าต้องสร้าง zip review ให้รวม:

- `MQL5/`
- `scripts/`
- `tools/`
- `docs/`
- `presets/`
- `research/`
- `AGENTS.md`
- `.gitignore`
- `README.md`

และ exclude:

- `.git/`
- `.agents/`
- nested `.zip`
- `.ex5`
- `.pyc`
- `__pycache__/`
- temp/cache files
