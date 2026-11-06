/* Portuguese (pt-PT): burnup (Taxa de queima do combustível) */
WT.L.ch.burnup = {
  num: "Lição 1", title: "Taxa de queima do combustível", short: "Taxa de queima",
  html: `
<div class="step">
  <h3>Uma pastilha ao longo da vida</h3>
  <p>Eis mil átomos de uma pastilha de combustível nova: 45 são urânio-235, os restantes urânio-238. Põe o reator a funcionar e vê o urânio-235 cindir-se enquanto aparecem átomos novos. A <b>taxa de queima</b> conta a energia extraída, em gigawatts-dia por tonelada de urânio; os reatores de água param por volta de 45–55.</p>
  <div class="ctl"><label for="bu-d1">Dias a plena potência</label><input id="bu-d1" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="400"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>O plutónio entra em jogo</h3>
  <p>O urânio-238 captura neutrões e torna-se plutónio-239, que também se cinde. No fim da vida, mais de metade das fissões dão-se no plutónio; ao longo de toda a vida, cerca de um terço da energia vem dele.</p>
  <div class="ctl"><label for="bu-d2">Dias a plena potência</label><input id="bu-d2" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="1000"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Os venenos acumulam-se</h3>
  <p>Cada fissão deixa dois produtos de fissão, e alguns absorvem neutrões. Com menos urânio-235 e mais venenos, <i>k</i><sub>∞</sub> (fissões novas por fissão numa rede infinita deste combustível) vai descendo até o combustível já não conseguir manter sozinho uma reação em cadeia.</p>
  <div class="ctl"><label for="bu-d3">Dias a plena potência</label><input id="bu-d3" type="range" data-bind="d" data-instant min="0" max="1400" step="10" value="700"><output data-show="d" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>Boro e recargas</h3>
  <p>Um núcleo mistura combustível novo, de meia-idade e velho. O combustível novo tem reatividade a mais, por isso o boro dissolvido na água de refrigeração absorve o excedente e vai sendo diluído. Quando chega a zero, sai o terço mais antigo e entra combustível novo.</p>
  <div class="ctl"><label for="bu-m">Meses a plena potência</label><input id="bu-m" type="range" data-bind="m" data-instant min="0" max="54" step="0.5" value="8"><output data-show="m" data-fmt="1"></output></div>
</div>`,
};

Object.assign(WT.L.labels, {
  "illustrative model": "modelo ilustrativo",
  // scenes 1-3: the pellet
  "{a} days · burnup {b} GWd/t": "{a} dias · taxa de queima {b} GWd/t",
  "uranium{#}": "urânio{#}",
  "plutonium{#}": "plutónio{#}",
  "other Pu": "outro Pu",
  "other plutonium": "outro plutónio",
  "fission products": "produtos de fissão",
  "fission products (pairs)": "produtos de fissão (pares)",
  "{a} in {#}": "{a} em {#}",
  "uranium{#}: the remaining ~{#}–{#} %": "urânio{#}: o restante, ~{#}–{#} %",
  "plutonium's share": "parte do plutónio",
  "fissions": "fissões",
  "fissions now": "fissões agora",
  "energy so far": "energia acumulada",
  "Pu": "Pu",
  "plutonium": "plutónio",
  "split": "cindidos",
  "each dot: {#} atom in {#}": "cada ponto: {#} átomo em {#}",
  "each dot: one atom in a thousand": "cada ponto: um átomo em mil",
  // scene 3: k-infinity
  "k = {#}": "k = {#}",
  "GWd/t →": "GWd/t →",
  "burnup (GWd/t) →": "taxa de queima (GWd/t) →",
  "typical discharge": "descarga típica",
  "typical discharge {#}–{#}": "descarga típica {#}–{#}",
  "can't keep a chain going alone": "já não mantém a cadeia sozinho",
  "this fuel alone can no longer keep a chain going": "sozinho, este combustível já não consegue manter uma reação em cadeia",
  "k∞ reaches {#}": "k∞ chega a {#}",
  "k∞ = {a}": "k∞ = {a}",
  "fission products catch {a} % of neutrons": "os produtos de fissão capturam {a} % dos neutrões",
  // scene 4: the core and boron
  "fresh": "novo",
  "{#} cycle": "{#} ciclo",
  "one cycle old": "com um ciclo",
  "{#} cycles": "{#} ciclos",
  "two cycles old": "com dois ciclos",
  "reload": "recarga",
  "boron (ppm)": "boro (ppm)",
  "boron in the water (ppm)": "boro na água (ppm)",
  "months →": "meses →",
  "months at full power →": "meses a plena potência →",
  "{a} ppm": "{a} ppm",
  "cycle {a} months · fuel leaves at {b} GWd/t": "ciclo de {a} meses · o combustível sai a {b} GWd/t",
});
