# Checkpoint X: Gold 2-5% Monthly Research Framework

วันที่จัดทำ: 2026-07-04

## สถานะของ checkpoint นี้

Checkpoint X เป็นเอกสารวางแผนวิจัยเท่านั้น

Checkpoint นี้ไม่ใช่สูตรทำกำไร ไม่ใช่คำแนะนำการลงทุน ไม่ใช่การอนุมัติให้เทรดจริง และไม่ใช่การอนุมัติให้รัน MT5 Strategy Tester

สิ่งที่ไม่ได้ทำ:

- ไม่แก้ EA/source code
- ไม่แก้ presets
- ไม่รัน MT5
- ไม่รัน Strategy Tester
- ไม่ optimize parameter
- ไม่เพิ่ม lot/risk
- ไม่เปิด demo/live forward test
- ไม่ claim profitability

## เป้าหมายที่ผู้ใช้สนใจ

ผู้ใช้สนใจการวิจัยทอง (`GOLD#` / `GOLDm#`) เพราะทองมีโอกาสเคลื่อนไหวแรง และอาจเหมาะกับระบบที่มีวินัยมากกว่าการเทรดด้วยอารมณ์

เป้าหมายเชิงวิจัย:

- ศึกษาว่ามี framework ใดที่อาจเข้าใกล้ผลตอบแทน 2-5% ต่อเดือนโดยไม่ทำให้ทุนเสียหายเกินรับได้
- ไม่บังคับให้ระบบต้องทำ 2-5% ทุกเดือน
- ยอมรับว่าบางเดือนอาจไม่มีกำไร หรืออาจต้องหยุดเมื่อระบบชน risk gate
- ให้ capital preservation สำคัญกว่า monthly target

## คำเตือนเรื่อง 2-5% ต่อเดือน

2-5% ต่อเดือนเป็นเป้าหมายสูงสำหรับระบบ trading โดยเฉพาะทองที่มีความผันผวนและ leverage สูง

โดยประมาณ:

- 2% ต่อเดือนแบบทบต้นใกล้เคียง 26.8% ต่อปี
- 5% ต่อเดือนแบบทบต้นใกล้เคียง 79.6% ต่อปี

ดังนั้นเป้าหมายนี้ควรถูกจัดเป็น `AGGRESSIVE_RESEARCH_TARGET` ไม่ใช่ `BASELINE_TARGET` และไม่ควรใช้เป็นเหตุผลให้เพิ่ม lot/risk อัตโนมัติ

## สิ่งที่คนทั่วโลกนิยมใช้กับทอง

จากแนวทางที่พบทั่วไปในตลาดทอง/CFD/futures/forex-style execution แนวคิดยอดนิยมมักแบ่งเป็นกลุ่มดังนี้:

1. Trend following / momentum

   ใช้แนวโน้มหลัก เช่น EMA slope, ADX, higher high / lower low, Donchian/channel breakout หรือ moving average alignment เพื่อเกาะรอบใหญ่ของทอง

2. Breakout

   ใช้การทะลุ high/low ของช่วงเวลา เช่น London open, New York open, previous day high/low, Asian range breakout หรือ volatility expansion

3. Mean reversion

   ใช้เมื่อ regime เป็น sideway เช่น Bollinger Band, VWAP deviation, RSI extreme หรือ price returning to mean แต่ต้องมี stop ชัดเจน เพราะทองสามารถ trend ต่อแรงได้

4. Pullback continuation

   รอราคาย่อเข้าหาโซน EMA / structure / previous breakout แล้วเข้าเมื่อ momentum กลับมา ไม่ไล่ราคาในจุดที่ risk/reward แย่

5. Multi-timeframe filter

   ใช้ H4/D1 เป็น direction filter และใช้ H1/M30/M15 เป็น execution/diagnostic timeframe เพื่อลดการสวน trend ใหญ่

6. Session filter

   แยกพฤติกรรม Asia, London, New York, และ overlap เพราะ liquidity และ volatility ของทองต่างกันในแต่ละ session

7. Event / macro filter

   ระวัง CPI, NFP, FOMC, interest-rate expectations, USD, real yields, geopolitical risk และ ETF/investment flow เพราะทองตอบสนองเร็วต่อข่าวเศรษฐกิจและการเมือง

8. ATR / volatility-based stop and sizing

   ใช้ ATR หรือ volatility regime เพื่อวาง SL/TP และคำนวณ lot ให้สอดคล้องกับความผันผวนจริง ไม่ใช้ fixed stop เดียวกับทุกตลาด

9. Strict risk gate

   มืออาชีพมักไม่ปล่อยให้หนึ่งไอเดียทำลายบัญชี จึงต้องมี max daily loss, weekly loss, monthly stop, max drawdown, losing streak pause, spread/slippage filter และ no-trade unsafe regime

## มุมมองเรื่อง "เซ้น" ของมนุษย์กับ AI

มนุษย์บางคนมีประสบการณ์หรือ pattern recognition ที่เรียกว่าเซ้น แต่เซ้นมีปัญหาสำคัญ:

- อาจเกิดจากประสบการณ์จริง
- อาจเกิดจาก hindsight bias
- อาจเป็นการหลอกตัวเองหลังเห็นผลลัพธ์แล้ว
- มักวัดซ้ำได้ยาก
- มักควบคุมอารมณ์ยากเมื่อเสียเงินจริง

ระบบ AI/EA ไม่มีเซ้นแบบมนุษย์ แต่มีข้อดี:

- ทำตามกฎซ้ำได้
- ไม่ revenge trade
- ไม่เพิ่ม lot เพราะอยากเอาคืน
- บันทึกเหตุผลได้
- ตรวจย้อนหลังได้

