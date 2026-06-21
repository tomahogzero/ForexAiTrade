# Checkpoint K: Annual Target and Risk-Adjusted Viability Framework

วันที่จัดทำ: 2026-06-21

## เป้าหมาย

Checkpoint K เพิ่มกรอบประเมินผลแบบ annual target และ risk-adjusted viability เพื่อให้ ForexAiTrade ไม่ดูแค่ net profit เป็นบวก แต่ต้องถามต่อว่า return คุ้มกับความเสี่ยงของ Forex หรือไม่

งานนี้ไม่ใช่ optimization, ไม่เพิ่ม lot/risk, ไม่เพิ่ม strategy ใหม่, ไม่ claim profitability และยังไม่อนุญาตให้เริ่ม demo/live forward test

## ทำไมเป้าหมาย Forex ต้องสูงกว่า investment ทั่วไป

การลงทุนทั่วไปอาจตั้งเป้าประมาณ 8-10% ต่อปี แต่ Forex มีความเสี่ยงสูงกว่า เช่น leverage, spread, slippage, execution risk, broker-specific symbol behavior และ drawdown ที่เกิดเร็วกว่า

ดังนั้นระบบ Forex ที่ให้ return ใกล้เคียง investment ทั่วไป แต่มีความเสี่ยงสูงกว่า ยังไม่ถือว่า worth-the-risk

## Higher Risk ไม่ได้แปลว่า Higher Return

ความเสี่ยงสูงไม่ได้รับประกันผลตอบแทนสูง ถ้าระบบเพิ่ม lot หรือเพิ่ม leverage เพื่อทำให้ annual return ดูสูงขึ้น แต่ edge ไม่ดีขึ้นจริง ระบบจะเปราะบางขึ้นและอาจพังเร็วขึ้น

หลักของโปรเจกต์นี้คือ:

- เพิ่ม edge quality ก่อนเพิ่ม exposure
- รักษา capital preservation เป็นอันดับแรก
- ไม่ใช้ lot size เพื่อปกปิด strategy weakness

## Annualized Return อาจทำให้เข้าใจผิด

Annualized return และ CAGR approximation มีประโยชน์ในการเทียบคร่าว ๆ แต่สามารถทำให้เข้าใจผิดได้เมื่อ:

- test period สั้นเกินไป
- trade count ต่ำเกินไป
- ผลลัพธ์มาจากไม่กี่ trade
- drawdown ยังไม่ถูกทดสอบในหลาย market regime

ดังนั้น metric เหล่านี้ต้องอ่านร่วมกับ validation, out-of-sample, drawdown, Calmar ratio, profit factor และ trade count

## ทำไม Drawdown และ Calmar สำคัญ

Drawdown แสดงความเจ็บปวดของระบบระหว่างทาง ส่วน Calmar ratio เทียบ annualized return กับ max drawdown

ตัวอย่าง:

- return สูงแต่ drawdown สูงมาก อาจไม่คุ้มความเสี่ยง
- return ต่ำแต่ drawdown ต่ำมาก อาจยังไม่คุ้ม Forex risk premium
- Calmar >= 1.0 เป็นเกณฑ์ขั้นต่ำที่ช่วยบอกว่า return เริ่มสัมพันธ์กับ risk ดีขึ้น

## Target Profile

ไฟล์ที่เพิ่ม:

`research/target_profile.json`

Target tiers:

| Tier | Min CAGR | Max DD | Min Calmar | Min PF | หมายเหตุ |
|---|---:|---:|---:|---:|---|
| Survival Research | 0% | 10% | 0 | - | research only |
| Conservative Forex | 12% | 15% | 0.8 | 1.15 | ขั้นต่ำให้เริ่มน่าสนใจสำหรับ Forex |
| Balanced Worth-The-Risk | 20% | 15% | 1.0 | 1.20 | default profile |
| Aggressive Research | 35% | 25% | 1.2 | 1.25 | research/demo only |
| Challenge Mode | 100% | 30% | - | - | research only, not baseline |

Default target:

`Balanced Worth-The-Risk`

## Recommended Project Target

เป้าหมายระยะวิจัยที่เหมาะสมกว่า ordinary investment:

- CAGR 20-30%
- max drawdown <= 15%
- Calmar >= 1.0
- profit factor >= 1.20
- validation และ out-of-sample ต้อง pass ทั้งคู่

ตัวเลขนี้ยังไม่ใช่การรับประกันกำไร แต่เป็นกรอบคัดกรองว่า strategy คุ้มพอจะวิจัยต่อหรือไม่

## Current Baseline Assessment

Baseline:

- EURUSD H1
- normal losing-streak gate
- RunId: `run_20260621_214917`

ผล validation และ out-of-sample:

- validation net profit: +61.38 บน deposit 10000
- out-of-sample net profit: +41.03 บน deposit 10000
- validation + OOS net profit: +102.41
- annualized return ประมาณ 0.70%
- CAGR approximation ประมาณ 0.70%
- max relative drawdown ประมาณ 0.63%
- Calmar ประมาณ 1.11
- trade count validation + OOS = 167

Classification:

`BELOW_FOREX_RISK_PREMIUM`

ความหมายคือผลเป็นบวกและ drawdown ต่ำ แต่ return ยังเล็กเกินไปเมื่อเทียบกับความเสี่ยง Forex จึงยังไม่ควรเพิ่ม lot และยังไม่ควรเริ่ม demo forward

## ทำไม $100 ไป $1000 เป็น Challenge Mode

การพยายามทำ $100 เป็น $1000 คือเป้าหมายประมาณ 10 เท่า ซึ่งเป็น challenge mode ไม่ใช่ baseline system target

ถ้าใช้เป็น baseline จะกดดันให้ระบบเพิ่ม risk, lot, leverage หรือ frequency เกินความปลอดภัย เป้าหมายแบบนี้ควรอยู่ใน research-only หรือ challenge-only framework เท่านั้น

## Output ที่เกี่ยวข้อง

- `research/results/annual_target_assessment.md`
- `research/results/annual_target_scores.csv`
- `research/target_profile.json`

## สรุป

EURUSD H1 normal gate ยังเป็น baseline สำหรับ research ต่อ แต่ยังไม่ถือว่า worth-the-risk สำหรับ Forex premium

ขั้นต่อไปควรมุ่งปรับปรุง edge quality, regime/session/exit behavior และ trade quality ก่อนคิดเรื่องเพิ่ม exposure size

Checkpoint นี้ไม่มีการ optimize parameter, ไม่มีการเพิ่ม lot/risk, ไม่มีการเพิ่ม strategy ใหม่ และไม่มีการ claim profitability
