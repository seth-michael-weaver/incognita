/* Japanese: binding (第3章、原子核はなぜまとまっているか) */
WT.L.ch.binding = {
  num: "第3章", title: "原子核はなぜまとまっているのか", short: "結合",
  html: `
<div class="step">
  <p>曲線の高いところほど、強く結合しています。各点は1つの質量数A（陽子と中性子の数の合計）で、その高さは、その原子核を完全にばらばらにするために核子1個あたり必要なエネルギーです。Aをドラッグしてマーカーを読み取ってください。曲線の中ほど、鉄やニッケルのあたりが頂上です。</p>
  <div class="ctl"><label for="bi-a">質量数 A</label><input id="bi-a" type="range" data-bind="pick" data-instant min="2" max="260" step="1" value="56"><output data-show="pick" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>ウランを分裂させます。2つの破片はどちらも、もとのウランより曲線の高い位置にあります。つまり同じ核子がより強く結合した状態になり、その差がエネルギーとして放出されます。軽いほうの破片を選んでください。重いほうは、236個の核子の残りです。</p>
  <div class="ctl"><label for="bi-f">軽いほうの破片の A</label><input id="bi-f" type="range" data-bind="frag" data-instant min="70" max="118" step="1" value="95"><output data-show="frag" data-fmt="0"></output></div>
  <p class="ctl-result" id="bi-split-out" aria-live="polite"></p>
  <p>どう分裂しても約200 MeVになります。燃料分子1個を燃やして得られる数電子ボルトの、数千万倍です。</p>
</div>
<div class="step">
  <p>2つの軽い原子核を1つに結合させます。できた原子核が曲線の高い位置にあれば、エネルギーが放出されます。頂上を越えると、結合させるにはかえってエネルギーが必要になります。</p>
  <div class="ctl"><label for="bi-u">それぞれの軽い原子核の A</label><input id="bi-u" type="range" data-bind="fuse" data-instant min="2" max="60" step="1" value="2"><output data-show="fuse" data-fmt="0"></output></div>
  <p class="ctl-result" id="bi-fuse-out" aria-live="polite"></p>
</div>`,
};

// canvas labels added 2026-10-29 (I18NLABELS_B)
Object.assign(WT.L.labels, {
  "mass number A →": "質量数 A →",
  "binding energy per nucleon (MeV)": "核子あたりの結合エネルギー (MeV)",
  "Ni{#}: most tightly bound": "Ni{#}：最も強く結合",
  "measured masses (AME{#})": "測定された質量（AME{#}）",
  "Fe{#}: {#} MeV per nucleon · {#} MeV in all": "Fe{#}：核子あたり {#} MeV · 全体で {#} MeV",
});
