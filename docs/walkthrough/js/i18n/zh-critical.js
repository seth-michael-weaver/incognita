/* Simplified Chinese: critical (第 21 章，临界与反应堆控制) */
WT.L.ch.critical = {
  num: "第 21 章", title: "临界与反应堆控制", short: "临界",
  html: `
<div class="step">
  <h3>倍增系数</h3>
  <p>每次裂变释放几个中子；其中一些引起下一次裂变，其余的则损失掉。<b>倍增系数</b> <i>k</i> 是一次裂变引起的新裂变数：每一代中子数都乘以 <i>k</i>。大于 1，链式反应增长；小于 1，则逐渐熄灭。</p>
  <div class="ctl"><label for="cri-k">倍增系数 k</label><input id="cri-k" type="range" data-bind="k" data-instant min="0.95" max="1.05" step="0.05" value="1.05"><output data-show="k" data-fmt="2"></output></div>
</div>
<div class="step">
  <h3>缓发中子</h3>
  <p>一小部分中子（0.65 %）晚到数秒，来自先要经过衰变的裂变碎片。正是这些迟到的中子决定了节奏，于是增长从一眨眼放慢到数分钟。图中以 10 倍速度演示。</p>
  <div class="ctl"><label for="cri-k2">倍增系数 k</label><input id="cri-k2" type="range" data-bind="kd" data-instant min="0.998" max="1.002" step="0.0005" value="1.001"><output data-show="kd" data-fmt="4"></output></div>
  <div class="btns"><button class="btn ghost" data-act="delayed" aria-pressed="true">缓发中子</button></div>
</div>
<div class="step">
  <h3>临界</h3>
  <p>临界实验：移动控制棒，直到功率保持平稳。此时 <i>k</i> 恰好为 1，而控制棒的位置就是测量结果。找到它：读数以五位小数显示 <i>k</i>。</p>
  <div class="ctl"><label for="cri-rod">控制棒插入 (%)</label><input id="cri-rod" type="range" data-bind="ins" data-instant min="35" max="75" step="1" value="45"><output data-show="ins" data-fmt="0"></output></div>
</div>`,
};
/* attributes referenced in the English chapter script (for the structure check): data-act="delayed" data-act="delayed" */
