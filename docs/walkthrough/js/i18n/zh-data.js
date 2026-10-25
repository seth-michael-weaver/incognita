/* Simplified Chinese (简体中文): data explorer (data.html, js/data.js) */
Object.assign(WT.L.ui, {
  lang_label: "语言", nav_teach: "教师指南",
  brand: "走进核反应", nav_physics: "物理原理", nav_data: "全部核素", nav_board: "记分板", menu: "菜单", site_nav: "网站",
  dx_title: "全部核素 · 走进核反应",
  site_nav: "网站", nav_walk: "导览", nav_board: "记分板", nav_data: "全部核素", nav_repo: "GitHub 上的代码",
  dx_kicker: "INCOGNITA · 数据浏览器",
  dx_h1: "全部核素",
  dx_lede: "引擎为数据库中每个核素预测的中子截面，与每个核素经过整理的测量数据并列展示。可以在核素图上选取一个核素，也可以直接搜索。",
  dx_lede_ver: "这些曲线是 v0.2 数据库（2026 年 10 月），由记分板计分的同一引擎版本（2026 年 10 月 22 日的引擎）生成。它们不是 TERRA——记分板上那个针对测量数据拟合的数据产品。每条曲线都是引擎自己的预测，没有一条针对旁边所示的测量数据拟合；唯一的例外是标为已锚定的核素：其曲线乘以一个系数，使 30 keV 处的恒星平均值等于测量值。引擎的总体设置是针对所有核素一次性选定的，用到了许多测量数据（包括这些），因此在已测量核素上的吻合是对模型的公平检验，但并非完全独立。大多数核素从未被测量（外推），它们的区间很宽。",
  dx_controls: "核素图控件", dx_search_label: "查找核素", dx_search_ph: "搜索：U-235、Fe56、Au…",
  dx_colour: "核素图着色依据", dx_m_tier: "已知程度", dx_m_macs: "30 keV 俘获", dx_m_meas: "测量数据",
  dx_chart_h: "核素图",
  dx_chart_aria: "核素图：质子数向上，中子数向右。使用搜索框选取核素。",
  dx_hint: "拖动以平移，滚动滚轮或双指捏合以缩放。点击方格即可打开，该核素的详细信息显示在图表下方。质子数向上，中子数向右。",
  dx_full: "显示完整能量范围", dx_mk_thr: "阈能", dx_mk_cb: "库仑势垒",
  dx_show_excl: "显示整理时排除的数据点", dx_table: "以表格显示",
  dx_run_h: "亲自获取这些数字", dx_copy: "复制", dx_copied: "已复制",
  dx_repo_h: "亲自运行",
  dx_repo_p: "本页的一切都来自开放的代码仓库：引擎、数据库和经过整理的测量数据。你需要 Linux 或 macOS、Python 3.12 和 <a href=\"https://docs.astral.sh/uv/\">uv</a>。",
  credit_sub: "INCOGNITA 引擎移植自 <a href=\"https://doi.org/10.1140/epja/s10050-023-01034-3\">TALYS-2</a>（A. J. Koning、S. Hilaire、S. Goriely），并使用 TALYS 的核结构数据库。INCOGNITA 新增的内容<a href=\"./?lang=zh#code\" data-keep-lang>在教学页面末尾逐个开关地列出</a>。",
  dx_repo_p2: "运行引擎本身还需要 TALYS 结构数据库；README 中说明了如何获取。",
  dx_repo_link: "GitHub 上的 seth-michael-weaver/incognita →",
  dx_src: "来源：预测值来自 v0.2 数据库（<code>library/v0.2</code>）；俘获测量数据来自 EXFOR，经 <code>data/curation</code> 整理；(n,2n)、(n,p) 和 (n,α) 测量数据来自 <code>incognita/bench</code> 中的基准条目。整理时排除的测量数据默认隐藏，除非你选择显示。可选的评价数据库叠加曲线（虚线，ENDF/B-VIII.1、JEFF-4.0、TENDL-2025）由 <code>scripts/build_site_overlay.py</code> 生成，仅供显示；INCOGNITA 从不读取它们。",
  dx_t0: "已测量", dx_t1: "锚定到实测 MACS", dx_t2: "插值（靠近已测量核素）", dx_t3: "外推",
  dx_ts0: "已测量", dx_ts1: "已锚定", dx_ts2: "插值", dx_ts3: "外推",
  dx_keep: "保留", dx_down: "降低权重", dx_excl: "排除", dx_fix: "单位已修正",
  dx_cap: "俘获 (n,γ)", dx_macs: "恒星平均（MACS）", dx_nat: "天然",
  dx_l_cap: "有俘获测量", dx_l_thr: "仅有 (n,2n)、(n,p) 或 (n,α) 测量", dx_l_none: "本数据集中无测量",
  dx_l_macs: "kT = 30 keV 时预测的麦克斯韦平均俘获截面（对数坐标）", dx_l_nomacs: "无数值",
  dx_capsets: "个俘获数据集", dx_measured: "已测量",
  dx_outside: "超出验证范围（Z 26–83）", dx_flag: "可分辨共振延伸到 MACS 窗口内：建议使用实测 MACS",
  dx_nocurve: "此条目没有数据库曲线；测量数据来自",
  dx_xE: "中子能量", dx_pred: "预测（数据库 v0.2）",
  dx_res: "可分辨共振区：此处曲线为平均值",
  dx_empty: "此反应没有可显示的内容。", dx_bands: "区间：68 % 和 95 %", dx_band68: "区间：68 %",
  dx_meas_pts: "测量点", dx_table_hint: "点击“以表格显示”查看数值。", dx_ds_h: "测量数据", dx_pts: "点",
  dx_th_src: "来源", dx_th_val: "数值", dx_th_unc: "范围 / 不确定度", dx_th_cur: "整理",
  dx_s_p: "质子", dx_s_n: "中子", dx_s_macs: "恒星中 30 keV 的俘获", dx_s_pts: "俘获测量点", dx_s_thr: "(n,2n)、(n,p)、(n,α) 数据点", dx_sets: "个数据集",
  dx_exfor_click: "点击数据点即可打开", dx_exfor_tap: "再点一次或点这里即可打开",
  dx_mxw: "麦克斯韦平均", dx_state: "状态", dx_cur: "整理", dx_fail: "无法加载数据。", dx_loading: "加载中", dx_nload: "无法加载此核素。", dx_retry: "重试",
});

