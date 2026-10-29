/* Italian: fisout (Capitolo 14, neutroni di fissione) */
WT.L.ch.fisout = {
  num: "Capitolo 14", title: "Neutroni di fissione", short: "Neutroni di fissione",
  html: `
<div class="step">
  <p>Ogni fissione libera due o tre neutroni: 2,4 in media. In alto, una fissione alla volta: il nucleo di uranio si strappa in due frammenti e le palline blu volano via. Questi sono i neutroni <b>pronti</b> (prompt), emessi in molto meno di un milionesimo di secondo.</p>
  <p>Il grafico a sinistra conta quante fissioni hanno liberato 0, 1, 2, 3 … neutroni. Le barre sono le fissioni che hai lanciato; la linea sottile su ciascuna barra è la frazione misurata. Lanciane di più e le barre si assestano sulle linee.</p>
  <div class="btns"><button class="btn" data-act="f100">100 fissioni</button><button class="btn ghost" data-act="f1000">1000 fissioni</button></div>
</div>
<div class="step">
  <p>Nascono veloci: circa 2 MeV in media, qualcosa come 80 milioni di volte l'energia di un neutrone lento in un reattore a temperatura ambiente. Il grafico a destra ordina i neutroni pronti per energia. La linea è la forma misurata (lo spettro di Watt): una gobba vicino a 1 MeV e una lunga coda fino a 10 MeV.</p>
  <p>Neutroni così veloci raramente provocano la fissione successiva nell'uranio-235, perciò un reattore prima li rallenta, come mostra un capitolo successivo.</p>
  <div class="btns"><button class="btn" data-act="f100">100 fissioni</button><button class="btn ghost" data-act="f1000">1000 fissioni</button></div>
</div>
<div class="step">
  <p>Alcuni arrivano secondi dopo: lo 0,65 % di tutti i neutroni. Certi frammenti sono così ricchi di neutroni che, quando poi decadono, il nuovo nucleo non riesce a trattenere uno dei suoi neutroni e lo lascia andare. Questo aspetta il decadimento, spesso per secondi.</p>
  <p>La linea in basso è un orologio dopo la fissione, da 0,01 s a 100 s; ogni tacca è dieci volte più tarda della precedente. La palla a sinistra sono tutti i neutroni pronti, emessi insieme. Ogni puntino è un neutrone ritardato: scorre lungo la linea mentre la sua attesa procede, su un orologio accelerato di 20 volte, e si ferma dove è uscito alla fine. Questi pochi neutroni tardivi rendono controllabile un reattore: rallentano la risposta della catena da millesimi di secondo a secondi.</p>
  <div class="btns"><button class="btn" data-act="f1000">1000 fissioni</button><button class="btn ghost" data-act="clear">Azzera</button></div>
</div>`,
};
