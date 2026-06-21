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

`research/checkpoint-k-annual-target-framework`

หลังทำงานเสร็จควรเปิด Pull Request ก่อน merge เข้า `main` ยกเว้นผู้ใช้สั่งให้ commit/push เข้า `main` โดยตรงอย่างชัดเจน

## สิ่งที่ควรใส่ใน Pull Request

PR ควรมี:

- summary ของ checkpoint
- changed files list
- RunId ที่เกี่ยวข้อง
- compile status ถ้ามี MQL5 change
- artifact audit ว่าไม่มี `.ex5`, `.pyc`, `__pycache__`, nested zip
- research result/recommendation
- คำยืนยันว่าไม่มี optimization, ไม่มี new strategy, ไม่มี profitability claim ถ้า checkpoint ไม่อนุญาต

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

## Commit Message

รูปแบบ commit message ที่แนะนำ:

`checkpoint-k: add annual target viability framework`

## Suggested Commands

Codex ไม่ควร push อัตโนมัติถ้าผู้ใช้ไม่ได้สั่งชัดเจน

คำสั่งที่ผู้ใช้อาจใช้เอง:

```powershell
git status
git add AGENTS.md .gitignore README.md docs scripts tools presets research MQL5
git commit -m "checkpoint-k: add annual target viability framework"
git branch
git push origin research/checkpoint-k-annual-target-framework
```

## Clean Review Zip

หลัง checkpoint เสร็จ ให้สร้าง zip review ที่รวม:

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
