/* Japanese: static page text (index.html data-i18n keys) and kit UI strings */
Object.assign(WT.L.ui, {
  lang_label: "言語", nav_teach: "教員向け",
  nav_topics: "その他の原子力トピック", way4_k: "学ぶ", way4_t: "その他の原子力トピック", way4_p: "本編と並ぶレッスン：放射線と線量、原子炉のしくみ、安定性と制御、核融合。入門から上級まで。", way4_go: "レッスンを選ぶ →", tp_lessons: "レッスン", tp_h1: "その他の原子力トピック",
  tp_kicker: "原子炉 · 放射線 · 核融合", tp_tag: "最初の考え方から研究レベルまで、動かして学ぶレッスン", tp_fire: "連鎖反応を始める", tp_hint: "または燃料棒をクリック",
  tp_cue: "レッスンを選ぶ ↓", tp_cue2: "スクロールして始める ↓", tp_p1_k: "第1部", tp_p1_h: "放射線", tp_p2_k: "第2部", tp_p2_h: "原子炉の内部", tp_p3_k: "第3部", tp_p3_h: "安定性と制御", tp_p4_k: "第4部", tp_p5_k: "第5部", tp_p5_h: "原子炉の種類", tp_p6_k: "第6部", tp_p6_h: "星の中で", tp_hint3: "またはトピックをクリック", tp_w_power: "クリーンな電力", tp_f_power: "世界の電力の約9 %、発電所からのCO₂はゼロ", tp_w_cancer: "がん治療", tp_f_cancer: "多方向からのビームが腫瘍の上で重なる", tp_w_fusion: "核融合エネルギー", tp_f_fusion: "軽い原子核を結合させる、太陽が輝くしくみ", tp_w_space: "ボイジャーの電源", tp_f_space: "プルトニウム238が1977年からVoyager 1と2を動かす", tp_w_pet: "PET検査", tp_f_pet: "背中合わせの2本のガンマ線がトレーサーの居場所を示す", tp_w_stars: "星くず", tp_f_stars: "重い元素の多くは星の中で中性子捕獲によりつくられた", tp_w_water: "きれいな水", tp_f_water: "カザフスタンのBN-350炉は26年間海水を淡水化した", tp_w_crops: "作物を守る", tp_f_crops: "不妊化したハエが北米全域でラセンウジバエを根絶", tp_w_mars: "火星探査車", tp_f_mars: "CuriosityとPerseveranceはプルトニウム238の熱で動く", tp_w_isotopes: "医療用同位体", tp_f_isotopes: "テクネチウム99m：年間約4000万件の検査", tp_w_dating: "炭素年代測定", tp_f_dating: "炭素14はかつて生きていたものの年齢を語る", tp_w_smr: "小型モジュール炉", tp_f_smr: "工場でつくり、運べるほど小さな原子炉", tp_w_recycle: "燃料のリサイクル", tp_f_recycle: "使用済み燃料にはまだ燃やせるウランとプルトニウムがある", tp_w_food: "より安全な食品", tp_f_food: "照射は細菌を殺すが、食品を放射性にはしない", tp_w_ice: "北極の砕氷船", tp_f_ice: "原子力砕氷船が北極海航路を開いておく", tp_w_build: "原子炉をつくる", tp_f_build: "燃料、減速材、大きさを選ぶ：動くだろうか？", tp_w_breed: "燃料の増殖", tp_f_breed: "ウラン238を新しい燃料に変える", tp_w_smoke: "煙感知器", tp_f_smoke: "ひと粒のアメリシウムが何百万もの家を守る",
  tp_coda: "これらのレッスンは、1個の中性子が1個の原子核に入るまでを追う本編<a href=\"./\" data-keep-lang>原子核反応の内側</a>と並ぶものです。特に断りのない限り、図はイメージです。",
  tp_title: "その他の原子力トピック · 原子核反応の内側",
  brand: "原子核反応の内側", nav_physics: "物理", nav_data: "全核種", nav_board: "スコアボード", menu: "メニュー", site_nav: "サイト",
  ways_h: "ほかの入り口", ways_more: "またはこのままスクロール：物理はここから始まります ↓",
  way1_k: "探索", way1_t: "全核種", way1_p: "6168核種の断面積予測を、精査済みの測定値とともに表示します。どの同位体でも検索でき、すべてのデータセットを見られます。", way1_go: "データを開く →",
  way2_k: "比較", way2_t: "スコアボード", way2_p: "エンジンとそのデータ製品が、他の反応コードやライブラリと比べてどうか。測定値に照らして判定し、負けた比較から先に示します。", way2_go: "結果を見る →",
  way3_k: "実行", way3_t: "コード", way3_p: "ここにあるものはすべて公開されています。リポジトリをクローンして、どの曲線でも調べたり、エンジンを自分で実行したりできます。", way3_go: "GitHub →",
  title: "原子核反応の内側",
  kicker: "INCOGNITA反応エンジンを操作しながら学ぶ解説",
  h1: "原子核反応の内側",
  hero1: "原子核に中性子を撃ち込むと、何かが飛び出してきます。跳ね返った中性子そのものかもしれません。陽子かもしれないし、アルファ粒子（陽子2個と中性子2個が固く結びついた塊）かもしれないし、光の閃光かもしれません。重い原子核なら、2つに割れることさえあります。",
  hero2: "そのうちどれが、どれくらいの頻度で起こるのでしょうか。このページでは、私たちのソフトウェアがその問いにどう答えるかを、一歩ずつたどっていきます。下へスクロールしながら、途中の操作部品を試してみてください。図はエンジンと同じ物理に従っていますが、図中の数値は説明用です。",
  scrollcue: "スクロールして始める ↓",
  hero_tag: "原子核物理をビジュアルで探る",
  hero_aud: "学生と原子核物理を学び始めた人、そして彼らを教える教員のためのサイトです。専門家の方へ：すべての核種のデータは<a href=\"data.html\" data-keep-lang>全核種</a>にあります。",
  hero_fire: "中性子を撃つ",
  hero_hint: "または図のどこかをクリック",
  credit_idx: "INCOGNITAエンジンは<a href=\"https://doi.org/10.1140/epja/s10050-023-01034-3\">TALYS-2</a>（A. J. Koning、S. Hilaire、S. Goriely）を移植したもので、TALYSの原子核構造データベースを使っています。INCOGNITAが追加したものは、<a href=\"#code\">このページの最後にスイッチごとに一覧</a>しています。",
  coda_h2: "コードのどこにあるか",
  coda_p1: "ここまでの各段階は<code>physics/hf</code>内のパッケージで、エンジンはそれらを今読んできた順に呼び出します。エンジンは定評ある反応コードTALYS-2.xの移植です。追加した機能は同じパッケージ内の名前つきスイッチの奥にあります。ほとんどは既定でオフで、いくつかの修正はオンになっており、それぞれ個別に元のTALYSの動作へ戻せます。",
  coda_table: `
    <thead><tr><th>章</th><th>内容</th><th>コード</th></tr></thead>
    <tbody>
      <tr><td><a href="#structure">1</a></td><td>質量、準位、変形、共鳴データ</td><td><code>structure/</code></td></tr>
      <tr><td><a href="#omp">5</a></td><td>光学模型、透過係数（粒子の入りやすさと出やすさ）</td><td><code>omp/</code></td></tr>
      <tr><td><a href="#direct">6</a></td><td>チャネル結合、DWBA、巨大共鳴、直接捕獲（任意）</td><td><code>ecis/</code>, <code>direct/</code></td></tr>
      <tr><td><a href="#preeq">7</a></td><td>前平衡：エキシトン模型、ピックアップとノックアウト、多重放出</td><td><code>preeq/</code>, <code>density/particle_hole.py</code></td></tr>
      <tr><td><a href="#compound">8</a></td><td>準位密度（1 MeVあたりの状態数）、スピン分布</td><td><code>density/</code></td></tr>
      <tr><td><a href="#decay">9</a></td><td>出口の選択（ハウザー・フェッシュバッハ）、幅ゆらぎ</td><td><code>compound/</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>光子強度関数とγ線透過、離散準位と核異性体</td><td><code>gamma/</code><br><code>structure/levels.py</code></td></tr>
      <tr><td><a href="#cascade">11</a></td><td>粒子とγ線の放出カスケード、排他的チャネル、残留核</td><td><code>emission/</code></td></tr>
      <tr><td><a href="#fission">12</a></td><td>核分裂障壁と透過</td><td><code>fission/</code></td></tr>
      <tr><td><a href="#measure">17</a></td><td>放出スペクトル、角度分布、二重微分断面積（任意、出力のみ）</td><td><code>specout.py</code><br><code>specang.py</code></td></tr>
      <tr><td><a href="#measure">17</a></td><td>熱的に励起された標的での捕獲と恒星内反応率（任意）</td><td><code>astro/stellar.py</code></td></tr>
      <tr><td><a href="#measure">17</a></td><td>多数のランダムな変種による不確かさ（トータル・モンテカルロ）</td><td><code>tmc.py</code></td></tr>
      <tr><td></td><td>各段階を順に実行するプログラムと、高速化のための任意のC言語計算コア</td><td><code>engine.py</code><br><code>engine_c.py</code>, <code>native/</code></td></tr>
      <tr><td></td><td>すべての既定値とオプション（起動時に1回読み込み）。TENDLの核種別調整パラメータも、TALYSと同じ方法で適用（任意）</td><td><code>input/</code></td></tr>
    </tbody>
  `,
  coda_h3_added: "TALYSへの追加機能",
  coda_p_added: "<b>オン</b>と記した行は既定で動作するため、既定の実行はもはやTALYSと完全には一致しません。それぞれキーワード1つか環境変数1つで元に戻せます。それ以外は設定しないかぎりオフのままです。",
  coda_table_added: `
    <thead><tr><th>章</th><th>変更点</th><th>コード</th></tr></thead>
    <tbody>
      <tr><td><a href="#cascade">11</a></td><td><b>オン。</b>流束の収支を閉じる：残留核を10⁻⁹ mbまで保持（TALYSは10⁻³ mb）、TALYSのカスケード窓の1段先の残留核も保持、排他的チャネルで各放出粒子を最大8個まで、ある準位からの繰り返しの脱励起分岐をすべて計上</td><td><code>emission/fluxclose.py</code><br><code>emission/channels.py</code><br><code>kevleak2.py</code></td></tr>
      <tr><td><a href="#decay">9</a></td><td><b>オン。</b>最初の複合核の最上位ビンを、一様ではなく一次光子による埋まり方（E<sub>γ</sub>³の重み）で埋める</td><td><code>compound/nnleak.py</code></td></tr>
      <tr><td><a href="#decay">9</a></td><td><b>オン。</b>最初の共鳴より下（1 keV未満）では平均化された複合核弾性散乱を含めない。そこでの弾性散乱はポテンシャル散乱</td><td><code>lowepot.py</code></td></tr>
      <tr><td><a href="#decay">9</a></td><td><b>オン。</b>核分裂しない変形標的：結合バンド外の準位への中性子の出口にチャネル結合の透過を使う</td><td><code>compound/ccexitnb.py</code></td></tr>
      <tr><td><a href="#omp">5</a></td><td><b>オン。</b>α粒子放出では残留核の温度に依存するポテンシャルを使い、α粒子の入射はアルファ模型6で扱う。三重陽子とヘリウム3のポテンシャルには入射粒子の大きさを含める</td><td><code>omp/alphatemp.py</code><br><code>alphaentr.py</code><br><code>omp/tfold.py</code></td></tr>
      <tr><td><a href="#fission">12</a></td><td><b>オン。</b>障壁の各こぶを通る厳密な1次元透過</td><td><code>fission/wkb.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td><b>オン。</b>実行時に原子核ごとのE1/M1強度因子が与えられた場合、変形の単一の大域的関数で置き換える</td><td><code>gamma/ftglobal.py</code></td></tr>
      <tr><td><a href="#compound">8</a></td><td><b>オン。</b>自身の測定された共鳴間隔D₀を持たない標的核について、max(E<sub>cut</sub> + 2, S<sub>n</sub> − 6) MeVより上の標的核の連続領域の準位密度を、パリティ・殻・変形の特徴に基づく単一の大域的規則が与える因子で引き上げる。TALYS-2の既定入力に対するしきい値付近の(n,p)の負けを引き分けにするために追加。捕獲、(n,2n)、(n,α)のいくつかの見方をわずかに悪化させるが、その害は受け入れて記録済み</td><td><code>density/npwindow.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>変形核でより強いシザーズモード。オスロの測定に合う新しい系統式を使用（アクチノイドで約4〜5倍）。または、エネルギーと強度を変形に応じてスケールする変種</td><td><code>gamma/scissors.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>各原子核が測定された放射強度⟨Γγ⟩/D₀に一致するよう光子強度関数を再スケール。最初の原子核だけでなく、カスケードのすべての原子核で</td><td><code>gamma/ggnorm.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>最も重い原子核（Z ≥ 88）に限ったより強いシザーズモードと⟨Γγ⟩の規格化。keVエネルギーでの捕獲向け</td><td><code>gamma/actphys.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>TENDLから導かれたTALYSの表の代わりに独自のE1幅定数を使用（配布しているデータなしのレシピで固定）</td><td><code>gamma/e1_width.py</code></td></tr>
      <tr><td><a href="#gamma">10</a></td><td>準連続領域での回転バンドの集団的E2強度</td><td><code>gamma/isoe2.py</code></td></tr>
      <tr><td><a href="#omp">5</a></td><td>変形した希土類標的向けの光学ポテンシャルの井戸の領域的調整。捕獲データを使わず、測定されたS₀とS₁に合わせたもの</td><td><code>omp/regional.py</code></td></tr>
      <tr><td><a href="#omp">5</a></td><td>測定された中性子強度関数S₀、S₁で低エネルギーの中性子透過を固定</td><td><code>omp/sfunc.py</code></td></tr>
      <tr><td><a href="#direct">6</a></td><td>束縛軌道への直接捕獲。元のコードの修正を含む：標準のTALYSでは、光学模型の全出力も要求しないかぎりゼロを返す</td><td><code>direct/racapcalc.py</code></td></tr>
      <tr><td><a href="#direct">6</a></td><td>標的の結合スキーム（回転体、振動体、球形）を測定された準位から選ぶ</td><td><code>structure/collrule.py</code></td></tr>
      <tr><td><a href="#structure">1</a></td><td>連続領域は、測定された準位図が完全でなくなるところから始まる</td><td><code>structure/levcomplete.py</code></td></tr>
      <tr><td><a href="#structure">1</a></td><td>登録されたスピンがその原子核ではありえない（奇数Aで整数）準位は、スピン不明の準位として扱う</td><td><code>structure/levjpar.py</code></td></tr>
      <tr><td><a href="#compound">8</a></td><td>離散準位の完全な部分に固定した定温度模型の準位密度</td><td><code>density/ctwindow2.py</code></td></tr>
      <tr><td><a href="#fission">12</a></td><td>核分裂の鞍点での遷移状態の回転バンド</td><td><code>fission/barriers.py</code></td></tr>
      <tr><td><a href="#resonance">15</a></td><td>恒星の窓に共鳴が数個しか入らない場合の捕獲：平均ではなく共鳴列の典型値を使う</td><td><code>fewres.py</code></td></tr>
      <tr><td></td><td>安定から遠い原子核のための4つの安全策：ユニタリー性で制限した直接流束、フェルミエネルギーの上限、奇奇核では既定で集団性なし、前平衡のスピン分布の規格化</td><td><code>engphys.py</code></td></tr>
    </tbody>
  `,
  coda_h3_outside: "エンジンの外側",
  coda_p_outside: "この物語の一部は、エンジンの内部ではなくその横で動きます。<a href=\"#resonance\">第15章</a>の統計的な共鳴列は<code>physics/resonance/</code>にあります。<a href=\"#measure\">第17章</a>のマクスウェル平均（MACS）は、実行後にエンジンの捕獲曲線を畳み込んで<code>validation/differential/core.py</code>で求めます。一方、熱的に励起された標的での捕獲と恒星内反応率は、エンジン自身が計算します（<code>astro/stellar.py</code>、任意）。<a href=\"#layers\">第21章</a>のデータに固定する層は<code>incognita/terra/</code>にあります。",
  close: "閉じる",
  chapters: "章",
  nav_board: "スコアボード", nav_data_short: "データ",
  coda_repo: "コード、ライブラリ、精査済みの測定値は公開されています：<a href=\"https://github.com/seth-michael-weaver/incognita\">GitHub上のseth-michael-weaver/incognita</a>。<a href=\"data.html\" data-keep-lang>全核種</a>のページでどの予測でも自分で調べられますし、リポジトリをクローンして実行することもできます。",
  diagram: "図",
});

