/* Portuguese (pt-PT): neutrons (Capítulo 4, porque é que os reatores funcionam com neutrões) */
WT.L.ch.neutrons = {
  num: "Capítulo 4", title: "Porque é que os reatores funcionam com neutrões", short: "Porquê neutrões",
  html: `
<div class="step">
  <p>Um protão é positivo, tal como os 82 protões do núcleo. Cargas iguais repelem-se, pelo que o protão é empurrado para longe, e o empurrão cresce depressa à medida que se aproxima (a seta). Um protão lento para antes e volta para trás sem tocar. Só acima de cerca de 13 MeV consegue vencer o empurrão; logo abaixo, por vezes passa na mesma (<b>efeito de túnel</b>). O pequeno gráfico mostra o mesmo empurrão como uma colina de energia.</p>
  <div class="ctl"><label for="wn-e1">Energia do protão (MeV)</label><input id="wn-e1" type="range" data-bind="Ep" data-instant min="0.5" max="20" step="0.1" value="6"><output data-show="Ep" data-fmt="1"></output></div>
</div>
<div class="step">
  <p>Um neutrão não tem carga: entra a qualquer velocidade. Nada o empurra para longe, por isso não há colina para subir; só precisa de chegar ao núcleo, e então a força forte puxa-o para dentro.</p>
  <div class="ctl"><label for="wn-e2">Energia do neutrão (lento → rápido)</label><input id="wn-e2" type="range" data-bind="lgEn" data-instant min="-1.6" max="7.3" step="0.01" value="-1.6"><output id="wn-en-out"></output></div>
  <p>O cursor vai de 0,025 eV, a velocidade de um neutrão à temperatura ambiente, até 20 MeV, quase mil milhões de vezes mais. Até ao extremo mais lento, o neutrão continua a entrar.</p>
</div>
<div class="step">
  <p>Por isso, mesmo neutrões lentos conseguem dividir urânio num reator. Um núcleo de urânio-235 que engole um deles torna-se urânio-236 com um pouco de energia a mais, o suficiente para oscilar, esticar-se num pescoço e partir-se em dois. Os dois pedaços afastam-se com cerca de 200 MeV, e os dois ou três neutrões novos que lançam podem dividir os núcleos seguintes: uma reação em cadeia.</p>
</div>`,
};

Object.assign(WT.L.labels, {
  "+{#} charge: the push grows as the proton gets closer": "carga +{#}: o empurrão cresce à medida que o protão se aproxima",
  "lead{#}": "chumbo{#}",
  "closest approach": "maior aproximação",
  "proton · {#} MeV": "protão · {#} MeV",
  "energy vs distance": "energia vs distância",
  "hill ≈ {#} MeV": "colina ≈ {#} MeV",
  "pushed back · about {#} in {#}³ tunnels through": "repelido · cerca de {#} em {#}³ passa por efeito de túnel",
  "no charge, no push": "sem carga, sem empurrão",
  "neutron · {#} eV": "neutrão · {#} eV",
  "even this crawling neutron gets in": "até este neutrão lentíssimo entra",
  "≈ {#} MeV released": "≈ {#} MeV libertados",
  "two fragments + {#} new neutrons": "dois fragmentos + {#} neutrões novos",
  "a slow neutron + U{#} → two fragments, {#}–{#} new neutrons, about {#} MeV": "um neutrão lento + U{#} → dois fragmentos, {#}–{#} neutrões novos, cerca de {#} MeV",
  "a proton this slow could never get in": "um protão tão lento nunca conseguiria entrar",
});
