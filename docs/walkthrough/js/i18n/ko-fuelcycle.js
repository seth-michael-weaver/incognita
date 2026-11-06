/* Korean: fuelcycle (핵연료 주기) */
WT.L.ch.fuelcycle = {
  num: "강의 1", title: "핵연료 주기", short: "핵연료 주기",
  html: `
<div class="step">
  <h3>우라늄 캐내기</h3>
  <p>광석은 대부분 암석이고, 그 안의 우라늄 가운데 쉽게 쪼개지는 우라늄-235는 0.7 %뿐입니다.</p>
  <div class="ctl"><label for="fc-g">광석 품위(우라늄 %)</label><input id="fc-g" type="range" data-bind="lg" data-instant min="-1.7" max="1.3" step="0.01" value="-1"></div>
</div>
<div class="step">
  <h3>농축은 물질 수지다</h3>
  <p>우라늄은 기체 상태로, 우라늄-235가 더 많은 작은 흐름(연료)과 감손된 큰 흐름(테일)으로 나뉩니다.</p>
  <div class="ctl"><label for="fc-p">연료 농축도(% U-235)</label><input id="fc-p" type="range" data-bind="xp" data-instant min="3" max="5" step="0.05" value="4.5"><output data-show="xp" data-fmt="2"></output></div>
  <div class="ctl"><label for="fc-t">테일(% U-235)</label><input id="fc-t" type="range" data-bind="xt" data-instant min="0.15" max="0.35" step="0.01" value="0.25"><output data-show="xt" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>펠릿, 연료봉, 집합체</h3>
  <p>농축 우라늄은 세라믹 펠릿으로 구워져 연료봉에 밀봉되고 집합체로 묶입니다. <a href="#reactor">다음 강의</a>에서 이들을 노심 안까지 따라갑니다.</p>
  <div class="ctl"><label for="fc-f">연료(우라늄 톤)</label><input id="fc-f" type="range" data-bind="ft" data-instant min="1" max="27" step="1" value="1"><output data-show="ft" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>노심 속의 세월</h3>
  <p>3~6년 동안 무거운 원자의 몇 퍼센트가 쪼개지며 핵분열 생성물과 약간의 새 플루토늄을 남깁니다(<a href="#burnup">연소도</a>).</p>
  <div class="ctl"><label for="fc-b">연소도(톤당 GWd)</label><input id="fc-b" type="range" data-bind="bu" data-instant min="0" max="60" step="1" value="50"><output data-show="bu" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>냉각, 그리고 두 갈래 길</h3>
  <p>사용후핵연료는 수조에서, 그다음 건식 캐스크에서 식습니다. 그 뒤에는 그대로 깊이 묻거나, 재처리해서 우라늄과 플루토늄을 다시 씁니다(<a href="#waste">사용후핵연료</a>, <a href="#breeding">증식</a>).</p>
  <div class="btns"><button class="btn ghost" data-act="frO" aria-pressed="true">일회 통과</button> <button class="btn ghost" data-act="frR" aria-pressed="false">재처리</button></div>
</div>`,
};
Object.assign(WT.L.labels, {
  "Convert": "변환",
  "Disposal": "처분",
  "End": "끝",
  "Enrich": "농축",
  "Fabricate": "성형가공",
  "Mill": "정련",
  "Mine": "채광",
  "Pool · cask": "수조 · 캐스크",
  "Reactor": "원자로",
  "Store": "저장",
  "about what a {#} MWe reactor loads in a year": "{#} MWe 원자로가 1년에 장전하는 양 정도",
  "assemblies": "집합체",
  "assemblies of {#} rods": "연료봉 {#}개짜리 집합체",
  "at least {#} years": "최소 {#}년",
  "cask": "캐스크",
  "decades": "수십 년",
  "decades in air": "공기 중 수십 년",
  "deep repository, {#}–{#} m down": "심층 처분장, 지하 {#}–{#} m",
  "dry cask": "건식 캐스크",
  "enrich": "농축",
  "enrichment plant (UF₆ gas)": "농축 공장 (UF₆ 기체)",
  "fission products": "핵분열 생성물",
  "illustration": "예시 그림",
  "minor actinides": "부악티늄족",
  "most mines: above {#} %": "대부분 광산: {#} % 이상",
  "of electricity from this tonne": "이 1톤에서 얻는 전기",
  "once-through: the whole tonne is disposed of": "일회 통과: 1톤 전체를 처분",
  "one tonne of fuel: each square is {#} kg": "연료 1톤: 한 칸이 {#} kg",
  "one tonne: each square {#} kg": "1톤: 한 칸 {#} kg",
  "pellets": "펠릿",
  "pellets, {#} cm tall": "펠릿, 높이 {#} cm",
  "plutonium": "플루토늄",
  "pool": "수조",
  "recycle": "재활용",
  "repository": "처분장",
  "repository {#}–{#} m deep": "처분장 깊이 {#}–{#} m",
  "reprocess": "재처리",
  "richest, Canada: up to {#} %": "가장 풍부한 캐나다: 최대 {#} %",
  "rods, about {#} m long": "연료봉, 길이 약 {#} m",
  "rods, {#} m": "연료봉, {#} m",
  "the rest: uranium{#}": "나머지: 우라늄{#}",
  "the whole tonne": "1톤 전체",
  "typical discharge {#}–{#}": "일반적인 방출 연소도 {#}–{#}",
  "uranium{#}": "우라늄{#}",
  "uranium{#} (and {#})": "우라늄{#} (및 {#})",
  "{#} U atoms": "U 원자 {#}개",
  "{#} are U{#}": "{#}개가 U{#}",
  "{#} are uranium{#}": "{#}개가 우라늄{#}",
  "{#} t used": "사용후 {#} t",
  "{#} t used fuel": "사용후핵연료 {#} t",
  "{#} uranium atoms": "우라늄 원자 {#}개",
  "≈ a big reactor's yearly reload": "≈ 대형 원자로의 연간 재장전량",
  "≥ {#} years": "≥ {#}년",
  "{a} t ore": "광석 {a} t",
  "{a} t U₃O₈": "U₃O₈ {a} t",
  "{a} t UF₆": "UF₆ {a} t",
  "{#} t fuel + {a} t tails": "연료 {#} t + 테일 {a} t",
  "{a} t UO₂": "UO₂ {a} t",
  "pool ≥ {#} years": "수조 ≥ {#}년",
  "ore ≈ {a} t · block = {#} t": "광석 ≈ {a} t · 블록 = {#} t",
  "ore for one tonne of fuel: ≈ {a} t  (each block {#} t)": "연료 1톤에 필요한 광석: ≈ {a} t (블록 하나 {#} t)",
  "{a} of one block": "블록 하나의 {a}",
  "{a} % U": "{a} % U",
  "grade {a} % U": "품위 {a} % U",
  "natural U {a} kg": "천연 U {a} kg",
  "natural uranium {a} kg": "천연 우라늄 {a} kg",
  "{a} % U{#}": "{a} % U{#}",
  "fuel {#} kg": "연료 {#} kg",
  "tails {a} kg": "테일 {a} kg",
  "feed/fuel = (xp − xt)/(xf − xt) = {a}": "공급/연료 = (xp − xt)/(xf − xt) = {a}",
  "natural / fuel = (xp − xt) / (xf − xt) = ({a} − {b}) / ({c} − {b}) = {d}": "천연 / 연료 = (xp − xt) / (xf − xt) = ({a} − {b}) / ({c} − {b}) = {d}",
  "≈ {a} SWU of separative work per kg of fuel": "연료 kg당 분리 작업 ≈ {a} SWU",
  "separative work ≈ {a} SWU per kg of fuel · lower tails: less uranium, more work": "분리 작업 ≈ 연료 kg당 {a} SWU · 테일을 낮추면: 우라늄은 덜, 작업은 더",
  "{a} t uranium = {b} t UO₂": "우라늄 {a} t = UO₂ {b} t",
  "{a} t of enriched uranium, as {b} t of uranium dioxide (UO₂) ceramic": "농축 우라늄 {a} t, 이산화우라늄(UO₂) 세라믹 {b} t로",
  "{a} % of the heavy atoms split": "무거운 원자의 {a} % 분열",
  "{a} GWd/t": "{a} GWd/t",
  "≈ {a} GWh of electricity": "≈ {a} GWh의 전기",
  "reprocessing": "재처리",
  "uranium {a} t": "우라늄 {a} t",
  "plutonium {a} kg": "플루토늄 {a} kg",
  "→ ≈ {a} t MOX fuel": "→ ≈ {a} t MOX 연료",
  "fission products + minor actinides {a} kg → ≈ {#} t glass": "핵분열 생성물 + 부악티늄족 {a} kg → ≈ {#} t 유리",
  "U {a} t → re-enrich": "U {a} t → 재농축",
  "Pu {a} kg → MOX": "Pu {a} kg → MOX",
  "{a} kg waste → glass": "폐기물 {a} kg → 유리",
  "fission prod.": "핵분열 생성물",
  "minor act.": "부악티늄족",
});