Object.assign(WT.L.ui, { pause_sweep: "掃引を一時停止", play_sweep: "掃引を再開" });

/* course mode: audience note, chapter level tags, per-step links */
Object.assign(WT.L.ui, {
  audience: '<b>対象：</b>好奇心のあるすべての人。最初の章は物理の知識がなくても読めます。後の章は研究レベルまで進みます。各章には<span class="lvl l0">入門</span>、<span class="lvl l1">中級</span>、<span class="lvl l2">上級</span>、<span class="lvl l3">専門</span>のタグがついています。授業で使いたい方は<a href="instructors.html" data-keep-lang>教員向けガイド</a>をご覧ください。',
  lvl0: "入門", lvl1: "中級", lvl2: "上級", lvl3: "専門", lvl_title: "レベル",
  xp_kicker: "第2部 · 専門", xp_h: "細部に分け入る",
  xp_p: "ここまでの章は、各段階を1枚の絵として語ってきました。続く6つの章では、同じ段階の中を開いて見せます。エンジンが計算する式、その中にある近似、そしてそれらが無理をきたすところです。評価者、模型の開発者、大学院生に向けて書いています。図は説明用の入力を使って、式をその場で計算しています。",
  fu_kicker: "第3部 · 核融合", fu_h: "軽い原子核を結合させる",
  fu_p: "4つの章、各レベルに1章ずつ：障壁、プラズマ、磁石、ブランケット。",
  step_link: "このステップへのリンクをコピー", link_copied: "リンクをコピーしました",
});
