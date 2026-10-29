/* Danish: landscape (Kapitel 4, kernernes landskab) */
WT.L.ch.landscape = {
  num: "Kapitel 4", title: "Kernernes landskab", short: "Landskab",
  lead: "Alle kerner, nogen nogensinde har lavet, på ét kort: 3.338 indtil videre, og kun 252 holder for evigt.",
  html: `
<div class="step">
  <h3>Nuklidkortet</h3>
  <p>Hver lille firkant er én kerne, der faktisk er set i et eksperiment: neutroner tæller på tværs, protoner tæller opad. Blege firkanter er set, men deres masse er endnu ikke vejet, kun anslået. De <b>mørke</b> firkanter er de 252, der aldrig henfalder. De andre falder fra hinanden, de orange på et øjeblik, de blå først efter år. Den <em style="font-style:normal;color:var(--proton);font-weight:600">røde</em> række er det grundstof, du vælger med skyderen: alle dets kendte isotoper.</p>
  <div class="ctl"><label for="ls-z">Se på grundstof (protoner Z)</label><input id="ls-z" type="range" data-bind="zSel" data-instant min="1" max="110" step="1" value="26"><output data-show="zSel" data-fmt="0"></output></div>
  <p class="ctl-result" id="ls-z-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>Bindingsenergi over kortet</h3>
  <p>Nu er hver firkant farvet efter sin <b>bindingsenergi pr. nukleon</b>, hvor hårdt hver neutron eller proton holdes fast (kapitel 3). De stabile kerner ligger langs en ryg af stærk binding; går man væk fra den, med for mange neutroner eller for mange protoner, falder bindingen. Den stærkeste af alle er nikkel-62. De tynde linjer markerer de <b>magiske tal</b> (8, 20, 28, 50, 82, 126), hvor kerner er ekstra stærkt bundet.</p>
</div>
<div class="step">
  <h3>Betahenfald mod stabilitet</h3>
  <p>Kerner med samme samlede antal nukleoner (samme <b>massetal</b> A) ligger på en diagonal linje hen over kortet, vist med <em style="font-style:normal;color:var(--proton);font-weight:600">rødt</em>. Start med for mange neutroner, som fragmenterne fra en spaltet urankerne har. Ved <b>betahenfald</b> bliver en neutron til en proton, så kernen rykker ét sted langs sin linje mod den stærkere bundne midte, igen og igen, indtil den når ryggen og stopper. Den lille graf viser den samme kæde som en dal, kernen ruller ned ad. Prøv A = 137: kæden passerer cæsium-137, det langlivede produkt fra reaktorulykker.</p>
  <div class="ctl"><label for="ls-a">Massetal A</label><input id="ls-a" type="range" data-bind="aSel" data-instant min="8" max="250" step="1" value="137"><output data-show="aSel" data-fmt="0"></output></div>
  <p class="ctl-result" id="ls-a-out" aria-live="polite"></p>
</div>
<div class="step">
  <h3>INCOGNITA's dækning</h3>
  <p>Det samme kort, farvet efter, hvad vores bibliotek rummer for hver kerne. <em style="font-style:normal;color:var(--fission);font-weight:600">Grøn</em>: evalueret ud fra dens målte resonanser. De øvrige har en modelfil bygget af motoren alene: <b>mørk</b> for stabile eller langlivede (niveau A), <em style="font-style:normal;color:var(--accent);font-weight:600">blå</em> for mere end et døgn (niveau B), <em style="font-style:normal;color:var(--warm);font-weight:600">orange</em> for kortlivede (niveau C). Grå er ikke i biblioteket (mest de letteste kerner og nogle få, motoren ikke kan køre).</p>
</div>`,
};
