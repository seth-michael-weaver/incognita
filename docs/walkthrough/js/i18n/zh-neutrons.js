/* Simplified Chinese: neutrons (第 5 章，为什么反应堆靠中子运行) */
WT.L.ch.neutrons = {
  num: "第 5 章", title: "为什么反应堆靠中子运行", short: "为什么是中子",
  html: `
<div class="step">
  <p>质子带正电，原子核里的 82 个质子也带正电。同号电荷相斥，所以质子被推开，而且越靠近，推力增长得越快（箭头）。慢速质子会在半路停下并折返，根本碰不到原子核。只有能量超过约 13 MeV，它才能越过这股推力；略低于这个值时，它有时仍然能溜进去（<b>隧穿</b>）。小图把同样的推力画成一座能量山丘。</p>
  <div class="ctl"><label for="wn-e1">质子能量 (MeV)</label><input id="wn-e1" type="range" data-bind="Ep" data-instant min="0.5" max="20" step="0.1" value="6"><output data-show="Ep" data-fmt="1"></output></div>
</div>
<div class="step">
  <p>中子不带电：无论多快多慢都能进入。没有任何东西把它推开，所以没有山丘要爬；它只需要到达原子核，然后强力就会把它拉进去。</p>
  <div class="ctl"><label for="wn-e2">中子能量（慢 → 快）</label><input id="wn-e2" type="range" data-bind="lgEn" data-instant min="-1.6" max="7.3" step="0.01" value="-1.6"><output id="wn-en-out"></output></div>
  <p>滑块从 0.025 eV（室温下中子的速度）一直到 20 MeV，相差近十亿倍。一路向下，中子依然能进入原子核。</p>
</div>
<div class="step">
  <p>所以，即使是慢中子，也能在反应堆里使铀裂变。铀-235 原子核吞下一个中子后变成铀-236，并带有一点额外的能量，足以让它摆动、拉伸出颈部并断成两半。两块碎片带着约 200 MeV 的能量飞散，它们抛出的两三个新中子又能使下一批原子核裂变：这就是链式反应。</p>
</div>`,
};
