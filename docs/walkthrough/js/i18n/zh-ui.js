/* Simplified Chinese (简体中文): static page text (index.html data-i18n keys) and kit UI strings */
Object.assign(WT.L.ui, {
  lang_label: "语言", nav_teach: "教师指南",
  brand: "走进核反应", nav_physics: "物理原理", nav_data: "全部核素", nav_board: "记分板", menu: "菜单", site_nav: "网站",
  ways_h: "更多入口", ways_more: "或者继续向下滚动：物理部分从这里开始 ↓",
  way1_k: "探索", way1_t: "全部核素", way1_p: "6168 个核素的预测截面，与每一组经过整理的测量数据并列。可以搜索任意同位素，查看每个数据集。", way1_go: "打开数据 →",
  way2_k: "比较", way2_t: "记分板", way2_p: "以测量数据为准，比较本引擎及其数据产品与其他反应程序和数据库的表现，落后项排在最前。", way2_go: "查看结果 →",
  way3_k: "运行", way3_t: "源代码", way3_p: "这里的一切都是开源的。克隆代码仓库，查询任意一条曲线，或者亲自运行引擎。", way3_go: "GitHub →",
  title: "走进核反应",
  kicker: "INCOGNITA 反应引擎交互式讲解",
  h1: "走进核反应",
  hero1: "用一个中子轰击原子核，总会有东西飞出来。可能是中子本身被弹了回来；也可能是一个质子、一个α粒子（由 2 个质子和 2 个中子紧密结合成的集团），或是一道闪光。重原子核甚至可能一分为二。",
  hero2: "究竟会发生哪一种，概率又有多大？本页一步一步地介绍我们的软件如何回答这个问题。请向下滚动，并随手试试沿途的控件。图中的物理与引擎完全一致；图中的数字仅作示意。",
  scrollcue: "向下滚动开始 ↓",
  hero_tag: "核物理的可视化探索",
  hero_aud: "面向学生和刚接触核物理的人，以及教授他们的教师。专业人士：每个核素的数据见<a href=\"data.html\" data-keep-lang>全部核素</a>。",
  hero_fire: "发射一个中子",
  hero_hint: "或点击图中任意位置",
  credit_idx: "INCOGNITA 引擎移植自 <a href=\"https://doi.org/10.1140/epja/s10050-023-01034-3\">TALYS-2</a>（A. J. Koning、S. Hilaire、S. Goriely），并使用 TALYS 的核结构数据库。INCOGNITA 新增的内容<a href=\"#code\">在本页末尾逐个开关地列出</a>。",
  coda_h2: "这些内容在代码中的位置",
  coda_p1: "上面的每个阶段都是 <code>physics/hf</code> 中的一个程序包，引擎按照你刚才阅读的顺序调用它们。引擎移植自成熟的反应程序 TALYS-2.x。新增的内容位于同一批程序包中、由具名开关控制：大多数默认关闭，少数修正默认开启，而且每一项都可以单独切换回原版 TALYS。",
  coda_table: `
    <thead><tr><th>章节</th><th>功能</th><th>代码</th></tr></thead>
    <tbody>
      <tr><td><a href="#structure">1</a></td><td>质量、能级、形变、共振数据</td><td><code>structure/</code></td></tr>
      <tr><td><a href="#omp">5</a></td><td>光学模型、穿透系数（粒子进出原子核的难易程度）</td><td><code>omp/</code></td></tr>
      <tr><td><a href="#direct">6</a></td><td>耦合道、DWBA、巨共振、直接俘获（可选）</td><td><code>ecis/</code>, <code>direct/</code></td></tr>
      <tr><td><a href="#preeq">7</a></td><td>预平衡：激子模型、拾取与敲出、多次发射</td><td><code>preeq/</code>, <code>density/particle_hole.py</code></td></tr>
      <tr><td><a href="#compound">8</a></td><td>能级密度（每 MeV 的状态数）、自旋分布</td><td><code>density/</code></td></tr>
      <tr><td><a href="#decay">9</a></td><td>选择出射道（Hauser–Feshbach）、宽度涨落</td><td><code>compound/</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>光子强度与 γ 穿透；分立能级与同质异能态</td><td><code>gamma/</code><br><code>structure/levels.py</code></td></tr>
      <tr><td><a href="#cascade">11</a></td><td>粒子与 γ 发射的级联、排他反应道、剩余核</td><td><code>emission/</code></td></tr>
      <tr><td><a href="#fission">12</a></td><td>裂变势垒与穿透</td><td><code>fission/</code></td></tr>
      <tr><td><a href="#measure">17</a></td><td>发射谱、角分布与双微分截面（可选，仅输出）</td><td><code>specout.py</code><br><code>specang.py</code></td></tr>
      <tr><td><a href="#measure">17</a></td><td>热激发靶核上的俘获与恒星反应率（可选）</td><td><code>astro/stellar.py</code></td></tr>
      <tr><td><a href="#measure">17</a></td><td>通过大量随机变体评估不确定度（全蒙特卡罗）</td><td><code>tmc.py</code></td></tr>
      <tr><td></td><td>按顺序运行各阶段的主控程序，以及用于加速的可选 C 内核</td><td><code>engine.py</code><br><code>engine_c.py</code>, <code>native/</code></td></tr>
      <tr><td></td><td>所有默认值和选项，在开始时读取一次；还有 TENDL 逐核素拟合的参数，按 TALYS 的方式使用（可选）</td><td><code>input/</code></td></tr>
    </tbody>
  `,
  coda_h3_added: "TALYS 之外的新增内容",
  coda_p_added: "标为<b>开启</b>的行默认运行，因此默认运行的结果不再与 TALYS 完全一致；每一项都可以用一个关键字或环境变量关闭。其余各项除非设置，否则保持关闭。",
  coda_table_added: `
    <thead><tr><th>章节</th><th>改动内容</th><th>代码</th></tr></thead>
    <tbody>
      <tr><td><a href="#cascade">11</a></td><td><b>开启。</b>通量记账闭合：剩余核保留到 10⁻⁹ mb（TALYS：10⁻³ mb），保留超出 TALYS 级联窗口一步的剩余核，排他反应道中每种出射粒子最多计 8 个，一个能级重复出现的退激分支全部计入</td><td><code>emission/fluxclose.py</code><br><code>emission/channels.py</code><br><code>kevleak2.py</code></td></tr>
      <tr><td><a href="#decay">9</a></td><td><b>开启。</b>第一个复合核的最高能量区间按初级光子的填充方式（以 E<sub>γ</sub>³ 加权）填充，而不是均匀填充</td><td><code>compound/nnleak.py</code></td></tr>
      <tr><td><a href="#decay">9</a></td><td><b>开启。</b>在最低的几个共振以下（低于 1 keV）不计平均复合弹性散射，那里的弹性散射是势散射</td><td><code>lowepot.py</code></td></tr>
      <tr><td><a href="#decay">9</a></td><td><b>开启。</b>无裂变的形变靶核：通往耦合带以外能级的中子出射道采用耦合道穿透系数</td><td><code>compound/ccexitnb.py</code></td></tr>
      <tr><td><a href="#omp">5</a></td><td><b>开启。</b>α发射所见的势依赖于剩余核的温度；α入射粒子通过 α 模型 6 进入；氚核与氦-3 的势计入入射粒子的尺寸</td><td><code>omp/alphatemp.py</code><br><code>alphaentr.py</code><br><code>omp/tfold.py</code></td></tr>
      <tr><td><a href="#fission">12</a></td><td><b>开启。</b>精确计算穿过每个势垒峰的一维穿透</td><td><code>fission/wkb.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td><b>开启。</b>运行中若提供了逐核的 E1/M1 强度因子，则以一个关于形变的全局函数取代</td><td><code>gamma/ftglobal.py</code></td></tr>
      <tr><td><a href="#compound">8</a></td><td><b>开启。</b>对没有自身实测共振间距 D₀ 的靶核：在 max(E<sub>cut</sub> + 2, S<sub>n</sub> − 6) MeV 以上，将靶核连续区的能级密度乘以一个因子，该因子由一条基于宇称、壳层和形变特征的全局规则给出。加入它是为了把阈能附近 (n,p) 对 TALYS-2 默认输入的落后变为持平；它使俘获、(n,2n) 和 (n,α) 的几个视角略有变差，这一代价已被接受并记录</td><td><code>density/npwindow.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>形变核中更强的剪刀模式，采用与 Oslo 测量相符的较新系统学（在锕系核中约为 4–5 倍）；或一种按形变缩放其能量和强度的变体</td><td><code>gamma/scissors.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>重新标定光子强度，使每个原子核与其测得的辐射强度 ⟨Γγ⟩/D₀ 一致，适用于级联中的每个原子核，而不仅是第一个</td><td><code>gamma/ggnorm.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>仅对最重的原子核（Z ≥ 88）采用更强的剪刀模式和 ⟨Γγ⟩ 归一化，面向 keV 能区的俘获</td><td><code>gamma/actphys.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>用我们自己的 E1 宽度常数取代 TALYS 由 TENDL 导出的表格（随附的无数据配方会设定它）</td><td><code>gamma/e1_width.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>准连续区中转动带的集体 E2 强度</td><td><code>gamma/isoe2.py</code></td></tr>
      <tr><td><a href="#omp">5</a></td><td>针对形变稀土靶核的光学势阱区域性调整，拟合测得的 S₀ 和 S₁，不使用俘获数据</td><td><code>omp/regional.py</code></td></tr>
      <tr><td><a href="#omp">5</a></td><td>由测得的中子强度函数 S₀、S₁ 确定低能中子穿透</td><td><code>omp/sfunc.py</code></td></tr>
      <tr><td><a href="#direct">6</a></td><td>直接俘获到束缚轨道，并修复了上游问题：在原版 TALYS 中，除非同时要求输出光学模型的全部结果，否则它返回零</td><td><code>direct/racapcalc.py</code></td></tr>
      <tr><td><a href="#direct">6</a></td><td>根据靶核测得的能级选择其耦合方案（转动核、振动核、球形核）</td><td><code>structure/collrule.py</code></td></tr>
      <tr><td><a href="#structure">1</a></td><td>连续区从实测能级纲图不再完整的位置开始</td><td><code>structure/levcomplete.py</code></td></tr>
      <tr><td><a href="#structure">1</a></td><td>若某能级列出的自旋对该原子核不可能（奇 A 核却为整数），则按自旋未知的能级处理</td><td><code>structure/levjpar.py</code></td></tr>
      <tr><td><a href="#compound">8</a></td><td>恒温能级密度锚定在分立能级的完整部分上</td><td><code>density/ctwindow2.py</code></td></tr>
      <tr><td><a href="#fission">12</a></td><td>裂变鞍点上过渡态的转动带</td><td><code>fission/barriers.py</code></td></tr>
      <tr><td><a href="#resonance">15</a></td><td>恒星窗口中只有少数几个共振时的俘获：取一个共振序列的典型值，而不是平均值</td><td><code>fewres.py</code></td></tr>
      <tr><td></td><td>远离稳定线时的四项防护：直接通量受幺正性限制，费米能设上限，奇奇核默认不加集体性，预平衡自旋分布归一化</td><td><code>engphys.py</code></td></tr>
    </tbody>
  `,
  coda_h3_outside: "引擎之外",
  coda_p_outside: "故事中有些部分在引擎旁边运行，而不在引擎内部。<a href=\"#resonance\">第 15 章</a>的统计共振序列位于 <code>physics/resonance/</code>。<a href=\"#measure\">第 17 章</a>的麦克斯韦平均（MACS）是在运行结束后，由引擎给出的俘获曲线在 <code>validation/differential/core.py</code> 中折算得到的；而热激发靶核上的俘获和恒星反应率则由引擎本身计算（<code>astro/stellar.py</code>，可选）。<a href=\"#layers\">第 21 章</a>的锚定层位于 <code>incognita/terra/</code>。",
  close: "关闭",
  chapters: "章节",
  nav_board: "记分板", nav_data_short: "数据",
  coda_repo: "代码、数据库和经过整理的测量数据都是开放的：<a href=\"https://github.com/seth-michael-weaver/incognita\">GitHub 上的 seth-michael-weaver/incognita</a>。你可以在<a href=\"data.html?lang=zh\" data-keep-lang>全部核素</a>页面亲自查询任何预测结果，也可以克隆代码仓库自行运行。",
  diagram: "示意图",
});

Object.assign(WT.L.ui, { pause_sweep: "暂停扫描", play_sweep: "继续扫描" });

/* course mode: audience note, chapter level tags, per-step links */
Object.assign(WT.L.ui, {
  audience: '<b>适合谁读：</b>任何有好奇心的人。前几章不需要物理基础，后面几章则达到研究水平。每一章都带有一个标签：<span class="lvl l0">入门</span>、<span class="lvl l1">中级</span>、<span class="lvl l2">高级</span>或<span class="lvl l3">专家</span>。想用于教学？请看<a href="instructors.html" data-keep-lang>教师指南</a>。',
  lvl0: "入门", lvl1: "中级", lvl2: "高级", lvl3: "专家", lvl_title: "难度",
  xp_kicker: "第二部分 · 专家",
  xp_h: "深入细节",
  xp_p: "前面各章把每一步都讲成一幅图。接下来的六章把同样的步骤逐一展开：引擎计算的公式、公式中包含的近似，以及这些近似力不从心的地方。它们是为评价工作者、模型开发者和研究生写的。图中的公式是实时计算的，所用输入仅作示意。",
  step_link: "复制指向此步骤的链接", link_copied: "链接已复制",
});
