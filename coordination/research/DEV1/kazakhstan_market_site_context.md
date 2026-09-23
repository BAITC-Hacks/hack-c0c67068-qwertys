# Kazakhstan wind-forecasting domain context: market rules, Shelek/Nurly site, local wind climate

Research date: 2026-09-23. Every fact is dated where the source allows. **Main finding:** the two turbine coordinates in the case (43.645150, 78.535604 and 43.643198, 78.538828) match the **Samruk-Green Energy 5 MW "ВЭС 5 МВт, п. Нурлы"** pilot plant: 2 × Goldwind GW109/2500, hub 80 m. This is not the 60 MW Shelek wind farm, which lies about 18 km to the NE.

---

## 1. Electricity market structure 2023–2026 and forecast/imbalance obligations for wind farms (ВЭС)

### Takeaway
Since 1 July 2023 Kazakhstan has run a **Unified Buyer (Единый закупщик) model**, with the Unified Buyer role held by ТОО «РФЦ по ВИЭ». It buys planned volumes day-ahead through KOREM's platform, and a **real-time hourly balancing market** runs alongside it. KOREM is the balancing market settlement centre (РЦ БРЭ) and KEGOC is the system operator. Wind and solar plants whose PPAs were signed **before 1 July 2023** carry no imbalance cost (coefficient = 1). The Unified Buyer absorbs their imbalances and socialises the cost. Plants whose PPAs were signed **after 1 July 2023** pay for imbalances at 1.3× / 0.7× their PPA price. RES daily schedules are due by **08:00 Astana time on D-1**. The rules were amended again in 2024, 2025 and twice in 2026.

