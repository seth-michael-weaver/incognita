/* Korean: blanket (32장, 증식 블랑켓과 제1벽) */
WT.L.ch.blanket = {
  num: "32장", title: "증식 블랑켓과 제1벽", short: "블랑켓",
  lead: "삼중수소는 자연에 거의 없습니다. D–T 발전소는 플라스마가 만드는 중성자를 써서 리튬으로부터 삼중수소를 스스로 증식해야 합니다.",
  html: `
<div class="step">
  <h3>삼중수소 증식비</h3>
  <p>중성자는 리튬에 붙잡혀 삼중양성자를 만들 때까지 떠돕니다. 빛나는 점 하나하나가 삼중양성자 하나입니다.</p>
  <div class="ctl"><label for="bk-e">리튬-6 비율 (%)</label><input id="bk-e" type="range" data-bind="enr" min="7.5" max="90" step="0.5" value="90" data-instant><output data-show="enr" data-fmt="1"></output></div>
  <div class="ctl"><label for="bk-d">증식재 두께 (cm)</label><input id="bk-d" type="range" data-bind="depth" min="10" max="100" step="1" value="60" data-instant><output data-show="depth" data-fmt="0"></output></div>
  <div class="formula">TBR = (⁶Li(n,t) + ⁷Li(n,n′t)) / n<sub>핵융합</sub> &gt; 1</div>
</div>
<div class="step">
  <h3>(n,2n)에 의한 중성자 증배</h3>
  <p>납에 부딪힌 14 MeV 중성자는 두 번째 중성자를 떼어 낼 수 있습니다. 이것이 (n,2n)입니다. 리튬만 있을 때와 비교해 보세요.</p>
  <div class="btns bk-m"><button class="btn ghost" data-act="pbli" aria-pressed="true">납–리튬</button> <button class="btn ghost" data-act="li" aria-pressed="false">리튬만</button></div>
  <div class="ctl"><label for="bk-e2">리튬-6 비율 (%)</label><input id="bk-e2" type="range" data-bind="enr" min="7.5" max="90" step="0.5" value="90" data-instant><output data-show="enr" data-fmt="1"></output></div>
</div>
<div class="step">
  <h3>제1벽 속의 헬륨과 수소</h3>
  <p>제1벽은 14 MeV 빔을 고스란히 받습니다. 그 안에 헬륨과 수소가 INCOGNITA가 계산한 비율로 쌓입니다.</p>
  <div class="btns bk-w"><button class="btn ghost" data-act="wFe" aria-pressed="true">강철</button> <button class="btn ghost" data-act="wW" aria-pressed="false">텅스텐</button> <button class="btn ghost" data-act="wV" aria-pressed="false">바나듐</button> <button class="btn ghost" data-act="wCu" aria-pressed="false">구리</button> <button class="btn ghost" data-act="wSi" aria-pressed="false">SiC</button></div>
  <div class="ctl"><label for="bk-l">벽 부하 (MW/m²)</label><input id="bk-l" type="range" data-bind="load" min="0.5" max="3" step="0.1" value="1" data-instant><output data-show="load" data-fmt="1"></output></div>
  <div class="ctl"><label for="bk-y">기간 (년)</label><input id="bk-y" type="range" data-bind="yrs" min="0" max="10" step="0.1" value="2" data-instant><output data-show="yrs" data-fmt="1"></output></div>
  <div class="formula">appm = σ(14.1 MeV) · φ · t · 10⁶</div>
  <div class="aside">단면적: INCOGNITA 라이브러리 v0.2 (<code>library/v0.2/channels_v02.parquet</code>), <a href="data.html#Fe-56" data-keep-lang>모든 핵종</a>과 같은 곡선입니다.</div>
</div>`,
};
