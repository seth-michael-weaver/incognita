/* Portuguese (pt-PT): gamow (Capítulo 30, o pico de Gamow, reatividades e ignição) */
WT.L.ch.gamow = {
  num: "Capítulo 30", title: "O pico de Gamow e a ignição", short: "Pico de Gamow",
  lead: "Um plasma quente arde através de uma janela estreita de energias: núcleos suficientemente rápidos para o efeito túnel e suficientemente numerosos para contar.",
  html: `
<div class="step">
  <h3>O pico de Gamow</h3>
  <p>Poucos núcleos são rápidos; os rápidos atravessam a barreira por efeito túnel com mais facilidade. O produto brilha: o pico de Gamow. Arrasta a linha da temperatura.</p>
  <div class="ctl"><label for="gw-t">Temperatura kT (keV)</label><input id="gw-t" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
  <div class="formula">E₀ = (E<sub>G</sub> (kT)² / 4)<sup>1/3</sup> · largura 4√(E₀kT/3)</div>
</div>
<div class="step">
  <h3>Reatividades dos combustíveis</h3>
  <p>Soma a janela inteira e obténs a reatividade ⟨σv⟩. O D–T ganha de longe a qualquer temperatura que uma máquina consiga atingir.</p>
  <div class="ctl"><label for="gw-t2">Temperatura kT (keV)</label><input id="gw-t2" type="range" data-bind="lT" min="0" max="2" step="0.01" value="1"><output data-show="T" data-fmt="1"></output></div>
  <div class="formula">⟨σv⟩ = ∫ σ(E) v f(E) dE</div>
</div>
<div class="step">
  <h3>O critério de Lawson e a ignição</h3>
  <p>Arrasta o plasma para uma temperatura e um confinamento, e larga-o. Acima da curva superior mantém-se quente sozinho.</p>
  <div class="btns"><button class="btn" data-act="lowgo">Experimenta uma máquina fraca</button> <button class="btn ghost" data-act="higo">Experimenta uma forte</button></div>
  <div class="formula">ignição: n τ<sub>E</sub> T ≳ 3·10²¹ keV s m⁻³</div>
</div>`,
};
