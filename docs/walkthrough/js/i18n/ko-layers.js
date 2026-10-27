/* Korean: layers (15장). The scoreboard counts come from WT.board (js/scoreboard-data.js, loaded first), as in
 * js/ch/layers.js; a missing block or field drops the number, not the sentence. */
(function () {
  const B = WT.board || {};
  const nOf = (v) => (typeof v === "number" && isFinite(v) ? v : null);
  const tally = (o) => {
    if (!o) return null;
    const w = nOf(o.WIN), t = nOf(o.TIE), l = nOf(o.LOSS);
    if (w === null || t === null || l === null) return null;
    return { w, t, l, d: nOf(o.decided) ?? w + t + l };
  };
  const TE = tally(B.incognita), TT = tally(B.terra);
  const LIBS = B.terra && Array.isArray(B.terra.by_rival) ? B.terra.by_rival.map((r) => r && r.rival).filter((s) => typeof s === "string") : [];
  const ASOF = (() => {
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(B.asof || ""); if (!m) return null;
    const mo = +m[2];
    return mo >= 1 && mo <= 12 ? `${m[1]}년 ${mo}월 ${+m[3]}일` : null;
  })();
  const figs = (T) => (T ? `<div class="figs" aria-label="${T.w}승, ${T.t}무, ${T.l}패"><div class="w"><b>${T.w}</b><span>승</span></div><div><b>${T.t}</b><span>무</span></div><div class="l"><b>${T.l}</b><span>패</span></div></div>` : "");
  const libs = LIBS.length ? `주요 평가 데이터 라이브러리(${LIBS.join(", ")})` : "주요 평가 데이터 라이브러리";
  const engineScore = TE ? ` 그런 비교 ${TE.d}건 중 ${TE.w}건에서 확실히 앞서고, ${TE.t}건에서 대등하며, ${TE.l}건에서 뒤집니다.` : "";
  const terraScore = TT ? `${libs}와 비교하면 ${TT.d}건 중 ${TT.w}건에서 앞서고, ${TT.t}건에서 대등하며, ${TT.l}건에서 뒤집니다.` : `${libs}와 비교합니다.`;

  WT.L.ch.layers = {
    num: "15장", title: "모형은 어떻게 층을 이루는가", short: "층",
    lead: "우리가 내놓는 결과는 엔진 위에 층층이 쌓아 만든 것이며, 각 층은 측정값 앞에서 제자리를 스스로 증명해야 합니다.",
    html: `
<div class="step">
  <div class="layer-chip on">사용 중</div>
  <h3>1층 · 모든 원자핵에 하나의 규칙</h3>
  <p>파란 선은 한 반응에 대한 엔진의 예측입니다. 엔진은 맨 아래층입니다. 모든 핵종에 같은 물리와 같은 전역 설정을 쓰며, 개별 원자핵의 단면적에 맞춘 것은 하나도 없습니다.</p>
  <div class="btns"><button class="btn ghost" data-act="reveal" aria-pressed="false">측정값 보기</button></div>
  <p>그래서 측정값과도, 같은 원자핵에 대해 실행한 다른 모형 코드들과도 견주어 검증할 수 있습니다. 다만 블라인드 테스트는 아닙니다. 전역 설정은 바로 이 비교들을 지켜보며 골랐습니다.${engineScore}</p>
  ${figs(TE)}
</div>
<div class="step">
  <div class="layer-chip null">시험함: 아직 개선 없음</div>
  <h3>2층 · 원자핵마다의 측정값</h3>
  <p>이 층은 전역 규칙 대신 각 원자핵 자신의 측정값을 씁니다. 준위 간격 D0, 세기 함수 S0와 S1(느린 중성자를 얼마나 쉽게 흡수하는지), 평균 감마 폭 ⟨Γγ⟩, 그리고 알려진 에너지 준위들입니다.</p>
  <div class="btns"><button class="btn ghost" data-act="ms0" aria-pressed="true">전역 규칙</button><button class="btn ghost" data-act="ms1" aria-pressed="false">자체 측정값</button></div>
  <p>켜 보면 선이 거의 움직이지 않습니다. 지금까지의 시험에서는 전체적인 개선을 찾지 못했습니다. 문턱 근처의 한 반응에 도움이 되는 유일한 변종은 중성자 포획을 오히려 나쁘게 만듭니다. 그래서 이 층은 당분간 꺼 둡니다.</p>
</div>
<div class="step">
  <div class="layer-chip cand">후보</div>
  <h3>3층 · 좋은 데이터 따라가기 (TERRA)</h3>
  <p>반응이 잘 측정된 곳에서는 선이 측정값을 따라가야 합니다. 세 번째 층인 TERRA는 좋은 데이터가 있는 곳에서는 엔진의 선이 그 데이터를 지나가게 하고, 없는 곳에서는 엔진으로 돌아갑니다.</p>
  <div class="ctl"><label for="lay-cov">측정된 에너지 범위의 비율 (%)</label><input id="lay-cov" type="range" data-bind="cov" min="0" max="1" step="0.01" value="0.45"><output data-show="covPct" data-fmt="0"></output></div>
  <p>${terraScore} 이 중 대부분은 표본 내 비교입니다. 라이브러리들과 마찬가지로 TERRA도 그 측정값을 본 적이 있습니다.</p>
  ${figs(TT)}
</div>
<div class="step">
  <div class="layer-chip wip">개발 중</div>
  <h3>4층 · 정직한 오차 막대</h3>
  <p>맨 위층은 선 주위에 참값을 세 번에 두 번꼴로 담아야 하는 띠(68% 띠)를 두릅니다. 좋은 데이터가 단단히 고정하는 곳에서는 좁고, 그렇지 않은 곳에서는 넓습니다.</p>
  <div class="ctl"><label for="lay-band">띠 폭 · 안에 든 측정값 (%)</label><input id="lay-band" type="range" data-bind="band" min="0.2" max="2.5" step="0.05" value="1"><output data-show="inside" data-fmt="0"></output></div>
  <p>띠를 조절하며 안에 든 측정값을 세어 보세요. 너무 좁으면 띠는 갖지 못한 정밀도를 주장하고, 너무 넓으면 아무것도 말해 주지 않습니다. 엔진 자체의 띠는 아직 채택되지 않았습니다. 모든 반응을 한데 모으면 목표에 맞지만, 아직 모든 반응 계열에서 맞지는 않습니다. TERRA는 자체 띠를 가지고 있으며, 그 띠는 위의 비교에 포함되어 있습니다.</p>
</div>
<div class="step">
  <h3>현재 상황</h3>
  <p>어떤 층이든 측정값으로 시험한 뒤에야 채택되며, 도움이 되지 않으면 꺼진 채로 남습니다. 현재 엔진은 사용 중이고 TERRA는 후보입니다. 측정 구조 층과 엔진의 불확도 띠는 아직 시험 중입니다.</p>
  <p><a href="scoreboard.html" data-keep-lang>전체 점수판 보기 →</a> 우리가 이기지 못한 모든 비교, 각 경쟁 상대, 그리고 읽는 방법이 있습니다.</p>
  <div class="aside">${ASOF ? `${ASOF} 기준 점수, 출처:` : "점수 출처:"} 프로젝트의 연구 기록부. 그림의 곡선은 예시입니다.</div>
</div>`,
  };
})();
Object.assign(WT.L.labels, {
  "{#} · engine": "{#} · 엔진",
  "{#} · measured structure": "{#} · 측정 구조",
  "{#} · TERRA: anchored to data": "{#} · TERRA: 데이터에 고정",
  "{#} · uncertainty band": "{#} · 불확도 띠",
  "measured here": "측정 구간",
  "neutron energy →": "중성자 에너지 →",
  "how often the reaction happens": "반응이 일어나는 빈도",
  "hollow dots: measurements the engine is compared with": "속이 빈 점: 엔진과 비교하는 측정값",
  "own measured values: the line barely moves": "자체 측정값: 선이 거의 움직이지 않음",
  "global rule": "전역 규칙",
  "no measurements: TERRA falls back to the engine": "측정값 없음: TERRA가 엔진으로 돌아감",
  "solid: follows the data · dashed: the engine alone": "실선: 데이터를 따름 · 점선: 엔진만",
  "{#} of {#} measurements inside the band (aim: about {#} %)": "측정값 {#}/{#}개가 띠 안 (목표: 약 {#}%)",
  "no measurements to check the band against": "띠를 확인할 측정값 없음",
});
Object.assign(WT.L.ui, { nav_board: "점수판" });
