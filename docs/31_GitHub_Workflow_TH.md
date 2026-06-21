# GitHub Workflow สำหรับ ForexAiTrade

เอกสารนี้อธิบาย workflow สำหรับการทำงานบน GitHub repo ของ ForexAiTrade

Repository:

`https://github.com/tomahogzero/ForexAiTrade.git`

## Main Branch

`main` ควรเป็น stable source of truth ของ source code, docs, presets, scripts, tools และ selected research summaries ที่ผ่าน review แล้ว

ไม่ควร commit ไฟล์ binary/cache/temp เช่น:

- `.ex5`
- `.pyc`
- `__pycache__/`
- `.zip`
- `.agents/`
- machine-specific `.env`
- terminal/tester temp/cache/log files

## Branch สำหรับ Checkpoint

งาน checkpoint ควรทำบน branch แยก เช่น:

`research/checkpoint-j-risk-gate-cooldown`

หลังทำงานเสร็จให้เปิด Pull Request ก่อน merge เข้า `main`

## สิ่งที่ควรใส่ใน Pull Request

PR ควรมี:

- summary ของ checkpoint
- changed files list
- RunId ที่เกี่ยวข้อง
- compile status ถ้ามี MQL5 change
- artifact audit ว่าไม่มี `.ex5`, `.pyc`, `__pycache__`, nested zip
- research result/recommendation
- คำยืนยันว่าไม่มี optimization, ไม่มี new strategy, ไม่มี profitability claim ถ้า checkpoint ไม่อนุญาต

## Commit Message

รูปแบบ commit message ที่แนะนำ:

`checkpoint-j: add risk gate cooldown diagnostic research`

## Suggested Commands

Codex ไม่ควร push อัตโนมัติถ้าผู้ใช้ไม่ได้สั่งชัดเจน

คำสั่งที่ผู้ใช้อาจใช้เอง:

```powershell
git status
git add AGENTS.md .gitignore README.md docs scripts tools presets research MQL5
git commit -m "checkpoint-j: add risk gate cooldown diagnostic research"
git branch
git push origin research/checkpoint-j-risk-gate-cooldown
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