/* downloads and data access */
Object.assign(WT.L.ui, {
  dx_dl: "下载此核素：",
  dx_dl_note: "此核素的每条曲线和每个测量点，涵盖所有反应，文件中写明单位、来源和 EXFOR 编号。",
  dx_access: "<b>数据获取。</b>这里显示的所有内容都在代码仓库的 <a href=\"https://github.com/seth-michael-weaver/incognita/tree/main/library/v0.2\"><code>library/v0.2</code></a> 下：带 68 / 95 % 区间的俘获曲线（<code>capture_v02.parquet</code>）、麦克斯韦平均（<code>macs30_v02.csv</code>、<code>macs_kt_v02.csv</code>）、恒星反应率（<code>rates_v02.csv</code>、<code>reaclib_v02.dat</code>）以及 (n,2n)、(n,p)、(n,α) 反应道（<code>channels_v02.parquet</code>、<code>grid_np_v02.parquet</code>），并由 <code>SHA256SUMS</code> 校验。如果只需要一个核素，上面的 CSV 和 JSON 下载就足够了。经过整理的测量数据位于 <code>data/curation</code>；它们来自 EXFOR（国际原子能机构核数据科），并保留其 EXFOR 编号。数据库数据采用 CC-BY-4.0 许可。较早的 v0.1 保留在 <code>library/v0.1</code>；改动见 <code>library/v0.2</code> 中的 <code>CHANGELOG.md</code>。",
});
Object.assign(WT.L.ui, {
  dx_lib: "叠加评价数据库（仅供比较——INCOGNITA 不使用）",
  dx_eval: "评价", dx_lib_pd: "美国公共领域", dx_lib_loading: "正在加载数据库…",
  dx_lib_bin: "数据库：区间平均",
  dx_lib_note: "虚线是评价核数据库，仅供比较：INCOGNITA 不使用它们，下载文件中也不包含它们。每个数据库都由其 ENDF-6 文件（经 NJOY）在 0 K 下重建，并在与曲线相同的能量区间上取平均（按能量对数取区间平均，因此共振被平滑掉）；MACS 则使用完整的逐点曲线。",
  dx_lib_none: "以下数据库中没有此核素的文件：", dx_lib_notab: "以下数据库中此反应没有单独的数值：",
  dx_lib_held: "JENDL-5 将在其再分发衍生表格的条款确认后加入。",
});