### Cited Findings
**Market model and actors**
- Amendments to the Law «Об электроэнергетике» took effect on 1 July 2023. They introduced a Unified Buyer and a real-time balancing market. The target model is centralised buying and selling of **planned** volumes. ТОО «Расчетно-финансовый центр по поддержке ВИЭ» (РФЦ) was named Unified Buyer. It is a KEGOC subsidiary. — [rfc.kz Единый закупщик](https://rfc.kz/ru/single-purchaser-of-electricity/); [informburo: Дочка KEGOC стала единым закупщиком](https://informburo.kz/novosti/dochka-kegoc-stala-edinym-zakupshchikom-elektroenergii-v-kazahstane.html); [adilet: Об определении единого закупщика](https://adilet.zan.kz/rus/docs/V1800017471)
- KEGOC describes the post-July-2023 model as follows. The Unified Buyer buys all domestic generation one day ahead, except intra-group deals. A balancing market settles hourly imbalances in real time. A capacity market and an ancillary-services market run alongside. KEGOC runs a "modernized hardware-software complex" for the balancing market, with Unified Buyer and settlement-centre modules. Balancing market system portal: https://bems.kegoc.kz/. Page updated 16.09.2026. — [KEGOC: Электроэнергетика Казахстана — ключевые факты](https://www.kegoc.kz/ru/electric-power/)
- The Unified Buyer buys electricity day-ahead from domestic plants through auctions on KOREM's centralised-trading e-platform. RES with long-term contracts get priority. — [search summary of KEGOC/RFC pages, e.g. KEGOC key facts](https://www.kegoc.kz/ru/electric-power/); [QazaqGreen expert opinion, 29.05.2024](https://qazaqgreen.com/journal-qazaqgreen/expert-opinion/2005/)
- AO «KOREM» was designated balancing market settlement centre (РЦ БРЭ) by Minister of Energy order of **6 June 2023**. It runs centralised purchase and sale of balancing electricity and negative imbalances. KOREM handled about **5.8 bn kWh** of negative-imbalance and balancing-energy purchases from July to December 2023. — [KOREM РЦ БРЭ page](https://www.korem.kz/rus/sc_bem/bre_offsets/) (via search summary); [eenergy.media](https://eenergy.media/news/30142) (via search summary)
- Scale of the Unified Buyer, from 2025 financials published 23.07.2026: revenue **1.65 trn tenge** (1.39 trn in 2024), of which electricity sales 1.36 trn, capacity service 188.3 bn and **imbalance settlement revenue 92.3 bn tenge**. RES support tariffs in 2025 were **20.28–34.77 tg/kWh** and market average prices 16.36–34.65 tg/kWh. Profit was 5.2 bn tenge in 2025 against 12.4 bn in 2024. — [Kursiv, 23.07.2026](https://kz.kursiv.media/2026-07-23/zhnb-edinyi-zakupshhik-elektroenergii-kazahstana-vdvoe-sokratil-pribyl/)

**Imbalance responsibility for RES**
- The RFC is balance provider for every RES plant it holds a contract with, and it settles their imbalances financially. RES with contracts signed **before 1 July 2023 are not responsible** for their imbalances. RES signing with РФЦ **after 1 July 2023** are financially responsible for positive and negative imbalances through increasing and decreasing coefficients. — [QazaqGreen, 03.09.2024](https://qazaqgreen.com/journal-qazaqgreen/industry-news/2242/); [QazaqGreen expert opinion (K. Ilyusizova, Egen Gregory), 29.05.2024](https://qazaqgreen.com/journal-qazaqgreen/expert-opinion/2005/)
- For pre-2023 PPAs the coefficient is "равный единице на весь период действия PPA". For new PPAs:
  - Under-delivery (positive imbalance: plan > actual): the plant buys balancing electricity at **PPA price × increasing coefficient**.
  - Over-delivery (negative imbalance): the plant sells the excess at **PPA price × decreasing coefficient**.
  - As of May 2024 the **tolerance band ("размер допустимого отклонения") had not yet been set**.

  — [QazaqGreen expert opinion, 29.05.2024](https://qazaqgreen.com/journal-qazaqgreen/expert-opinion/2005/)
- The coefficients are **1.3 (upward) and 0.7 (downward)** for RES with post-July-2023 contracts. — [Inbusiness, 11.06.2025](https://inbusiness.kz/ru/news/edinyj-zakupshik-ushel-v-ubytok-iz-za-zelenoj-energii)
- **Cost of RES imbalances to the Unified Buyer.** In 2024 РФЦ's balancing-market expenses for RES deviations were **7,546,098,188 tenge**, against 5.40 bn tenge of income, a deficit of about 2.15 bn. In January–April 2025 expenses were 4.03 bn against 23.62 bn income. From 1 Jan 2025, positive balancing-market differences are credited against RFC's negative imbalances regardless of hourly direction. Balancing costs are spread across wholesale market participants, but household suppliers and crypto-miners are excluded. — [Inbusiness, 11.06.2025](https://inbusiness.kz/ru/news/edinyj-zakupshik-ushel-v-ubytok-iz-za-zelenoj-energii)

**General balancing-market rules (Order No. 112 of 20.02.2015)**
- Text as consolidated at 01.07.2024, read from a mirror because adilet is JS-rendered:
  - An imbalance is "разность планового и фактического сальдо генерации-потребления" in kWh (p.2 sub-p.27; p.78).
  - A "critical deviation" is a deviation of more than **20%** of actual over planned balance (p.90-1, 90-2). Above it, reduced price coefficients apply (about −30%).
  - Positive imbalances are priced at the forecast Unified Buyer price, or at the plant's own cap tariff for plants that have one (p.90).
  - The negative-imbalance price formula uses a coefficient K that differs between "control" and ordinary hours (p.92).
  - Mandatory participants submit bids for each hour of the next day no later than 1 h before the end of the current day (p.40). Bid corrections are allowed up to **10 min before the hour** (p.53).

  — [cdb.kz mirror of Order 112](https://cdb.kz/sistema/pravovaya-baza/ob-utverzhdenii-pravil-funktsionirovaniya-balansiruyushchego-rynka-elektricheskoy-energii/); official text: [adilet V1500010532](https://adilet.zan.kz/rus/docs/V1500010532)
- The 2024 reform changed the daily-schedule approach: "штрафы до 30% за отклонения свыше 20% от плановой генерации/потребления". — [QazaqGreen, 03.09.2024](https://qazaqgreen.com/journal-qazaqgreen/industry-news/2242/)
- **Amendment of 25.06.2026**, in force from 10.07.2026:
  - Subjects may pass balance responsibility to a **single balance provider per balancing zone**, with contracts of at least one calendar month.
  - **RES with long-term Unified Buyer contracts may transfer balance responsibility to the Unified Buyer.**
  - Notice to РЦ БРЭ is due by the 20th of the month.
  - Each balance provider other than the Unified Buyer is capped at 750 mln kWh of positive imbalances per period.
  - Balance providers must hold guarantee deposits.

  The consolidated text shows revision date 25.06.2026. — [zakon.kz, 01.07.2026](https://www.zakon.kz/pravo/6523205-pravila-raboty-balansiruyushchego-rynka-elektroenergii-izmenilis-v-kazakhstane.html); [zakon.uchet.kz V1500010532](https://zakon.uchet.kz/rus/docs/V1500010532)

**RES-specific schedule and forecast deadlines (Order on centralised purchase of RES electricity by the Unified Buyer, V1500010662)**
- Consolidated revision 30.06.2026; last substantive amendment Order No. 367-н/қ of 30.09.2025.
  - RES producers submit daily bids to the balancing market system **by 08:00 Astana time for the next operational day** (p.9).
  - Annual production forecast with monthly split is due **by 1 October** (p.8(1)).
  - Monthly actuals are due by the 5th of the following month (p.8(2)).
  - Payment is based on **actual meter-verified output** delivered to the grid, from automated commercial metering (АСКУЭ) reporting to regional dispatch centres (p.5, 6, 11). There is no payment without working meters.
  - p.18-1 covers new auctioned projects of ≥499 MW with mandatory storage. It mentions "увеличение понижающих и повышающих коэффициентов; снижение предельного диапазона", which implies a coefficient and band structure in the balancing rules.

  — [zakon.uchet.kz V1500010662](https://zakon.uchet.kz/rus/docs/V1500010662); official: [adilet V1500010662](https://adilet.zan.kz/rus/docs/V1500010662)
- Expert summary from 2024: schedule deadline is 08:00 on the day before the operating day. Adjustments are allowed up to **2 hours before** the delivery hour. For new PPAs the Unified Buyer pays only the planned volume approved in the daily schedule, with a daily payment by 12:00 of the operating day. — [QazaqGreen expert opinion, 29.05.2024](https://qazaqgreen.com/journal-qazaqgreen/expert-opinion/2005/). This partly conflicts with the "payment on actual metered output" wording of V1500010662 p.11. The two may apply to different contract vintages. **Unresolved.**
- **Wholesale market rules change, Order of 23.02.2026, in force 14.03.2026.** RES, secondary-resource and waste-to-energy plants must sell **only to the Unified Buyer**, or inside their corporate group. Daily prepayment is due by 08:00 Astana time. Producers may not sell without automated metering. — [zakon.kz, 05.03.2026](https://www.zakon.kz/pravo/6509989-izmenilis-pravila-raboty-optovogo-rynka-elektroenergii.html); [prg.kz annotation 23.02.2026](https://prg.kz/document/?doc_id=39935104)

**Historic imbalance statistics (pre-2023 regime)**
- In 9M 2022 total RES imbalances were **1,751 mln kWh** on actual generation of **3,504.4 mln kWh**, about 50%.
  - By source: wind 1,182 mln kWh (67%), solar 489 mln kWh (28%), hydro 79 mln kWh.
  - **Average hourly deviation was 60.73% for wind**, 40.67% for solar and 22.88% for hydro.
  - РФЦ consolidated the daily schedules of 91 RES plants totalling about 2,094 MW.
  - March was the peak month: 249 mln kWh under-production and 220 mln kWh over-production.

  — [QazaqGreen analytics by G. Nalibayeva (CEO of РФЦ), 21.12.2022](https://qazaqgreen.com/journal-qazaqgreen/analitycs/864/)
- The 2020 imbalance volume was **660 mln kWh, valued at 21.3 bn tenge**, about 20% of RES electricity purchased. At that time actual output was not supposed to deviate by more than **±10% from the declared plan**. Forecasts were submitted 2–3 days ahead. Kazakhstan uses a **decentralised forecasting model**: each plant forecasts for itself, unlike China, where the system operator forecasts. Rule of thumb cited: 2 MW of RES needs about 1 MW of manoeuvring reserve. — [QazaqGreen expert opinion by Zh. Mominbayev, 21.04.2021](https://qazaqgreen.com/journal-qazaqgreen/expert-opinion/260/). **Possibly outdated.** The ±10% figure predates the 2023 reform and is not confirmed in current rules.

**RES auctions and tariffs**
- 2025 auction schedule: 26 May – 12 Nov 2025 with **1,200 MW of wind**. The wind ceiling price was **22.68 tg/kWh**. Winning bids fell to **18.72 tg/kWh**. — [QazaqGreen: график аукционов 2025](https://qazaqgreen.com/news/kazakhstan/2555/) (via search summary); [Inbusiness: два проекта ВЭС для южной зоны](https://inbusiness.kz/ru/last/dva-proekta-ves-otobrano-cherez-aukcion-dlya-yuzhnoj-zony-k)
- The Shelek 60 MW plant sells to ТОО «РФЦ по ВИЭ» under a **15-year contract**. — [informburo, 13.09.2022](https://informburo.kz/fotoreportazh/kitaj-postroil-pod-almaty-vetropark-kotoryj-obespechit-energiej-60-tysyach-domov-no-deshyovoj-ona-ne-budet)

**Direction of reform (2026)**
- The competition agency (АЗРК) proposes liquidating or transforming the Unified Buyer, and phasing out direct and indirect price regulation in 2029–2031. — [bes.media](https://bes.media/news/neftegaz-taksi-aviatsiya-i-marketpleysy-kak-azrk-predlagaet-menyat-krupnye-rynki-kazahstana/) (via search summary only)
- The Unified Buyer price fell from **35 to 27 tg/kWh** between June and July 2026. — [Inbusiness](https://inbusiness.kz/ru/news/elektroenergiya-rezko-podeshevela-v-kazahstane-posrednikam-perekryli-lazejki) (via search summary only)
- KEGOC in September 2026: wind and solar are about **7% of generation from 170 stations**, with large differences between maximum and minimum output within hours and days. Participants often deviate from their daily schedules, and that forces balancing-market trades. The biggest weakness is incomplete АСКУЭ coverage, so load profiles are used instead of metered data. Eight plants are on automatic frequency control (AFRM). Russia's grid sets the frequency. — [Inbusiness, 09.09.2026](https://inbusiness.kz/ru/news/kegoc-raskryl-slaboe-mesto-energorynka-kazahstana)

### Inferences
- **Why hourly D-1 forecasts matter, 2023–2026:**
  - Every RES plant must submit an **hourly generation schedule for day D by 08:00 Astana time on D-1**. Its horizon runs from about 16 h (hour 00 of D) to about 40 h (hour 23 of D), which is exactly the 24–48 h case horizon.
  - Deviations settle hourly on the balancing market.
  - For post-2023 PPAs the **penalty is roughly 0.3 × PPA price per kWh of absolute hourly deviation**, and it is symmetric. Buying the shortfall at 1.3P loses 0.3P. Selling the surplus at 0.7P forgoes 0.3P.
  - For pre-2023 PPAs the plant pays nothing directly. The Unified Buyer absorbs the cost (7.55 bn tenge in 2024) and passes it to wholesale buyers. The forecast still matters for system cost and reputation, and very likely for future contract terms.
- From 10.07.2026 RES may formally hand balance responsibility to the Unified Buyer. The Unified Buyer therefore has a growing incentive to demand, or itself produce, better RES forecasts. Samruk-Energy's AI forecasting launch, due end-2026 (see §6), fits this trend.
- Metering is **net delivery to the grid (АСКУЭ at the connection point)**. Turbine SCADA "active power" is gross output at the turbine terminals. The gap is transformer and line losses plus own consumption. A forecast built on SCADA should be calibrated to the АСКУЭ meter if it is used for market schedules.

### Gaps
- The official adilet texts are JS-rendered and could not be read directly. Rule details come from mirrors (cdb.kz, zakon.uchet.kz) and secondary summaries.
- I could not confirm from primary text:
  - the exact current tolerance band ("предельный диапазон") for RES under post-2023 contracts;
  - whether the 1.3/0.7 coefficients were changed in 2025–2026.
- No official statement was found of a **quantitative forecast-accuracy requirement** (for example a maximum MAPE) for wind or solar in current (2026) rules. Only the historic ±10% (2021) and the general 20% "critical deviation" threshold were found.
- The contract vintage and tariff of the Nurly 5 MW plant (§2) are unknown. It is presumably pre-2023, since it was commissioned in 2018–2020, so imbalance responsibility probably sits with the Unified Buyer.
- I found no data on the gross vs net loss ratio for Nurly.

---

## 2. Wind farms in the Shelek corridor, and which one matches the case coordinates

### Takeaway
The case turbines match the **Samruk-Green Energy "ВЭС 5 МВт" at Nurly village**: 2 × Goldwind GW109/2500 direct-drive PMSG, hub 80 m, rotor 109 m, built in 2018 and formally commissioned on 20.07.2020. thewindpower.net places "Nurly wind farm" (2 × GW109/2500) at 43.6442 N, 78.5369 E, within about 100 m of the midpoint of the two case coordinates. Goldwind SCADA (Chinese) explains the translated Chinese column names. The larger **Shelek 60 MW** plant (Energia Semirechya: PowerChina/Hydrochina 75%, Samruk-Energy 25%) has 24 × Goldwind GW130-2.5 at 90 m hub and lies about 18 km to the NE (43.7117, 78.7440).

### Cited Findings
**ВЭС 5 МВт Нурлы (Samruk-Green Energy): best match for the dataset**
- Plant data from the owner:
  - Location: п. Нурлы, Енбекшиказахский район, Алматинская область.
  - **2 turbines of 2.5 MW** from XINJIANG GOLDWIND Science & Technology. They use a **gearless multipole synchronous (PM direct-drive) generator** and a 3-blade rotor with **109 m diameter**.
  - **Hub 80 m**, on a tubular conical steel tower.
  - Operating range 3–25 m/s; **rated wind speed 10.3 m/s**.
  - Expected generation about **16 mln kWh/yr** on one owner page and 17 mln kWh on another.
  - Built under a KZ–China grant agreement of 26.09.2011. Construction ran March–November 2018. **Commissioned 20 July 2020.**

  — [samruk-green.kz: Эксплуатация ВЭС 5 МВт (п. Нурлы)](https://samruk-green.kz/ru/projects/1047-20210219-133650); [samruk-green.kz news 30.11.2018](https://samruk-green.kz/ru/press-center/news/858-20181130-205039)
- Launch announced on 04.12.2018 as a Samruk-Energy 5 MW wind farm "район поселка Нурлы Енбекшиказахского р-на". — [inform.kz, 04.12.2018](https://www.inform.kz/ru/solnechnuyu-i-vetrovuyu-elektrostancii-zapustili-v-almaty-i-almatinskoy-oblasti_a3473332)
- thewindpower.net "Nurly" entry (database updated 01.04.2020):
  - 5 MW, **2 × Goldwind GW109/2500**.
  - Coordinates **43°38'39.2" N, 78°32'13" E** (= 43.6442, 78.5369).
  - "Shelek wind farm" is listed as about 18 km away.

  — [thewindpower.net: Nurly](https://www.thewindpower.net/windfarm_en_30769_nurly.php)
- GW109/2500 generic specifications: 2,500 kW; rotor 109 m (9,516 m²); cut-in 3 m/s, rated 10.3 m/s, cut-out 25 m/s; max rotor speed 13.5 rpm; direct drive with PM synchronous generator. The database lists a 90 m hub variant; the site uses 80 m. — [wind-turbine-models.com: GW 109/2500](https://en.wind-turbine-models.com/turbines/1193-goldwind-gw-109-2500); [thewindpower.net GW109/2500](https://www.thewindpower.net/turbine_en_896_goldwind_gw109-2500.php)
- Samruk-Green Energy is a group company of АО «Самрук-Энерго». — [samruk-energy.kz: ТОО «Samruk Green Energy»](https://samruk-energy.kz/ru/company/group-of-companies/too-samruk-green-energy)

**Shelek wind farm 60 MW (ТОО «Энергия Семиречья»)**
- Project: "Строительство ВЭС в Шелекском коридоре мощностью 60 МВт с перспективой расширения до 300 МВт".
  - Енбекшиказахский район, near **п. Нурлы**.
  - 24 × 2.5 MW; expected **225.75 mln kWh/yr**.
  - The turbine was chosen for a cold continental climate (**−30…+43 °C**), seismicity up to 10 points and IEC **wind class II**.

  — [Kapital.kz](https://kapital.kz/economic/80092/samruk-energo-stroit-vetrovuyu-stantsiyu-v-energodefitsitnom-regione.html); [Samruk-Energy AR2022](https://ar2022.samruk-energy.kz/ru/strategic-report.html); [Forbes.kz](https://forbes.kz/process/energetics/bliz_almatyi_stroyat_novuyu_vetryanuyu_elektrostantsiyu/)
- **Turbine: Goldwind GW130-2.5MW** PMDD, 24 units. The first batch was delivered around August 2019, with expected utilisation above 3,800 equivalent hours. — [windfair, 05.08.2019](https://w3.windfair.net/wind-energy/news/32244-goldwind-kazakhstan-powerchina-turbine-wind-energy-wind-farm-smart-wind-turbine-power-supply-china)
- dprom.kz, 06.10.2022:
  - Goldwind, hub **90 m**, rotor 128 m (64 m blades).
  - Plant 160 km from Almaty.
  - Mean wind at 50 m **7.8 m/s**, power density **310 W/m²**.
  - Cut-in 2.5, rated 10, cut-out 25 m/s; about 3,100 full-load hours.
  - Cost **$80 mln**: 80% Chinese bank loan over 15 years; equity split PowerChina 75% / Samruk-Energy 25%.

  — [dprom.kz](https://dprom.kz/trendy/vetropark-v-shelekskom-koridore-proekt-kitaya-v-kazahstane/). The rotor figure conflicts with the GW130 designation (130 m) and with time.kz's "blade 60 m", which would be about 120–130 m.
- informburo, 13.09.2022:
  - Hub 90 m; cost 37.4 bn tenge; IRR above 11.5%.
  - Buyer РФЦ по ВИЭ, 15-year PPA.
  - Wind: "better in autumn and spring, minimal in summer".

  — [informburo](https://informburo.kz/fotoreportazh/kitaj-postroil-pod-almaty-vetropark-kotoryj-obespechit-energiej-60-tysyach-domov-no-deshyovoj-ona-ne-budet)
- Construction started 27.06.2019. Full-capacity grid connection came in **July 2022**; the acceptance act for industrial operation was also signed in July 2022. — [WindInsider, 04.11.2024](https://windinsider.com/2024/11/04/powerchinas-shelek-wind-farm-in-kazakhstan-in-surpasses-500-million-kwh-in-cumulative-power-generation/); [sk.kz](https://sk.kz/press-center/news/73476/?lang=en)
- **2024 generation was 228 mln kWh**, reached on 26.12.2024 and meeting target. Cumulative output passed 500 mln kWh by November 2024. — [WindInsider, 02.01.2025](https://windinsider.com/2025/01/02/powerchinas-shelek-wind-farm-in-kazakhstan-achieves-2024-power-generation-target/)
- Global Energy Monitor record:
  - Coordinates **43.7117, 78.7440** (marked "exact").
  - Operating since 2022; operator Energia Semirechya.
  - Owners: Samruk-Energo 25%, Hydrochina Corp 50%, PowerChina Resources 10%, PowerChina Chengdu Engineering 15%.

  — [GEM wiki](https://www.gem.wiki/Shelek_(Energia_Semirechya)_wind_farm)
- thewindpower.net "Shelek": 43°42'42.1" N, 78°44'38.2" E; 20 × **Envision 2.5-131**, 50 MW. It also states total KZ wind capacity of 1,909 MW at end-2025 and 55 MW operating in the "Almaty zone". — [thewindpower.net: Shelek](https://www.thewindpower.net/windfarm_en_27785_shelek.php). **This conflicts** with the Goldwind GW130 × 24 / 60 MW figures from the owner and vendor. The entry may be wrong or may describe a different project.
- Site geography: "mountains on both sides and wind flowing between them like a draft". The area could host up to about 2,000 MW. — [time.kz, 20.09.2022](https://time.kz/articles/territory/2022/09/20/energiya-regiona)

**Other nearby projects**
- ТОО «ВЭС Нурлы» (VES Nurly LLP) is a separate private project:
  - **8.45 MW, 13 turbines**, in the Shelek corridor.
  - 43,225 MWh/yr.
  - Cost $8.7 mln, of which $4.7 mln came from Bank CenterCredit under EBRD GEFF. The company was founded in 2016.
  - Turbine model not disclosed.

  — [EBRD GEFF Kazakhstan](https://ebrdgeff.com/kazakhstan/projects/new-turbines-for-power-plant-in-almaty-region/); [kompra.kz: ТОО ВЭС НУРЛЫ](https://kompra.kz/organization/tovarischestvo-s-ogranichennoj-otvetstvennostju-ves-nurly_160340006724)
- Planned Shelek expansion: phase 2 memorandum to reach **300 MW**, about 120 towers. — [informburo](https://informburo.kz/fotoreportazh/kitaj-postroil-pod-almaty-vetropark-kotoryj-obespechit-energiej-60-tysyach-domov-no-deshyovoj-ona-ne-budet); [Samruk-Energy news](https://www.samruk-energy.kz/ru/press-center/company-news?view=article&id=978:proekt-stroitelstvo-vetrovoj-elektricheskoj-stantsii-v-shelekskom-koridore-moshchnostyu-60-mvt-s-perspektivoj-rasshireniya-do-300-mvt&catid=12)

### Inferences
- **Coordinate match.** The midpoint of the case turbines is 43.64417 N, 78.53722 E. thewindpower's "Nurly" point is 43.64422 N, 78.53694 E, a difference of about 25 m. The two turbines are about **340 m apart (about 3.1 rotor diameters)**, on a roughly **NW–SE axis (bearing about 310°/130°)**. Two turbines, 5 MW and Goldwind with Chinese SCADA together make the dataset almost certainly **ВЭС 5 МВт Нурлы (Samruk-Green Energy)**. Normalised power = P / 2,500 kW per turbine.
- **Wake and layout implication.** The turbines stand on a NW–SE line and the prevailing winds are E/NE and W/SW. The inter-turbine axis is therefore about 40–85° off the main wind sectors, so direct full wakes should be uncommon. Partial wake is possible for ESE and WNW winds, with the turbines about 3 D apart. The two turbines' power difference as a function of direction is a useful diagnostic.
- **Capacity factor benchmarks.** The design figure is 16–17 GWh ÷ (5 MW × 8,760 h), a CF of about 37–39%. Shelek 60 MW produced 228 GWh in 2024, a CF of about 43%. The case data's seasonal CF of 0.23 (summer) to 0.51 (winter) is consistent with both. Hub height (80 m vs 90 m) and rotor size (109 m vs about 130 m) favour the larger Shelek machines. Shelek can serve as a regional sanity check, or a neighbour signal if its data ever becomes available.
- The design temperature range of −30…+43 °C for the Shelek machines is a proxy for site extremes. The GW109 at Nurly would face the same climate.

### Gaps
- There is no public source for the exact turbine coordinates, the Nurly plant's SCADA vendor settings, the power-curve file, or the GW109 IEC class at this site.
- Turbine model at VES Nurly LLP (8.45 MW) and its coordinates: not found.
- The Shelek rotor diameter (128 vs 130 m) and thewindpower's "Envision 2.5-131 / 50 MW" entry remain unresolved.
- No actual yearly generation was found for the Nurly 5 MW plant. The Samruk-Energy 2024 annual report PDF exceeded 10 MB and could not be fetched.

---

## 3. Local wind climate of the Shelek (Chilik) corridor

### Takeaway
Public, citable climatology for this exact site is thin. Several things are established:
- The corridor is a topographic **funnel between mountain ranges on the Ili valley side of the Zailiysky/Ketmen Tien Shan**, with high and steady winds.
- Reported mean speeds are about 7.8–8 m/s at 50 m and power density about 280–320 W/m².
- Winds are strongest in spring and autumn (one study says May) and weakest in summer (June–August).
- Design temperatures run −30…+43 °C.
- The Dzungarian Gate "Ибэ" wind is a cold-season, dry SE wind from China driven by a trans-mountain pressure gradient, and serves as a regional analogue.

I found no peer-reviewed wind rose, diurnal cycle or icing statistics for Shelek.

### Cited Findings
- Shelek corridor mean wind speed is **7.8 m/s at 50 m** and power density **310 W/m²**. — [dprom.kz, 06.10.2022](https://dprom.kz/trendy/vetropark-v-shelekskom-koridore-proekt-kitaya-v-kazahstane/)
- Officials describe the corridor's wind as "очень плотный и постоянный", about 8 m/s. Seasonally it is "better in autumn and spring; minimal in summer". — [informburo, 13.09.2022](https://informburo.kz/fotoreportazh/kitaj-postroil-pod-almaty-vetropark-kotoryj-obespechit-energiej-60-tysyach-domov-no-deshyovoj-ona-ne-budet)
- A Weibull study used **hourly data at 10 m height for 2013**. Findings:
  - Annual mean speed across the Shelek corridor ranges from **4.0 to 8.0 m/s**.
  - Weibull power density ranges from **280 to 320 W/m²**.
  - The highest speeds come in **May**; **June–August are the lowest**.

  — ["Evaluation of wind power potential in Shelek corridor (Kazakhstan) using Weibull distribution function", academia.edu](https://www.academia.edu/105549257/Evaluation_of_wind_power_potential_in_shelek_corridor_Kazakhstan_using_weibull_distribution_function). Only search snippets were available (403 on fetch); authors and year were not verified.
- A techno-economic study found Yereymentau, Fort Shevchenko and **Shelek** among the highest-potential KZ sites, with mean speeds above 8 m/s and wind availability above 90%. — [Pourasl & Khojastehnezhad, Proc. IMechE Part A, 2021](https://journals.sagepub.com/doi/10.1177/09576509211001598) (search snippet only; fetch blocked)
- The site is a funnel: "mountains on both sides and wind flowing between them like a draft". The land is barely usable for settlement or grazing because of the constant wind. — [time.kz, 20.09.2022](https://time.kz/articles/territory/2022/09/20/energiya-regiona)
- The corridor lies "на пути основного воздушного потока через Джунгарские ворота и Шелекский коридор". It is "почти не уступает Джунгарским воротам". — [search summary citing informburo/dprom](https://dprom.kz/trendy/vetropark-v-shelekskom-koridore-proekt-kitaya-v-kazahstane/)
- Design climate for the Shelek turbines: **−30…+43 °C**, seismicity up to 10 points, IEC wind class II. — [Kapital.kz](https://kapital.kz/economic/80092/samruk-energo-stroit-vetrovuyu-stantsiyu-v-energodefitsitnom-regione.html); [dprom.kz](https://dprom.kz/trendy/vetropark-v-shelekskom-koridore-proekt-kitaya-v-kazahstane/)
- **Dzungarian Gate analogue.** "Ибэ" (ebe/ebi) is a dry **south-easterly wind from China in the cold season**. "Сайкан" is a north-westerly wind during weather changes. The gate acts as an aerodynamic channel between the Balkhash-Alakol basin and the Dzungarian plain, and gusts reportedly reach 70 m/s. — [ru.wikipedia: Джунгарские Ворота](https://ru.wikipedia.org/wiki/%D0%94%D0%B6%D1%83%D0%BD%D0%B3%D0%B0%D1%80%D1%81%D0%BA%D0%B8%D0%B5_%D0%92%D0%BE%D1%80%D0%BE%D1%82%D0%B0)
- **UNDP measurements.**
  - Detailed UNDP-supported met studies of the **Dzungarian Gate and the Shelek corridor ran in 1998–2000**. Dzungarian Gate results: 9.7 m/s at 50 m and about 1,050 W/m².
  - The UNDP/GEF "Kazakhstan – Wind Power Market Development Initiative" presented the first **Wind Atlas of Kazakhstan** in Astana on **21.10.2009**. The atlas drew on 10 measurement points measured over 2 years (masts included Kordai, Karkaralinsk, Yereymentau, Fort Shevchenko, Arkalyk, Atyrau, Astana, Zhuzymdyk).

  — [Kazakhstan Today](https://www.kt.kz/rus/society/v_kazahstane_razrabotan_pervij_vetrovoj_atlas_1153500682.html); [gisa.ru](http://gisa.ru/57005.html) and AUES lecture notes ([libr.aues.kz PDF](https://libr.aues.kz/facultet/102_EEF/110_Elektricheskie_stantsiy,_seti_i_sistemi/194_Elektricheskie_stantsii_podstantsii/SPc2plkF5JZqmsavtY463weNjzHUby.pdf)), both via search summary.
- In 2006 the Deputy Minister of Energy named the Shelek corridor and the Dzungarian Gate the most promising wind sites. — [zonakz, 06.09.2006](https://zonakz.net/2006/09/06/solnce-vozdux-i-voda/)
- The Chilik (Shelek) River is a tributary of the Ili. It flows from the Ile Alatau / Kungey Alatau down into the Ili valley. — [Wikipedia: Chilik (river)](https://en.wikipedia.org/wiki/Chilik_(river))

### Inferences
- The bimodal E/NE (~45%) vs W/SW (~41%) direction split in the SCADA data fits **channelled flow along the ENE–WSW axis of the Ili valley**, between the Ile/Kungey Alatau to the south and the Ketmen/Dzungarian Alatau side to the north/east. The two modes likely reflect different synoptic regimes:
  - **Easterly: cold-season Siberian/Mongolian anticyclone outflow from Xinjiang/Dzungaria.** This is the same pressure-gradient mechanism as the Ибэ at the Dzungarian Gate. It is consistent with the higher winter CF (0.51).
  - **Westerly: frontal passages or cyclones from the west, possibly the Сайкан-type NW flow at the Gate.**

  Summer's weaker gradients plus thermally driven mountain-valley circulation fit the low summer CF (0.23) and the "minimal in summer" statements.
- For forecasting this means:
  - direction-regime-specific error behaviour is likely;
  - NWP models at about 9–25 km resolution will poorly resolve gap and channel acceleration, so local MOS or statistical correction by direction sector is needed;
  - regime changes around front passages (E↔W reversals) are likely the main source of large D-1 errors.

  These are inferences, not sourced findings.
- Cold-season icing is plausible at 555 m with −30 °C lows. I found no icing statistics, so treat low-power, high-wind, sub-zero SCADA periods as candidates to flag.

### Gaps
- There is **no Global Wind Atlas value** for 43.644 N, 78.537 E: the GWA web app is JS-only and was not queried. The case team can read it directly at https://globalwindatlas.info (100 m mean speed, power density, wind rose).
- No peer-reviewed **wind rose, diurnal cycle, föhn or icing** climatology was found for the Shelek/Chilik corridor. The UNDP 1998–2000 Shelek measurement results (numbers) were not retrievable. The OSCE CADGAT PDF could not be parsed.
- There is no Kazhydromet station climatology online for the Shelek or Chundzha stations.
- The Weibull paper's authors and year are unverified.

---

## 4. Timezone: UTC+6 → UTC+5 on 1 March 2024

### Takeaway
A government decree of **19 January 2024** amended the decree of 23 November 2000 and moved all of Kazakhstan to a single **UTC+5** zone from **00:00 on 1 March 2024**. Almaty and the eastern regions set clocks back one hour, from UTC+6. Market rules quote deadlines in **"время Астаны"**, which is now UTC+5. A SCADA clock left at fixed UTC+6 is therefore one hour ahead of market and local time for all data from 2024-03-01 onward.

### Cited Findings
- Kazakhstan unified on UTC+5 on 1 March 2024 by government decree of 19 January 2024, which amended the decree of 23 November 2000. Almaty and East Kazakhstan had used UTC+6 and moved back one hour at midnight on 1 March 2024. A 2024–2025 petition to "turn the time back" was rejected by the Ministry of Trade and Integration. IANA tzdata sets Asia/Almaty to UTC+5. — [Wikipedia: Time in Kazakhstan](https://en.wikipedia.org/wiki/Time_in_Kazakhstan)
- The Ministry of Trade and Integration proposed the switch on 7 December 2023. Astana, Almaty, Shymkent and several regions turned clocks back one hour on 1 March 2024. — [Interfax](https://interfax.com/newsroom/top-stories/98581/); [APA](https://en.apa.az/asia/kazakhstan-will-switch-to-a-single-time-zone-from-march-1-2024-423635)
- Microsoft published a Windows time-zone update for Kazakhstan 2024. — [Microsoft Tech Community](https://techcommunity.microsoft.com/blog/dstblog/kazakhstan-2024-time-zone-update-now-available/4100664)
- The time question remained politically debated in 2025. — [The Diplomat, 03.2025](https://thediplomat.com/2025/03/kazakhstan-buries-time-zone-issue/)
- Market deadlines are stated in Astana time: RES bids by 08:00 Astana time D-1, prepayment by 08:00 Astana time. — [zakon.uchet.kz V1500010662](https://zakon.uchet.kz/rus/docs/V1500010662); [zakon.kz, 05.03.2026](https://www.zakon.kz/pravo/6509989-izmenilis-pravila-raboty-optovogo-rynka-elektroenergii.html)

### Inferences
- **Data alignment.** SCADA "Статистическое время" at fixed UTC+6 equals local legal time before 2024-03-01 and is **local + 1 h** after. Convert everything to UTC internally. For market deliverables, output hourly schedules in UTC+5 (Astana time, the market clock).
  - NWP (GFS/ECMWF/ERA5) is in UTC, so UTC+6 SCADA needs a −6 h shift. Using −5 h for post-2024 SCADA would create a 1-hour lag error.
  - Diurnal features (e.g., solar-driven valley winds) are tied to solar time. Local solar noon at 78.54 E is about 12:46 UTC+5, or about 06:46 UTC.
  - Kazakhstan has no DST, so there are no seasonal jumps.
- The 08:00 D-1 deadline in UTC+5 is 03:00 UTC. The 00 UTC NWP run is usually available by about 04–06 UTC. **The deadline therefore likely forces use of the previous day's 12 UTC or 18 UTC runs**, a lead time of about 30–54 h to the end of day D. This is an inference about operational timing and should be verified against actual NWP availability.

### Gaps
- The decree number of 19.01.2024 was not captured, and the exact switch minute was not verified in the primary legal text.

---

## 5. Public Kazakhstan data sources relevant to wind forecasting

### Takeaway
Public data consists mostly of aggregates: KEGOC annual and market reports, РФЦ press releases on monthly and quarterly RES shares, and KOREM/РЦ БРЭ settlement pages. Plant-level hourly data is not openly published. The balancing-market portal bems.kegoc.kz exists but is for participants.

### Cited Findings
- National wind totals:

  | Year | Wind generation | Wind capacity | Other |
  |---|---|---|---|
  | 2024 | **4,497.6 mln kWh** | **1,525.7 MW** in 57 wind plants | Solar 1,895.6 mln kWh; small hydro 1,161.3 mln kWh. All RES: 7,555.1 mln kWh (6.4% of generation), 3,038.6 MW across 157 plants. 8 new RES plants (154.6 MW) added in 2024. |
  | 2025 | **5.38 bn kWh** | Grew from 1,570 to **2,059 MW** (+31%) | All RES 8.6 bn kWh, about 7–8% of generation. 2026 plan: 10 RES plants, 245 MW (4 wind). |

  — [KEGOC AR2024: баланс электроэнергии](https://ar2024.kegoc.kz/ru/electricity-balance.html); [Kursiv, 21.01.2026](https://kz.kursiv.media/2026-01-21/zhnb-vetrom-nadulo-proizvodstvo-elektroenergii-v-kazahstane-vyroslo-na-sotni-millionov-kvtch/); [Forbes.kz](https://forbes.kz/articles/kazahstan-vchetyre-raza-uvelichil-dolyu-vie-venergobalanse); [bes.media](https://bes.media/news/kazhdyy-dvenadtsatyy-kilovatt-chas-stal-zelenym-vie-kazahstana-vyrosli-za-chetyre-goda/) (via search summaries)
- 2024 system context: consumption exceeded generation by 2,080.1 mln kWh. Net imports from Russia were 3,411.1 mln kWh and net exports to Central Asia 1,331.0 mln kWh. Almaty region consumption rose by 621.6 mln kWh (+5.2%). — [KEGOC AR2024](https://ar2024.kegoc.kz/ru/electricity-balance.html)
- Total installed capacity on 01.01.2026 was **26,807.0 MW**, with 22,844.2 MW available across 248 plants. KEGOC publishes wholesale-market analyses for 2024, H1 2025 and FY2025, and links the balancing-market system at **https://bems.kegoc.kz/**. — [KEGOC key facts, updated 16.09.2026](https://www.kegoc.kz/ru/electric-power/)
- РФЦ publishes periodic RES-share press releases, for example "Доля ВИЭ за 6 месяцев 2024 года — 6,5%". — [rfc.kz news 163797](https://rfc.kz/ru/press-center/news/163797/)
- KOREM, as РЦ БРЭ, publishes balancing-market settlement and offset information. — [KOREM РЦ БРЭ](https://www.korem.kz/rus/sc_bem/bre_offsets/)
- Kazhydromet publishes storm warnings (strong wind, dust storms, fog) by region. — [Kazhydromet storm warnings](https://www.kazhydromet.kz/ru/storm)

### Inferences
- For a hackathon, the realistic external inputs are:
  - global NWP (ECMWF/GFS via Open-Meteo, etc.) and ERA5 reanalysis;
  - Kazhydromet storm warnings as a qualitative high-wind or regime flag;
  - national monthly RES aggregates, used only for context.

  There is no open hourly market or plant dataset for the site.

### Gaps
- I did not verify whether KOREM publishes hourly balancing-market prices publicly, or whether bems.kegoc.kz has any public view.
- I did not find a Ministry of Energy RES registry URL with plant coordinates.

---

## 6. Business value: imbalance costs, value of accuracy, forecast services in KZ

### Takeaway
Direct evidence:
- RES imbalances cost the Unified Buyer about **7.55 bn tenge in 2024**.
- The 2020 imbalance volume of 660 mln kWh was valued at 21.3 bn tenge, about 32 tg/kWh.
- New RES face a symmetric penalty of about **0.3 × PPA price per kWh of hourly deviation**, from the 1.3/0.7 coefficients.

Samruk-Energy, owner of the Nurly 5 MW plant and 25% owner of Shelek 60 MW, announced in August 2026 an ML-based RES forecasting system targeting **80% accuracy**, to launch by end-2026. The local vendor InTech-Forecast claims a 15–20% cut in imbalances.

### Cited Findings
- **Samruk-Energy AI forecasting** (announced 20.08.2026):
  - ML model integrated with a meteorological service, using high-resolution met data plus **АСКУЭ and SCADA** history.
  - Aim: "повысить точность прогнозов до 80%" and cut financial losses from deviations of actual output from declared volumes.
  - Wind was singled out: "Точность прогнозирования особенно важна для объектов ветровой генерации".
  - Launch planned by **end of 2026**. No accuracy metric was defined.

  — [inform.kz, 20.08.2026](https://www.inform.kz/ru/ii-povisit-tochnost-prognozov-virabotki-vie-do-80-v-kazahstane-8221b43c)
- **InTech-Forecast** (ТОО «Центр Зеленых Технологий»; earlier ТОО «Modern Innovative Technologies»):
  - Billed as the "first in Central Asia" RES forecasting system, with a horizon of one day and beyond, delivered as daily Excel reports.
  - Uses algorithmic plus deep-learning models, a digital twin and satellite data.
  - Deployed at Kengir PV (10 MW) and Balkhash PV (50 MW), and in test mode at a 100 MW plant.
  - Claims **15–20% reduction in imbalances** and losses.
  - Development budget 25–50 mln tenge (2025–2027).

  — [greenregister.igtipc.org, 18.03.2025](https://greenregister.igtipc.org/2025/03/18/4448/); [QazaqGreen, 21.04.2021](https://qazaqgreen.com/journal-qazaqgreen/expert-opinion/260/)
- RES imbalance cost to the Unified Buyer in 2024 was **7,546,098,188 tenge**; the penalty coefficients for post-2023 contracts are 1.3/0.7. — [Inbusiness, 11.06.2025](https://inbusiness.kz/ru/news/edinyj-zakupshik-ushel-v-ubytok-iz-za-zelenoj-energii)
- The Unified Buyer's imbalance settlement revenue in 2025 was 92.3 bn tenge (all subjects, not only RES). RES tariffs were 20.28–34.77 tg/kWh. — [Kursiv, 23.07.2026](https://kz.kursiv.media/2026-07-23/zhnb-edinyi-zakupshhik-elektroenergii-kazahstana-vdvoe-sokratil-pribyl/)
- In 2020 imbalances of 660 mln kWh were valued at 21.3 bn tenge, about 20% of RES purchases. — [QazaqGreen, 21.04.2021](https://qazaqgreen.com/journal-qazaqgreen/expert-opinion/260/)
- Wind's average hourly deviation in 9M 2022 was 60.73% under the RFC-aggregated schedule, which gives a sense of how poor the baseline schedules were. — [QazaqGreen analytics, 21.12.2022](https://qazaqgreen.com/journal-qazaqgreen/analitycs/864/)
- The 2025 wind auction ceiling was 22.68 tg/kWh, with bids down to 18.72 tg/kWh. — [QazaqGreen](https://qazaqgreen.com/news/kazakhstan/2555/) (via search summary)

### Inferences (illustrative, assumptions stated)
- **Penalty per MWh for a post-2023 plant:** ΔR ≈ 0.3 × P × |E_plan − E_actual|.
  - At P = 20 tg/kWh: about **6 tg/kWh = 6,000 tg/MWh** of absolute hourly error.
  - At P = 22.68: about 6.8 tg/kWh.
- **Value of 1 percentage point of capacity-normalised NMAE per year:** 0.01 × P_rated × 8,760 h of absolute error.
  - **Nurly 5 MW:** 438 MWh/yr. At 6,000 tg/MWh that is about **2.6 mln tenge/yr per pp**. Moving from NMAE 20% to 12% saves about 21 mln tenge/yr, relative to about 16–17 GWh × P ≈ 320–380 mln tenge of revenue.
  - **Shelek 60 MW:** about **31.5 mln tenge/yr per pp**.
  - National fleet of about 2,059 MW wind at the same unit cost: about 1.08 bn tenge/yr per pp.

  These are upper-bound style estimates. They assume every hour's error is penalised, no tolerance band and no netting. Pre-2023 plants (probably Nurly and Shelek) do not pay this directly: the cost lands on the Unified Buyer and wholesale consumers. It is still the right "system value" framing for Samruk-Energy/РФЦ.
- **Anchoring the 2024 cost:** 7.55 bn tenge spread over RES imbalance volumes. If imbalances were still about 40–50% of RES output (about 3–3.8 TWh), that implies roughly 2–2.5 tg/kWh net cost to the Unified Buyer. This is lower than the 0.3P penalty because of netting across plants and hours. **This is speculative**, since 2024 volumes were not found.
- A reasonable pitch metric aligned with how the market settles is hourly MAE in MWh, and tenge penalty = 0.3 × P × Σ|error|, **plus the share of hours whose deviation exceeds 20%** (the "critical deviation" threshold in Order 112). The team should state explicitly how "80% accuracy" is defined. Samruk-Energy did not define it; one plausible reading is 1 − NMAE ≥ 0.8.

### Gaps
- Actual 2024–2026 RES imbalance volumes (MWh) and hourly balancing prices were not found in public sources.
- No named Chinese vendor forecasting service was found for Shelek/Nurly (e.g., Goldwind's own forecasting products). No KZ case study reports NMAE/RMSE figures.
- The tenge/USD rate was not researched, so no USD conversions are given.
