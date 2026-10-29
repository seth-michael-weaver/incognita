/* Simplified Chinese: tof (第 17 章，飞行时间测量) */
WT.L.ch.tof = {
  num: "第 17 章", title: "飞行时间测量", short: "测量共振峰",
  html: `
<div class="step">
  <p>中子的飞行时间决定它的能量。一个包含各种能量中子的短脉冲离开中子源，沿着一根空管飞向探测器；快中子最先到达。管长 <i>L</i> 已知，因此每个到达时间 <i>t</i> 给出中子的速度，速度再给出它的能量：</p>
  <div class="formula">E = (72.3 · L / t)²   （E 单位 eV，L 单位 m，t 单位 µs）</div>
  <p>管子上方的时钟显示脉冲发出后的真实时间；飞行过程大约被放慢了 1400 倍来绘制。管子下方，最后一个到达的中子被换算成能量。拖动飞行距离：管子越长，同样的能量散布在更长的时间上，每个能量就能分辨得更细。</p>
  <div class="ctl"><label for="tof-l1">飞行距离 (m)</label><input id="tof-l1" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="50"><output data-show="Lv" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>薄样品：凹陷描出截面的形状。现在束流中放了一块样品。在 6.7 eV 附近，它的原子核有一个共振并抓住中子（闪光），所以在对应的时间到达的中子变少。图表比较有样品和没有样品时的计数：即<b>透射率</b>，每个中子都穿过时为 1。</p>
  <p>圆点是模拟计数，带有涨落；实线是探测器平均记录到的结果；虚线是截面本身的形状。样品很薄时，凹陷复制的就是这个形状。</p>
  <div class="ctl"><label for="tof-d1">样品厚度 (µm)</label><input id="tof-d1" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="0.5"><output data-show="thk" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>厚样品：凹陷饱和。在峰值能量处，样品前部就捕获了每一个中子，所以中心变黑，无论样品多厚都保持黑色；凹陷只能向两侧变宽。这就是<b>自屏蔽</b>：前面的层屏蔽了后面的层。于是，厚样品更多地反映共振的两翼，而不是它的峰顶。</p>
  <div class="ctl"><label for="tof-d2">样品厚度 (µm)</label><input id="tof-d2" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="3"><output data-show="thk" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>脉冲更长、飞行更短：凹陷变模糊。决定凹陷宽度的有三个因素，都写在图表下方：共振本身的宽度；样品原子的热运动，它使每次碰撞的能量略有弥散（<b>多普勒</b>展宽）；以及时间上的模糊，因为脉冲越长或管子越短，每个到达时间、进而每个能量就越不确定。</p>
  <p>加长脉冲或缩短管子：凹陷变得更宽、更浅，但它移除的中子份额大致不变。</p>
  <div class="ctl"><label for="tof-p1">脉冲宽度 (µs)</label><input id="tof-p1" type="range" data-bind="lgDt" data-instant min="-2" max="1" step="0.01" value="0.3"><output data-show="dt" data-fmt="2"></output></div>
  <div class="ctl"><label for="tof-l2">飞行距离 (m)</label><input id="tof-l2" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="20"><output data-show="Lv" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>INCOGNITA 反向工作：它取这样的实测计数，问哪一个共振在经过同样的实验（厚度、温度、时间模糊）之后能再现它们。这里拟合从一个猜测出发，其中子宽度 Γ<sub>n</sub>（能级抓住中子的强弱）大了将近四倍（蓝色曲线），并一步步修改它，直到曲线穿过圆点。</p>
  <p>读数显示当前的猜测和<b>失配度</b>：约为 1 表示曲线与圆点的接近程度已达到其计数涨落所允许的极限。改变实验条件，拟合就从新的计数重新开始，并落在几乎相同的宽度附近；若无法与圆点很好地吻合，失配度会说明这一点。</p>
  <div class="ctl"><label for="tof-l3">飞行距离 (m)</label><input id="tof-l3" type="range" data-bind="Lv" data-instant min="5" max="200" step="1" value="50"><output data-show="Lv" data-fmt="0"></output></div>
  <div class="ctl"><label for="tof-d3">样品厚度 (µm)</label><input id="tof-d3" type="range" data-bind="lgT" data-instant min="0" max="3.5" step="0.01" value="1.5"><output data-show="thk" data-fmt="0"></output></div>
  <div class="ctl"><label for="tof-p2">脉冲宽度 (µs)</label><input id="tof-p2" type="range" data-bind="lgDt" data-instant min="-2" max="1" step="0.01" value="-1"><output data-show="dt" data-fmt="2"></output></div>
</div>`,
};
