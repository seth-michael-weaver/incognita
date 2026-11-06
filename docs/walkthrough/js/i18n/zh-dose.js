/* Chinese: dose (辐射剂量) */
WT.L.ch.dose = {
  num: "第3课", title: "辐射剂量", short: "剂量",
  html: `
<div class="step">
  <h3>希沃特衡量什么</h3>
  <p>剂量首先是每千克身体吸收的能量。<b>希沃特</b>再按危害大小给这份能量加权：同样的能量，由 α 粒子带来时，要比由 γ 射线带来时多算二十倍，因为它集中在少数几条密集的径迹里。</p>
  <div class="btns"><button class="btn ghost" data-act="rg" aria-pressed="true">γ 射线</button><button class="btn ghost" data-act="ra" aria-pressed="false">α 粒子</button></div>
</div>
<div class="step">
  <h3>日常剂量</h3>
  <p>这座塔上的每一格都是下面一格的十倍。拖动发光的小珠来比较：一次胸部 CT 扫描的剂量相当于好几千根香蕉，一年的天然本底辐射相当于几十次航班。</p>
  <div class="ctl"><label for="ds-l">剂量</label><input id="ds-l" type="range" data-bind="ld" data-instant min="-7" max="1" step="0.02" value="-2.15"><output class="ds-out"></output></div>
</div>
<div class="step">
  <h3>累加你的一年</h3>
  <p>每个人每年从自然界接受约 2.4 毫希沃特，其中大部分来自地下逸出的氡气。再加上你自己的航班、扫描和居住海拔。</p>
  <div class="ctl"><label for="ds-f">跨大西洋航班（次）</label><input id="ds-f" type="range" data-bind="fl" data-instant min="0" max="40" step="1" value="4"><output data-show="fl" data-fmt="0"></output></div>
  <div class="ctl"><label for="ds-ct">胸部 CT 扫描（次）</label><input id="ds-ct" type="range" data-bind="ct" data-instant min="0" max="3" step="1" value="0"><output data-show="ct" data-fmt="0"></output></div>
  <div class="ctl"><label for="ds-h">住所海拔（m）</label><input id="ds-h" type="range" data-bind="alt" data-instant min="0" max="3500" step="50" value="300"><output data-show="alt" data-fmt="0"></output></div>
</div>
<div class="step">
  <h3>一次性受到大剂量</h3>
  <p>在约 100 毫希沃特以下，额外的癌症风险小到无法测出；安全规则假定这一风险与剂量成正比增长。一次受到约一希沃特时，细胞被击中得如此频繁，放射病便开始出现。</p>
  <div class="ctl"><label for="ds-a">一次性剂量</label><input id="ds-a" type="range" data-bind="la" data-instant min="-3" max="1" step="0.02" value="-1"><output class="ds-out2"></output></div>
</div>`,
};
(function () {
  const L = {
    "{#} µSv": "{#} µSv",
    "{#} mSv": "{#} mSv",
    "{#} Sv": "{#} Sv",
    "mSv": "mSv",
    "illustration": "示意图",
    "typical values": "典型值",
    // cells
    "cell nuclei in a patch of body": "一小块身体中的细胞核",
    "cell nuclei in a patch of body tissue": "一小块身体组织中的细胞核",
    "{#} milligray of alpha: a few cells hit hard": "{#} 毫戈瑞的 α：少数细胞受到重击",
    "{#} milligray of gamma: about one track per cell": "{#} 毫戈瑞的 γ：每个细胞约一条径迹",
    "same energy · counts as {#} millisieverts": "能量相同 · 计为 {#} 毫希沃特",
    "counts as {#} millisievert": "计为 {#} 毫希沃特",
    // ladder items (long and short)
    "eating a banana  ·  {#} µSv": "吃一根香蕉  ·  {#} µSv",
    "banana  ·  {#} µSv": "香蕉  ·  {#} µSv",
    "dental X-ray  ·  {#} µSv": "牙科 X 光  ·  {#} µSv",
    "chest X-ray  ·  {#} µSv": "胸部 X 光  ·  {#} µSv",
    "flight across the Atlantic  ·  {#} µSv": "飞越大西洋  ·  {#} µSv",
    "Atlantic flight  ·  {#} µSv": "跨大西洋航班  ·  {#} µSv",
    "a year of natural background  ·  {#} mSv": "一年的天然本底辐射  ·  {#} mSv",
    "{#} yr background  ·  {#} mSv": "{#} 年本底  ·  {#} mSv",
    "chest CT scan  ·  {#} mSv": "胸部 CT 扫描  ·  {#} mSv",
    "chest CT  ·  {#} mSv": "胸部 CT  ·  {#} mSv",
    "yearly limit for radiation workers  ·  {#} mSv": "辐射工作人员年剂量限值  ·  {#} mSv",
    "worker limit/yr  ·  {#} mSv": "职业限值/年  ·  {#} mSv",
    "a year on the Kerala coast (high spots)  ·  {#} mSv": "在喀拉拉邦海岸住一年（高值点）  ·  {#} mSv",
    "Kerala, {#} yr  ·  {#} mSv": "喀拉拉，{#} 年  ·  {#} mSv",
    "a year in the highest Ramsar homes  ·  {#} mSv": "在拉姆萨尔最高剂量的住宅住一年  ·  {#} mSv",
    "Ramsar, {#} yr  ·  {#} mSv": "拉姆萨尔，{#} 年  ·  {#} mSv",
    "at once: radiation sickness begins  ·  {#} Sv": "一次性：开始出现放射病  ·  {#} Sv",
    "{#} Sv at once  ·  {#} Sv": "一次 {#} Sv  ·  {#} Sv",
    "at once: about half die untreated  ·  {#} Sv": "一次性：不治疗约半数死亡  ·  {#} Sv",
    "{#}–{#} Sv at once  ·  {#} Sv": "一次 {#}–{#} Sv  ·  {#} Sv",
    // year
    "radon in the air  {#}": "空气中的氡  {#}",
    "radon  {#}": "氡  {#}",
    "rocks and soil  {#}": "岩石和土壤  {#}",
    "ground  {#}": "地面  {#}",
    "food and water  {#}": "食物和水  {#}",
    "food  {#}": "食物  {#}",
    "cosmic rays  {#}": "宇宙射线  {#}",
    "cosmic rays at {#} m  {#}": "{#} m 处的宇宙射线  {#}",
    "cosmic  {#}": "宇宙  {#}",
    "{#} flights  {#}": "{#} 次航班  {#}",
    "flights  {#}": "航班  {#}",
    "{#} chest CT  {#}": "{#} 次胸部 CT  {#}",
    "CT  {#}": "CT  {#}",
    "average {#}": "平均 {#}",
    "world average {#} mSv": "世界平均 {#} mSv",
    "worker limit {#}": "职业限值 {#}",
    "worker limit {#} mSv": "职业限值 {#} mSv",
    "your year: {#} mSv": "你的一年：{#} mSv",
    "more than the yearly worker limit": "超过了职业人员的年剂量限值",
    "{#} times the world average": "世界平均值的 {#} 倍",
    "close to the world average": "接近世界平均值",
    // acute
    "tracks through each cell nucleus: about {#}": "穿过每个细胞核的径迹：约 {#} 条",
    "tracks through each cell nucleus: about {#} (a few drawn)": "穿过每个细胞核的径迹：约 {#} 条（只画出几条）",
    "tracks through each cell nucleus: about {#} thousand (a few drawn)": "穿过每个细胞核的径迹：约 {#} 千条（只画出几条）",
    "no effect seen": "未见效应",
    "risk assumed": "假定有风险",
    "small added risk assumed": "假定略增风险",
    "sickness": "放射病",
    "lethal": "致死",
    "often lethal": "常致死",
  };
  // dose at once: unit × message
  const MSG = [
    ["any extra risk too small to measure", "额外风险小到无法测出"],
    ["no sickness; risk assumed to rise with dose", "不发病；假定风险随剂量上升"],
    ["radiation sickness: nausea, low blood counts", "放射病：恶心、血细胞减少"],
    ["about half die without treatment", "不经治疗约半数死亡"],
  ];
  const U = ["µSv", "mSv", "Sv"];
  for (const u of U) for (const [e, z] of MSG) L[`{#} ${u} at once: ${e}`] = `一次 {#} ${u}：${z}`;
  // ladder readout: bananas / flights / years of background
  const BN = [["{#} bananas", "{#} 根香蕉"], ["{#} thousand bananas", "{#} 千根香蕉"], ["{#} million bananas", "{#} 百万根香蕉"]];
  const FL = [["{#} flights", "{#} 次航班"], ["{#} thousand flights", "{#} 千次航班"], ["{#} million flights", "{#} 百万次航班"]];
  for (const u of U) {
    for (const [be, bz] of BN) {
      L[`{#} ${u}: the dose of ${be}`] = `{#} ${u}：相当于 ${bz}的剂量`;
      for (const [fe, fz] of FL) {
        L[`{#} ${u}: ${be}, or ${fe}`] = `{#} ${u}：${bz}，或 ${fz}`;
        L[`{#} ${u}: ${be}, ${fe} or {#} years of background`] = `{#} ${u}：${bz}、${fz}或 {#} 年本底`;
      }
    }
  }
  Object.assign(WT.L.labels, L);
})();
