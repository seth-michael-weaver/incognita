/* Simplified Chinese: doppler (第 20 章，多普勒展宽) */
WT.L.ch.doppler = {
  num: "第 20 章", title: "多普勒展宽", short: "多普勒",
  html: `
<div class="step">
  <h3>靶核的热运动</h3>
  <p>燃料越热，原子抖动得越快。中子到达时，每个铀原子不再是静止的。</p>
  <div class="ctl"><label for="dop-t1">燃料温度 (K)</label><input id="dop-t1" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="600"><output data-show="T" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>多普勒展宽</h3>
  <p>曲线是铀-238 捕获中子的概率随中子能量的变化。其高度是以<b>靶恩</b>为单位的靶面积（1 靶恩是 10<sup>−24</sup> cm²，大致是原子核在中子面前显现的大小）。由于原子在运动，有的迎面撞上中子，有的则远离它，所以窄峰被抹开：变低变宽，而面积保持不变。</p>
  <div class="ctl"><label for="dop-t2">燃料温度 (K)</label><input id="dop-t2" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="1200"><output data-show="T" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>共振自屏蔽</h3>
  <p>燃料芯块很厚。阴影带是它在每个能量上阻挡的中子份额。无论冷热，峰中心已经阻挡了一切，所以更低的峰在那里并无损失；更宽的两翼则捕获更多。更多中子因被俘获而损失，而不是引起裂变，因此 <i>k</i> 自行下降。（<i>k</i> 是每次裂变引起的新裂变数；第 21 章会解释。）</p>
  <div class="ctl"><label for="dop-t3">燃料温度 (K)</label><input id="dop-t3" type="range" data-bind="T" data-instant min="300" max="1500" step="10" value="900"><output data-show="T" data-fmt="0"></output></div>
</div>`,
};