แนวทางที่เหมาะคือแปลง "เซ้น" ให้เป็น diagnostic rules ที่วัดได้ เช่น trend strength, volatility expansion, session, spread, drawdown concentration, news window, และ exit behavior

## Gold ต้องเป็น instrument class แยก

ห้ามใช้ parameter ของ EURUSD กับทองโดยตรง

Gold profile ต้องแยกจาก forex profile:

- actual symbol อาจเป็น `GOLD#` หรือ `GOLDm#`
- ต้องใช้ `_Symbol` และ broker metadata จริง
- ต้องอ่าน tick size, tick value, point, contract size, lot step, min lot, stop level, freeze level จาก broker
- ต้องไม่ force broker minimum lot ถ้าเกิน risk budget
- ต้องมี risk-budget review ก่อนทุก research run
- ต้องไม่ถือว่า deposit 10,000 หรือ 30,000 เพียงพอสำหรับทองโดยอัตโนมัติ

## Proposed target tiers

Checkpoint X เสนอ target tier สำหรับการวิจัยทอง:

| Tier | Monthly Return Target | Max Monthly Loss Stop | Max Relative Drawdown | สถานะ |
| --- | ---: | ---: | ---: | --- |
| Survival Gold Research | 0.5-1.5% | 3% | 8-10% | เหมาะเป็น baseline |
| Conservative Gold Research | 1-2% | 4% | 10-12% | วิจัยต่อได้ |
| Aggressive Gold Research | 2-5% | 6-8% | 12-18% | ต้องผ่าน gate หนัก |
| Challenge Mode | >5% | >8% | >18% | ไม่แนะนำในระบบหลัก |

เป้าหมาย 2-5%/เดือนควรอยู่ใน `Aggressive Gold Research` และต้องไม่ข้าม risk gate

## Minimum risk rules for any future Gold research

ก่อนมีการรัน MT5 ในอนาคต ต้องกำหนดกติกาขั้นต่ำ:

- `InpRequireStrategyTester=true`
- `InpDemoSafeMode=true`
- live/demo chart execution ยังไม่อนุมัติ
- risk per trade เริ่มต่ำมาก เช่น 0.05-0.15% สำหรับ Gold research
- max open positions = 1
- no martingale
- no uncontrolled grid
- no recovery lot multiplication
- no force minimum lot
- no trade if spread/slippage is unsafe
- no trade if calculated lot below broker minimum and forcing lot would violate risk
- stop after losing streak
- daily/weekly/monthly/drawdown kill switch
- event blackout window สำหรับข่าวแรงต้องถูกวิจัยก่อนเปิดใช้จริง

## Candidate research directions

Checkpoint X ยังไม่อนุมัติให้ implement แต่จัดลำดับไอเดียไว้ดังนี้:

1. Gold Regime Diagnostic Expansion

   ตรวจว่า trend, breakout, sideway, unsafe เกิดช่วงเวลาใด และ spread/slippage กระจุกตัวตรงไหน

2. Gold Session Breakout Diagnostic

   วัด Asian range, London breakout, New York continuation, false breakout และ drawdown by session

3. Gold Trend Pullback Diagnostic

   วัด pullback เข้า EMA/structure แล้ว momentum กลับมาหรือไม่ โดยยังไม่เปิด order

4. Gold Event Risk Filter

   วัดผลกระทบของ CPI, NFP, FOMC, rate decision, USD shock ต่อ SL/TP/spread/slippage

5. Gold Exit Research

   วัด initial SL loss, breakeven, trailing profit, TP hit, realized R และ whether TP too far / SL too close

6. Price Action / Fibo Gold Diagnostic

   ใช้ได้เฉพาะ diagnostic-only ก่อน ห้าม pending order จนกว่าจะพิสูจน์ no-trade path และ artifact production ได้

## Research gate before any trading logic change

ก่อนเปลี่ยน logic หรือเพิ่ม strategy ต้องมีข้อมูล:

- trade-level ledger
- session attribution
- spread/slippage attribution
- risk gate attribution
- drawdown concentration
- exit telemetry
- regime distribution
- broker minimum lot / deposit sufficiency
- train / validation / out-of-sample
- annual target / Calmar / drawdown / PF / trade count

## Why this is not optimization

Checkpoint X ไม่เลือก parameter และไม่เลือกสูตรเพื่อให้ backtest สวย

สิ่งที่ทำคือ:

- จัดหมวดหมู่แนวทางที่นิยม
- แยก Gold เป็น instrument class
- วาง target/risk tier
- ระบุข้อมูลที่ต้องเก็บก่อน implementation
- ป้องกันการหลอกตัวเองจากเป้าหมายรายเดือน

## Recommended next safe checkpoint

Checkpoint Y ควรเป็น docs-only หรือ diagnostic-only planning:

`Checkpoint Y: Gold Diagnostic Data Requirements and No-Trade Signal Logging Plan`

Checkpoint Y ยังไม่ควรรัน MT5 จนกว่า Checkpoint W retry/artifact path process จะผ่านและระบบ artifact production เชื่อถือได้

## References

- CME Group Gold Futures: `https://www.cmegroup.com/markets/metals/precious/gold.contractSpecs.html`
- World Gold Council Gold Demand Trends: `https://www.gold.org/goldhub/research/gold-demand-trends`
- Investopedia Stop-Loss Strategies: `https://www.investopedia.com/stop-loss-strategies-that-actually-work-11988839`
- Investopedia Position Sizing: `https://www.investopedia.com/articles/trading/09/determine-position-size.asp`
- Investopedia Forex Leverage: `https://www.investopedia.com/ask/answers/06/forexleverage.asp`
