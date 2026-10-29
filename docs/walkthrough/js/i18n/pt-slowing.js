/* Portuguese (pt-PT): slowing (Capítulo 18, moderação de neutrões) */
WT.L.ch.slowing = {
  num: "Capítulo 18", title: "Moderação de neutrões", short: "Abrandamento",
  html: `
<div class="step">
  <p>Cada ressalto no hidrogénio custa cerca de metade da energia. Um neutrão de fissão parte com 2 MeV e ressalta pela água. Um núcleo de hidrogénio pesa o mesmo que o neutrão, pelo que, como bolas de bilhar, cada ressalto lhe tira em média metade da energia do neutrão.</p>
  <p>O gráfico mostra a energia do neutrão após cada ressalto; cada marca ao longo do lado tem mil vezes menos energia. Perder a mesma fração de cada vez dá uma descida em linha reta, a tracejado. Ao fim de cerca de 18 ressaltos o neutrão atinge a energia <b>térmica</b>, 0,025 eV, onde a água quente o empurra para cima tantas vezes quantas o abranda. O oxigénio é 16 vezes mais pesado: cada ressalto tira pouco, e são precisos mais de cem.</p>
  <div class="btns"><button class="btn ghost" data-act="tgtH" aria-pressed="true">Hidrogénio</button><button class="btn ghost" data-act="tgtO" aria-pressed="false">Oxigénio</button><button class="btn" data-act="again">Disparar de novo</button></div>
</div>
<div class="step">
  <p>Abaixo de cerca de 1 eV, as ligações da molécula moldam cada ressalto. Cada hidrogénio está preso ao seu oxigénio (as linhas brilhantes). Um neutrão lento já não bate num hidrogénio livre: bate numa molécula inteira, 18 vezes mais pesada, e um ressalto simples quase nada tira.</p>
  <p>Também pode fazer a molécula rodar ou vibrar, mas só cedendo uma quantidade fixa de energia de cada vez, 0,06, 0,2 ou 0,45 eV (os clarões brilhantes). As moléculas quentes por vezes devolvem uma quantidade destas. No gráfico, a faixa sombreada abaixo de 1 eV é onde isto importa. Desliga a ligação para comparar com o hidrogénio livre.</p>
  <div class="btns"><button class="btn ghost" data-act="bind" aria-pressed="true">Ligação química</button><button class="btn" data-act="again">Disparar de novo</button></div>
</div>
<div class="step">
  <p>Um código de computador precisa de tudo isto sob a forma de tabela: a <b>lei de dispersão</b>, o mapa. Na horizontal: a força da pancada, α (o impulso dado à molécula; pequeno num toque rasante, grande num choque frontal). Na vertical: a energia que o neutrão ganha (para cima) ou perde (para baixo), β, contada em unidades da energia térmica da água, 0,025 eV. Brilhante significa provável, pálido significa raro.</p>
  <p>O contorno é o que um neutrão da energia escolhida consegue alcançar: não pode perder mais do que tem, e cada variação de energia só permite um intervalo de pancadas. Arrasta a energia e o contorno cresce ou encolhe. Sem ligação, o mapa é o de um gás de hidrogénio livre, uma crista brilhante ao longo da linha tracejada de recuo; com ligação, a molécula acrescenta riscas brilhantes, as suas quantidades fixas de energia. A INCOGNITA calcula as suas próprias leis para a água e o berílio: <a href="https://github.com/seth-michael-weaver/incognita/tree/main/library/tsl-v0.1" style="white-space:nowrap">tsl-v0.1</a>.</p>
  <div class="ctl"><label for="slo-e">Energia do neutrão (eV)</label><input id="slo-e" type="range" data-bind="lgE" data-instant min="-2.3" max="0" step="0.01" value="-1"><output data-show="Eshow" data-fmt="3"></output></div>
  <div class="btns"><button class="btn ghost" data-act="bind" aria-pressed="true">Ligação química</button></div>
</div>`,
};
/* i18n_check.sh counts these attribute strings found in the English script code (not in html): data-act="${act}" */
