/* Portuguese (pt-PT): tokamak (Capítulo 31, confinamento magnético) */
WT.L.ch.tokamak = {
  num: "Capítulo 31", title: "Confinamento magnético", short: "Confinamento",
  lead: "Nenhuma parede pode tocar num gás a 100 milhões de graus. Um campo magnético consegue segurá-lo, porque as partículas carregadas não podem atravessar as linhas de campo.",
  html: `
<div class="step">
  <h3>Giração num campo magnético</h3>
  <p>Na direção perpendicular ao campo, uma carga só pode andar em círculo; ao longo dele, desliza. Arrasta a figura para a rodar.</p>
  <div class="ctl"><label for="tk-b">Campo B (tesla)</label><input id="tk-b" type="range" data-bind="B" min="1" max="12" step="0.1" value="5"><output data-show="B" data-fmt="1"></output></div>
  <div class="btns tk-sp"><button class="btn ghost" data-act="spd" aria-pressed="true">Deuterão</button> <button class="btn ghost" data-act="spa" aria-pressed="false">Alfa</button> <button class="btn ghost" data-act="spe" aria-pressed="false">Eletrão</button></div>
  <div class="formula">ρ = √(2mE) / (|q| B)</div>
</div>
<div class="step">
  <h3>Linhas de campo toroidais e o fator de segurança</h3>
  <p>Um campo reto tem as pontas abertas, por isso dobra-se num anel e torce-se: um tokamak. Cada volta deixa um ponto onde a linha atravessa o corte.</p>
  <div class="ctl"><label for="tk-q">Fator de segurança q</label><input id="tk-q" type="range" data-bind="q" min="1" max="4" step="0.01" value="2.62" data-instant><output data-show="q" data-fmt="2"></output></div>
  <div class="btns"><button class="btn ghost" data-act="q32">q = 3/2</button> <button class="btn ghost" data-act="q2">q = 2</button> <button class="btn ghost" data-act="qg">q = áureo</button></div>
</div>
<div class="step">
  <h3>Ilhas magnéticas e caos das linhas de campo</h3>
  <p>As ondulações do campo rasgam as superfícies em ilhas onde q é uma fração simples, e depois em caos. Clica para lançar uma linha de campo.</p>
  <div class="ctl"><label for="tk-k">Perturbação K</label><input id="tk-k" type="range" data-bind="K" min="0" max="6" step="0.05" value="1.5" data-instant><output data-show="K" data-fmt="2"></output></div>
  <div class="formula">ψ′ = ψ − (K/2π) ψ′/(1+ψ′) sin θ<br>θ′ = θ + 2π/q(ψ′) − (K/2π) cos θ/(1+ψ′)²</div>
</div>`,
};
