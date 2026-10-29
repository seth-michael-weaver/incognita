/* Korean: neutrons (5장, 중성자가 필요한 이유) */
WT.L.ch.neutrons = {
  num: "5장", title: "원자로는 왜 중성자로 돌아가는가", short: "중성자가 필요한 이유",
  html: `
<div class="step">
  <p>양성자는 양전하이고, 원자핵의 양성자 82개도 그렇습니다. 같은 전하끼리는 밀어내므로 양성자는 밀려나고, 가까워질수록 그 밀침은 빠르게 커집니다(화살표). 느린 양성자는 닿기 전에 멈추어 되돌아갑니다. 약 13 MeV를 넘어야 그 밀침을 넘어서고, 그 바로 아래에서는 가끔 그래도 빠져들어 갑니다(<b>터널링</b>). 작은 그래프는 같은 밀침을 에너지 언덕으로 보여 줍니다.</p>
  <div class="ctl"><label for="wn-e1">양성자 에너지 (MeV)</label><input id="wn-e1" type="range" data-bind="Ep" data-instant min="0.5" max="20" step="0.1" value="6"><output data-show="Ep" data-fmt="1"></output></div>
</div>
<div class="step">
  <p>중성자는 전하가 없어서 어떤 속도로도 들어갑니다. 밀어내는 것이 없으니 오를 언덕이 없습니다. 원자핵에 닿기만 하면 강한 핵력이 끌어당겨 줍니다.</p>
  <div class="ctl"><label for="wn-e2">중성자 에너지 (느림 → 빠름)</label><input id="wn-e2" type="range" data-bind="lgEn" data-instant min="-1.6" max="7.3" step="0.01" value="-1.6"><output id="wn-en-out"></output></div>
  <p>슬라이더는 상온 중성자의 속도인 0.025 eV에서 20 MeV까지, 거의 10억 배에 걸쳐 움직입니다. 끝까지 내려가도 중성자는 여전히 들어갑니다.</p>
</div>
<div class="step">
  <p>그래서 원자로에서는 느린 중성자도 우라늄을 쪼갤 수 있습니다. 중성자를 삼킨 우라늄-235 원자핵은 약간의 여분의 에너지를 가진 우라늄-236이 되고, 그 에너지로 흔들리다 목이 생기도록 늘어나 둘로 끊어지기에 충분합니다. 두 조각은 약 200 MeV로 날아 흩어지고, 그들이 내놓는 두세 개의 새 중성자가 다음 원자핵을 쪼갤 수 있습니다. 연쇄 반응입니다.</p>
</div>`,
};

// canvas labels added 2026-10-29 (I18NLABELS_B)
Object.assign(WT.L.labels, {
  "+{#} charge: the push grows as the proton gets closer": "+{#} 전하: 양성자가 가까울수록 밀침이 커짐",
  "lead{#}": "납{#}",
  "closest approach": "최근접 거리",
  "proton · {#} MeV": "양성자 · {#} MeV",
  "energy vs distance": "거리에 따른 에너지",
  "hill ≈ {#} MeV": "언덕 ≈ {#} MeV",
  "pushed back · about {#} in {#}³ tunnels through": "밀려남 · 약 {#}/{#}³이 터널링",
  "no charge, no push": "전하 없음, 밀침 없음",
  "neutron · {#} eV": "중성자 · {#} eV",
  "even this crawling neutron gets in": "이렇게 느린 중성자도 들어감",
  "≈ {#} MeV released": "≈ {#} MeV 방출",
  "two fragments + {#} new neutrons": "조각 둘 + 새 중성자 {#}개",
  "a slow neutron + U{#} → two fragments, {#}–{#} new neutrons, about {#} MeV": "느린 중성자 + U{#} → 조각 둘, 새 중성자 {#}–{#}개, 약 {#} MeV",
  "a proton this slow could never get in": "이렇게 느린 양성자는 결코 못 들어감",
});
