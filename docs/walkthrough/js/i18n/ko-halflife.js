/* Korean: halflife (방사능과 반감기) */
WT.L.ch.halflife = {
  num: "강의 1", title: "방사능과 반감기", short: "반감기",
  lead: "어떤 원자는 불안정합니다. 그 원자핵은 언젠가 터지듯 붕괴하여 방사선을 내놓고 다른 것으로 바뀝니다. 하나가 언제 붕괴할지는 아무도 모르지만, 시료 전체는 시계를 맞춰도 될 만큼 정확한 규칙을 따릅니다.",
  html: `
<div class="step">
  <h3>무작위로 붕괴하는 시료</h3>
  <p>빛나는 공 하나하나가 불안정한 원자핵입니다. 어느 것이든 언제라도 붕괴하여 방사선을 번쩍 내놓고 차분하고 안정한 원자가 될 수 있습니다. 하나를 눌러 붕괴시켜 보세요.</p>
  <div class="btns"><button class="btn" data-act="refill">새 시료</button></div>
</div>
<div class="step">
  <h3>절반, 다시 그 절반</h3>
  <p>다음에 어느 것이 붕괴할지는 아무도 모르지만, 무리 전체는 예측할 수 있습니다. <b>반감기</b>가 한 번 지나면 약 절반이 남고, 두 번이면 4분의 1, 그다음엔 8분의 1이 남습니다. 반감기를 늘리거나 줄여 보세요.</p>
  <div class="ctl"><label for="hl-th">반감기 (초)</label><input id="hl-th" type="range" data-bind="Th" data-instant min="1" max="8" step="0.5" value="3"><output data-show="Th" data-fmt="1"></output></div>
  <div class="btns"><button class="btn ghost" data-act="refill">새 시료</button></div>
</div>
<div class="step">
  <h3>원자핵에는 기억이 없다</h3>
  <p>살아남은 핵 하나를 따라가 보세요. 이미 얼마나 오래 버텼든, 반감기 한 번을 더 버틸 확률은 여전히 2분의 1입니다. 원자핵은 늙지 않습니다.</p>
  <div class="btns"><button class="btn ghost" data-act="tag">다른 핵 따라가기</button><button class="btn ghost" data-act="refill">새 시료</button></div>
</div>
<div class="step">
  <h3>실제 반감기</h3>
  <p>실제 동위원소의 반감기는 며칠에서 수십억 년에 이릅니다. 이 늘인 시간축에서 각 동위원소는 자기 반감기에서 절벽처럼 떨어집니다. 하나를 골라 시간을 앞으로 끌어 보세요.</p>
  <div class="btns"><button class="btn ghost" data-act="iso0" aria-pressed="false">아이오딘-131</button><button class="btn ghost" data-act="iso1" aria-pressed="true">세슘-137</button><button class="btn ghost" data-act="iso2" aria-pressed="false">탄소-14</button><button class="btn ghost" data-act="iso3" aria-pressed="false">우라늄-238</button></div>
  <div class="ctl"><label for="hl-t1">지난 시간</label><input id="hl-t1" type="range" data-bind="lt" data-instant min="3" max="17.8" step="0.02" value="8.98"><output class="hl-tout"></output></div>
</div>
<div class="step">
  <h3>방사능: 초당 붕괴 수</h3>
  <p>각각 1그램씩 나란히 놓았습니다. 반감기가 짧으면 매초 많이 붕괴하지만 오래가지 못하고, 반감기가 길면 아주 오랫동안 희미하게 빛납니다. 시간을 끌면서 램프가 하나씩 꺼지는 것을 지켜보세요.</p>
  <div class="ctl"><label for="hl-t2">지난 시간</label><input id="hl-t2" type="range" data-bind="lt" data-instant min="3" max="17.8" step="0.02" value="4.94"><output class="hl-tout"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "Cs{#}": "Cs{#}",
  "C{#}": "C{#}",
  "I{#}": "I{#}",
  "U{#}": "U{#}",
  "all": "전부",
  "almost none": "거의 없음",
  "caesium{#}": "세슘{#}",
  "carbon{#}": "탄소{#}",
  "iodine{#}": "아이오딘{#}",
  "uranium{#}": "우라늄{#}",
  "caesium{#} · half-life {#} years": "세슘{#} · 반감기 {#}년",
  "carbon{#} · half-life {#} years": "탄소{#} · 반감기 {#}년",
  "iodine{#} · half-life {#} days": "아이오딘{#} · 반감기 {#}일",
  "uranium{#} · half-life {#} billion years": "우라늄{#} · 반감기 {#}십억 년",
  "chance to last one more: {#} in {#}": "한 번 더 버틸 확률: {#}분의 {#}",
  "drag": "끌기",
  "every survivor has the same {#}-in{#} chance per half-life": "살아남은 핵은 모두 반감기마다 같은 확률 ({#}:{#})",
  "every survivor has the same 1-in-2 chance per half-life": "살아남은 핵은 모두 반감기마다 같은 2분의 1 확률",
  "fission product": "핵분열 생성물",
  "medicine, fission product": "의료용, 핵분열 생성물",
  "natural uranium": "천연 우라늄",
  "radiocarbon dating": "방사성 탄소 연대 측정",
  "half-lives →": "반감기 →",
  "illustrative half-life": "설명용 반감기",
  "it popped: follow another": "붕괴했음: 다른 핵 따라가기",
  "nuclei left": "남은 원자핵",
  "pops per second (log)": "초당 붕괴 수 (로그)",
  "pops per second, {#} gram (each line ×{#})": "초당 붕괴 수, {#}그램 (선마다 ×{#})",
  "survived {#} half-lives": "반감기 {#}번을 버팀",
  "survived {#} half-lives · still {#} in {#}": "반감기 {#}번을 버팀 · 여전히 {#}/{#}",
  "{#} of {#} still unstable": "{#}/{#}개가 아직 불안정",
  "{#} of {#} left · half-life {#} s": "{#}/{#}개 남음 · 반감기 {#} s",
  "{#} half-life": "반감기 {#}번",
  "{#} minutes": "{#}분",
  "{#} hours": "{#}시간",
  "{#} hour": "{#}시간",
  "{#} h": "{#}시간",
  "{#} days": "{#}일",
  "{#} day": "{#}일",
  "{#} d": "{#}일",
  "{#} months": "{#}개월",
  "{#} years": "{#}년",
  "{#} year": "{#}년",
  "{#} yr": "{#}년",
  "{#}³ yr": "{#}³년",
  "{#}⁶ yr": "{#}⁶년",
  "{#}⁹ yr": "{#}⁹년",
  "{#} thousand years": "{#}천 년",
  "{#} million years": "{#}백만 년",
  "{#} billion years": "{#}십억 년",
  "½ {#} days": "½ {#}일",
  "½ {#} years": "½ {#}년",
  "½ {#} billion years": "½ {#}십억 년",
  "½ {#} bn years": "½ {#}십억 년",
  "{#} % left after {#} minutes": "{#} % 남음 ({#}분 뒤)",
  "{#} % left after {#} hours": "{#} % 남음 ({#}시간 뒤)",
  "{#} % left after {#} days": "{#} % 남음 ({#}일 뒤)",
  "{#} % left after {#} months": "{#} % 남음 ({#}개월 뒤)",
  "{#} % left after {#} years": "{#} % 남음 ({#}년 뒤)",
  "{#} % left after {#} thousand years": "{#} % 남음 ({#}천 년 뒤)",
  "{#} % left after {#} million years": "{#} % 남음 ({#}백만 년 뒤)",
  "{#} % left after {#} billion years": "{#} % 남음 ({#}십억 년 뒤)",
  "under {#} % left after {#} minutes": "{#} % 미만 남음 ({#}분 뒤)",
  "under {#} % left after {#} hours": "{#} % 미만 남음 ({#}시간 뒤)",
  "under {#} % left after {#} days": "{#} % 미만 남음 ({#}일 뒤)",
  "under {#} % left after {#} months": "{#} % 미만 남음 ({#}개월 뒤)",
  "under {#} % left after {#} years": "{#} % 미만 남음 ({#}년 뒤)",
  "under {#} % left after {#} thousand years": "{#} % 미만 남음 ({#}천 년 뒤)",
  "under {#} % left after {#} million years": "{#} % 미만 남음 ({#}백만 년 뒤)",
  "under {#} % left after {#} billion years": "{#} % 미만 남음 ({#}십억 년 뒤)",
  "one gram of each, after {#} minutes": "각각 1그램, {#}분 뒤",
  "one gram of each, after {#} hours": "각각 1그램, {#}시간 뒤",
  "one gram of each, after {#} days": "각각 1그램, {#}일 뒤",
  "one gram of each, after {#} months": "각각 1그램, {#}개월 뒤",
  "one gram of each, after {#} years": "각각 1그램, {#}년 뒤",
  "one gram of each, after {#} thousand years": "각각 1그램, {#}천 년 뒤",
  "one gram of each, after {#} million years": "각각 1그램, {#}백만 년 뒤",
  "one gram of each, after {#} billion years": "각각 1그램, {#}십억 년 뒤",
  "{#} /s": "{#} /s",
  "~{#} /s": "~{#} /s",
  "{#}×{#}¹ /s": "{#}×{#}¹ /s",
  "{#}×{#}² /s": "{#}×{#}² /s",
  "{#}×{#}³ /s": "{#}×{#}³ /s",
  "{#}×{#}⁴ /s": "{#}×{#}⁴ /s",
  "{#}×{#}⁵ /s": "{#}×{#}⁵ /s",
  "{#}×{#}⁶ /s": "{#}×{#}⁶ /s",
  "{#}×{#}⁷ /s": "{#}×{#}⁷ /s",
  "{#}×{#}⁸ /s": "{#}×{#}⁸ /s",
  "{#}×{#}⁹ /s": "{#}×{#}⁹ /s",
  "{#}×{#}¹⁰ /s": "{#}×{#}¹⁰ /s",
  "{#}×{#}¹¹ /s": "{#}×{#}¹¹ /s",
  "{#}×{#}¹² /s": "{#}×{#}¹² /s",
  "{#}×{#}¹³ /s": "{#}×{#}¹³ /s",
  "{#}×{#}¹⁴ /s": "{#}×{#}¹⁴ /s",
  "{#}×{#}¹⁵ /s": "{#}×{#}¹⁵ /s",
  "{#}×{#}¹⁶ /s": "{#}×{#}¹⁶ /s",
});
