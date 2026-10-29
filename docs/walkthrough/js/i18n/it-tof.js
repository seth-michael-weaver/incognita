/* Italian: tof (Capitolo 17, misure a tempo di volo) */
WT.L.ch.tof = {
  num: "Capitolo 17", title: "Misure a tempo di volo", short: "Misurare i picchi",
  html: `
<div class="step">
  <p>Il tempo di volo di un neutrone ne rivela l'energia. Un breve impulso di neutroni con energie di ogni tipo parte dalla sorgente e corre lungo un tubo vuoto fino al rivelatore; i veloci arrivano per primi. La lunghezza <i>L</i> del tubo è nota, quindi ogni tempo di arrivo <i>t</i> dà la velocità del neutrone, e la velocità ne dà l'energia:</p>
  <div class="formula">E = (72,3 · L / t)²   (E in eV, L in metri, t in microsecondi)</div>
  <p>L'orologio sopra il tubo conta il tempo reale dall'impulso; il volo è disegnato circa 1400 volte più lento. Sotto il tubo, l'ultimo arrivo viene convertito in un'energia. Trascina il percorso di volo: un tubo più lungo distribuisce le stesse energie su un tempo più lungo, quindi ciascuna si distingue con più finezza.</p>
  <div class="ctl"><label for="tof-l1">Percorso di volo (m)</label><input id="tof-l1" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="50"><output data-show="Lv" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Campione sottile: la buca ricalca la sezione d'urto. Ora un campione sta nel fascio. Vicino a 6,7 eV i suoi nuclei hanno una risonanza e catturano neutroni (i lampi), quindi ne arrivano meno al tempo corrispondente. Il grafico confronta i conteggi con e senza il campione: la <b>trasmissione</b>, uguale a 1 quando ogni neutrone passa.</p>
  <p>I punti sono conteggi simulati, con la loro dispersione; la linea continua è ciò che il rivelatore registra in media; la linea tratteggiata è la forma della sezione d'urto stessa. Con un campione sottile la buca ne copia la forma.</p>
  <div class="ctl"><label for="tof-d1">Spessore del campione (µm)</label><input id="tof-d1" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="0.5"><output data-show="thk" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Campione spesso: la buca satura. All'energia del picco la parte anteriore del campione cattura ogni neutrone, quindi il centro diventa nero e resta nero per quanto lo spessore aumenti; la buca può crescere solo allargandosi ai lati. Questo è l'<b>autoschermo</b>: gli strati davanti proteggono quelli dietro. Un campione spesso racconta allora più delle ali della risonanza che del suo picco.</p>
  <div class="ctl"><label for="tof-d2">Spessore del campione (µm)</label><input id="tof-d2" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="3"><output data-show="thk" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Impulsi più lunghi, voli più corti: la buca si sfoca. Tre cose determinano la larghezza di una buca, tutte scritte sotto il grafico: la larghezza propria della risonanza; l'agitazione termica degli atomi del campione, che sfuma un poco l'energia di ogni collisione (allargamento <b>Doppler</b>); e la sfocatura temporale, perché un impulso più lungo o un tubo più corto rende ogni tempo di arrivo, e quindi ogni energia, meno certo.</p>
  <p>Allunga l'impulso o accorcia il tubo: la buca diventa più larga e meno profonda, anche se la frazione di neutroni che rimuove resta circa la stessa.</p>
  <div class="ctl"><label for="tof-p1">Larghezza dell'impulso (µs)</label><input id="tof-p1" type="range" data-bind="lgDt" data-instant min="-2" max="1" step="0.01" value="0.3"><output data-show="dt" data-fmt="2"></output></div>
  <div class="ctl"><label for="tof-l2">Percorso di volo (m)</label><input id="tof-l2" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="20"><output data-show="Lv" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>INCOGNITA lavora a ritroso: prende conteggi misurati come questi e chiede quale risonanza, sottoposta a questo stesso esperimento (spessore, temperatura, sfocatura temporale), li riproduce. Qui l'adattamento parte da una stima la cui larghezza neutronica Γ<sub>n</sub> (quanto saldamente il livello trattiene i neutroni) è quasi quattro volte troppo grande (la curva blu), e la modifica passo dopo passo finché la curva passa per i punti.</p>
  <p>L'indicatore mostra la stima corrente e il <b>disadattamento</b>: circa 1 significa che la curva è vicina ai punti quanto lo consente la loro dispersione di conteggio. Cambia l'esperimento e l'adattamento riparte, da nuovi conteggi, e approda a una larghezza vicina alla stessa; dove non riesce a combaciare bene con i punti, il disadattamento lo dice.</p>
  <div class="ctl"><label for="tof-l3">Percorso di volo (m)</label><input id="tof-l3" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="50"><output data-show="Lv" data-fmt="0"></output></div>
  <div class="ctl"><label for="tof-d3">Spessore del campione (µm)</label><input id="tof-d3" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="1.5"><output data-show="thk" data-fmt="0"></output></div>
  <div class="ctl"><label for="tof-p2">Larghezza dell'impulso (µs)</label><input id="tof-p2" type="range" data-bind="lgDt" data-instant min="-2" max="1" step="0.01" value="-1"><output data-show="dt" data-fmt="2"></output></div>
</div>`,
};