/* library v0.2: a nuclide whose capture below 1 MeV hinges on one engine setting ({n}: the factor at 30 keV) */
Object.assign(WT.L.ui, {
  dx_mf_pe_lo: "模型选择不确定：本引擎在所有能量下都允许粒子在原子核达到平衡之前逸出（预平衡发射），而 TALYS 只在约 1 MeV 以上才这样做；按 TALYS 的选择，30 keV 处的俘获约为现值的 1/{n}，1 MeV 以下的 95 % 区间涵盖两者。",
  dx_mf_pe_hi: "模型选择不确定：本引擎在所有能量下都允许粒子在原子核达到平衡之前逸出（预平衡发射），而 TALYS 只在约 1 MeV 以上才这样做；按 TALYS 的选择，30 keV 处的俘获约为现值的 {n} 倍，1 MeV 以下的 95 % 区间涵盖两者。",
  dx_mf_pe_near: "模型选择不确定：本引擎在所有能量下都允许粒子在原子核达到平衡之前逸出（预平衡发射），而 TALYS 只在约 1 MeV 以上才这样做；按 TALYS 的选择，30 keV 处结果一致，但在 1 MeV 以下的其他能量相差超过 2 倍，那里的 95 % 区间涵盖两者。",
  dx_mf_fi_lo: "模型选择不确定：在 1 MeV 以下，这条曲线取决于引擎中关于原子核如何越过裂变势垒的一项设置；按另一种选择，30 keV 处的俘获约为现值的 1/{n}，1 MeV 以下的 95 % 区间涵盖两者。",
  dx_mf_fi_hi: "模型选择不确定：在 1 MeV 以下，这条曲线取决于引擎中关于原子核如何越过裂变势垒的一项设置；按另一种选择，30 keV 处的俘获约为现值的 {n} 倍，1 MeV 以下的 95 % 区间涵盖两者。",
  dx_mf_fi_near: "模型选择不确定：在 1 MeV 以下，这条曲线取决于引擎中关于原子核如何越过裂变势垒的一项设置；按另一种选择，30 keV 处结果一致，但在 1 MeV 以下的其他能量相差超过 2 倍，那里的 95 % 区间涵盖两者。",
  dx_mf_gg_lo: "这条曲线使用了 TALYS 和 TENDL 不采用的一项原子核伽马衰变修正；若不修正，30 keV 处的俘获约为现值的 1/{n}。",
  dx_mf_gg_hi: "这条曲线使用了 TALYS 和 TENDL 不采用的一项原子核伽马衰变修正；若不修正，30 keV 处的俘获约为现值的 {n} 倍。",
  dx_mf_gg_near: "这条曲线使用了 TALYS 和 TENDL 不采用的一项原子核伽马衰变修正；若不修正，30 keV 处的俘获大致相同。",
});

/* pointwise library comparators below 1 keV and the measured thermal value (KONINGOVERLAY) */
Object.assign(WT.L.ui, {
  dx_eval_cmp: "评价库 · 仅作比较，非 INCOGNITA",
  dx_pw_leg2: "1 keV 以下为实线：逐点、0 K",
  dx_lib_pw_dense: "该核素在 1 keV 以下共振很多，因此保留更多的点：每个共振峰 5 个点，最多 5000 个（若固定为 500 个点，U-235 或 Pu-239 的许多峰会被截掉）。",
  dx_pw_short: "0 K 逐点，1 keV 以下",
  dx_lib_pw: "1 keV 以下，同样的评价库以细实线逐点绘出：在 0 K 下重建（NJOY RECONR，容差 0.01 %），每条曲线精简至最多 {n} 个点，所选的点保留共振的峰和谷。它们同样仅作比较：INCOGNITA 在 1 keV 以下没有曲线。",
  dx_below_cv: "1 keV 以下：没有 INCOGNITA 曲线，只有评价库和测量值",
  dx_below: "INCOGNITA 自己的曲线从 1 keV 开始；低于 1 keV 只显示比较用的评价库和测量值。",
  dx_pw_tip: "评价库（仅作比较），0 K 逐点值；1 keV 以下没有 INCOGNITA 曲线",
  dx_th: "测量的热中子值（EXFOR）",
  dx_th_sent: "菱形：测量的热中子俘获截面 σγ(0.0253 eV)",
  dx_th_mean: "{n} 个 EXFOR 条目的加权平均",
  dx_th_abs: "吸收减去裂变",
});
