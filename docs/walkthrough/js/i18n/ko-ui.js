/* Korean: static page text (index.html data-i18n keys) and kit UI strings */
Object.assign(WT.L.ui, {
  lang_label: "언어", nav_teach: "교수자용",
  brand: "핵반응의 내부", nav_physics: "물리", nav_data: "모든 핵종", nav_board: "점수판", menu: "메뉴", site_nav: "사이트",
  ways_h: "더 많은 입구", ways_more: "아니면 계속 내려가세요. 물리는 여기서 시작합니다 ↓",
  way1_k: "탐색", way1_t: "모든 핵종", way1_p: "6,168개 핵종에 대한 예측 단면적을 정리된 모든 측정값과 나란히 보여 줍니다. 어떤 동위원소든 검색하고 모든 데이터 세트를 살펴보세요.", way1_go: "데이터 열기 →",
  way2_k: "비교", way2_t: "점수판", way2_p: "엔진과 그 데이터 결과물이 다른 핵반응 코드 및 라이브러리와 비교하여 어떤지, 측정값을 기준으로 평가하고 진 경우부터 보여 줍니다.", way2_go: "점수 보기 →",
  way3_k: "실행", way3_t: "코드", way3_p: "여기 있는 모든 것은 공개되어 있습니다. 저장소를 복제하고, 어떤 곡선이든 찾아보거나, 엔진을 직접 실행해 보세요.", way3_go: "GitHub →",
  title: "핵반응의 내부",
  kicker: "INCOGNITA 핵반응 엔진을 직접 탐색하며 배우는 해설",
  h1: "핵반응의 내부",
  hero1: "원자핵에 중성자를 쏘면 무언가가 다시 튀어나옵니다. 튕겨 나온 중성자 자신일 수도 있습니다. 양성자일 수도, 알파 입자(양성자 2개와 중성자 2개가 단단히 뭉친 덩어리)일 수도, 빛의 섬광일 수도 있습니다. 무거운 원자핵은 아예 둘로 쪼개질 수도 있습니다.",
  hero2: "이 가운데 어떤 일이, 얼마나 자주 일어날까요? 이 페이지는 우리 소프트웨어가 그 질문에 어떻게 답하는지 한 단계씩 따라갑니다. 아래로 스크롤하면서 도중에 나오는 조작 도구를 직접 움직여 보세요. 그림은 엔진과 같은 물리를 따르지만, 그림 속 숫자는 예시입니다.",
  scrollcue: "스크롤하여 시작 ↓",
  hero_tag: "중성자 하나. 원자핵 하나. 끝나는 방법은 여러 가지.",
  hero_aud: "학생과 핵물리학을 처음 접하는 모든 사람, 그리고 그들을 가르치는 교수자를 위한 사이트입니다. 전문가께: 모든 핵종의 데이터는 <a href=\"data.html\" data-keep-lang>모든 핵종</a>에 있습니다.",
  hero_fire: "중성자 발사",
  hero_hint: "또는 그림의 아무 곳이나 클릭",
  credit_idx: "INCOGNITA 엔진은 <a href=\"https://doi.org/10.1140/epja/s10050-023-01034-3\">TALYS-2</a>(A. J. Koning, S. Hilaire, S. Goriely)를 이식한 것으로, TALYS 핵구조 데이터베이스를 사용합니다. INCOGNITA가 더한 것은 <a href=\"#code\">이 페이지 끝에 스위치별로 정리되어 있습니다</a>.",
  coda_h2: "코드에서 이것이 있는 곳",
  coda_p1: "위의 각 단계는 <code>physics/hf</code> 안의 패키지 하나이며, 엔진은 방금 읽은 순서대로 이들을 호출합니다. 엔진은 검증된 핵반응 코드인 TALYS-2.x를 이식한 것입니다. 추가된 기능은 같은 패키지 안에서 이름 붙은 스위치 뒤에 있습니다. 대부분은 기본값이 꺼져 있고, 몇몇 보정은 켜져 있으며, 각각을 따로 원래의 TALYS로 되돌릴 수 있습니다.",
  coda_table: `
    <thead><tr><th>장</th><th>하는 일</th><th>코드</th></tr></thead>
    <tbody>
      <tr><td><a href="#structure">1</a></td><td>질량, 준위, 변형, 공명 데이터</td><td><code>structure/</code></td></tr>
      <tr><td><a href="#omp">2</a></td><td>광학 모형, 투과 계수 (입자가 얼마나 쉽게 들어오고 나가는지)</td><td><code>omp/</code></td></tr>
      <tr><td><a href="#direct">3</a></td><td>결합 채널, DWBA, 거대 공명, 직접 포획 (선택 사항)</td><td><code>ecis/</code>, <code>direct/</code></td></tr>
      <tr><td><a href="#preeq">4</a></td><td>전평형: 엑시톤 모형, 픽업과 녹아웃, 다중 방출</td><td><code>preeq/</code>, <code>density/particle_hole.py</code></td></tr>
      <tr><td><a href="#compound">5</a></td><td>준위 밀도 (MeV당 상태 수), 스핀 분포</td><td><code>density/</code></td></tr>
      <tr><td><a href="#decay">6</a></td><td>출구 고르기 (하우저–페시바흐), 폭 요동</td><td><code>compound/</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>감마 세기 함수와 γ 투과, 불연속 준위와 핵이성질체</td><td><code>gamma/</code><br><code>structure/levels.py</code></td></tr>
      <tr><td><a href="#cascade">8</a></td><td>입자와 γ 방출의 캐스케이드, 배타적 채널, 잔류핵</td><td><code>emission/</code></td></tr>
      <tr><td><a href="#fission">9</a></td><td>핵분열 장벽과 투과</td><td><code>fission/</code></td></tr>
      <tr><td><a href="#measure">11</a></td><td>방출 스펙트럼, 각분포, 이중 미분 단면적 (선택 사항, 출력 전용)</td><td><code>specout.py</code><br><code>specang.py</code></td></tr>
      <tr><td><a href="#measure">11</a></td><td>열적으로 들뜬 표적에서의 포획과 항성 반응률 (선택 사항)</td><td><code>astro/stellar.py</code></td></tr>
      <tr><td><a href="#measure">11</a></td><td>여러 무작위 변종에 의한 불확도 (전체 몬테카를로)</td><td><code>tmc.py</code></td></tr>
      <tr><td></td><td>단계들을 순서대로 실행하는 구동기, 그리고 속도를 위한 선택적 C 커널</td><td><code>engine.py</code><br><code>engine_c.py</code>, <code>native/</code></td></tr>
      <tr><td></td><td>시작할 때 한 번 읽는 모든 기본값과 옵션, 그리고 TALYS와 같은 방식으로 적용하는 TENDL의 핵종별 조정 매개변수 (선택 사항)</td><td><code>input/</code></td></tr>
    </tbody>
  `,
  coda_h3_added: "TALYS를 넘어 추가된 것",
  coda_p_added: "<b>켜짐</b>으로 표시된 행은 기본으로 실행되므로, 기본 실행 결과는 더 이상 TALYS와 정확히 일치하지 않습니다. 각각은 키워드 하나나 환경 변수 하나로 되돌릴 수 있습니다. 나머지는 설정하지 않는 한 꺼져 있습니다.",
  coda_table_added: `
    <thead><tr><th>장</th><th>바뀌는 것</th><th>코드</th></tr></thead>
    <tbody>
      <tr><td><a href="#cascade">8</a></td><td><b>켜짐.</b> 선속 장부를 닫음: 잔류핵을 10⁻⁹ mb까지 유지(TALYS: 10⁻³ mb), TALYS 캐스케이드 창보다 한 단계 더 나아간 잔류핵 유지, 배타적 채널에서 방출 입자 종류별로 최대 8개, 한 준위의 반복되는 붕괴 갈래를 모두 셈</td><td><code>emission/fluxclose.py</code><br><code>emission/channels.py</code><br><code>kevleak2.py</code></td></tr>
      <tr><td><a href="#decay">6</a></td><td><b>켜짐.</b> 첫 번째 복합핵의 맨 위 구간을 고르게 채우지 않고, 1차 광자가 채우는 방식대로(E<sub>γ</sub>³ 가중치로) 채움</td><td><code>compound/nnleak.py</code></td></tr>
      <tr><td><a href="#decay">6</a></td><td><b>켜짐.</b> 첫 공명들보다 아래(1 keV 미만)에서는 평균 복합핵 탄성 산란을 넣지 않음. 그곳의 탄성 산란은 퍼텐셜 산란임</td><td><code>lowepot.py</code></td></tr>
      <tr><td><a href="#decay">6</a></td><td><b>켜짐.</b> 핵분열하지 않는 변형 표적: 결합된 띠 밖의 준위로 가는 중성자 출구에 결합 채널 투과를 사용</td><td><code>compound/ccexitnb.py</code></td></tr>
      <tr><td><a href="#omp">2</a></td><td><b>켜짐.</b> 알파 방출은 잔류핵의 온도에 의존하는 퍼텐셜을 봄. 입사 알파는 알파 모형 6으로 들어옴. 삼중양성자와 헬륨-3 퍼텐셜에 입사 입자의 크기를 포함</td><td><code>omp/alphatemp.py</code><br><code>alphaentr.py</code><br><code>omp/tfold.py</code></td></tr>
      <tr><td><a href="#fission">9</a></td><td><b>켜짐.</b> 장벽의 각 봉우리를 지나는 정확한 1차원 투과</td><td><code>fission/wkb.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td><b>켜짐.</b> 실행에서 원자핵별 E1/M1 세기 인자를 주는 경우, 이를 변형에 대한 하나의 전역 함수로 대체</td><td><code>gamma/ftglobal.py</code></td></tr>
      <tr><td><a href="#compound">5</a></td><td><b>켜짐.</b> 자체 측정된 공명 간격 D₀가 없는 표적: max(E<sub>cut</sub> + 2, S<sub>n</sub> − 6) MeV 위에서 표적의 연속 영역 준위 밀도를, 홀짝성·껍질·변형 특징에 기반한 하나의 전역 규칙이 주는 인자만큼 높입니다. TALYS-2 기본 입력에 대한 문턱 근처 (n,p)의 패배를 무승부로 바꾸려고 추가했으며, 포획·(n,2n)·(n,α)의 몇몇 관점을 조금 나쁘게 만드는 손해는 받아들이고 기록해 두었습니다</td><td><code>density/npwindow.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>오슬로 측정에 맞는 새 계통성에 따른, 변형된 원자핵의 더 강한 가위 모드(악티늄족에서 약 4–5배). 또는 그 에너지와 세기를 변형에 따라 조정하는 변종</td><td><code>gamma/scissors.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>첫 번째 원자핵만이 아니라 캐스케이드의 모든 원자핵이 측정된 복사 세기 ⟨Γγ⟩/D₀와 일치하도록 감마 세기 함수를 재조정</td><td><code>gamma/ggnorm.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>가장 무거운 원자핵(Z ≥ 88)에만 적용하는 더 강한 가위 모드와 ⟨Γγ⟩ 규격화. keV 에너지에서의 포획이 목표</td><td><code>gamma/actphys.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>TENDL에서 유도한 TALYS의 표 대신 자체 E1 폭 상수 사용(함께 배포하는 무데이터 레시피가 이를 설정)</td><td><code>gamma/e1_width.py</code></td></tr>
      <tr><td><a href="#gamma">7</a></td><td>준연속 영역에서 회전 띠의 집단 E2 세기</td><td><code>gamma/isoe2.py</code></td></tr>
      <tr><td><a href="#omp">2</a></td><td>변형된 희토류 표적에 대한 광학 우물의 지역적 조정. 포획 데이터 없이 측정된 S₀와 S₁에 맞춤</td><td><code>omp/regional.py</code></td></tr>
      <tr><td><a href="#omp">2</a></td><td>측정된 중성자 세기 함수 S₀, S₁이 저에너지 중성자 투과를 정함</td><td><code>omp/sfunc.py</code></td></tr>
      <tr><td><a href="#direct">3</a></td><td>속박 궤도로의 직접 포획, 원본에 대한 수정 포함: 기본 TALYS에서는 광학 모형 출력을 모두 함께 요청하지 않으면 0을 반환함</td><td><code>direct/racapcalc.py</code></td></tr>
      <tr><td><a href="#direct">3</a></td><td>표적의 결합 방식(회전체, 진동체, 구형)을 측정된 준위로부터 선택</td><td><code>structure/collrule.py</code></td></tr>
      <tr><td><a href="#structure">1</a></td><td>측정된 준위 도식이 더 이상 완전하지 않은 곳에서 연속 영역이 시작</td><td><code>structure/levcomplete.py</code></td></tr>
      <tr><td><a href="#structure">1</a></td><td>목록의 스핀이 그 원자핵에 불가능한(홀수 A인데 정수인) 준위를 스핀을 모르는 준위로 취급</td><td><code>structure/levjpar.py</code></td></tr>
      <tr><td><a href="#compound">5</a></td><td>불연속 준위 중 완전한 부분에 고정한 일정 온도 준위 밀도</td><td><code>density/ctwindow2.py</code></td></tr>
      <tr><td><a href="#fission">9</a></td><td>핵분열 안장점에서 전이 상태의 회전 띠</td><td><code>fission/barriers.py</code></td></tr>
      <tr><td><a href="#resonance">10</a></td><td>항성 창에 공명이 몇 개만 들어오는 경우의 포획: 평균 대신 공명 사다리 하나의 전형적인 값</td><td><code>fewres.py</code></td></tr>
      <tr><td></td><td>안정성에서 먼 곳을 위한 네 가지 안전장치: 유니터리성으로 제한한 직접 선속, 페르미 에너지의 한계, 홀수–홀수 원자핵에는 기본 집단성 없음, 전평형 스핀 분포의 규격화</td><td><code>engphys.py</code></td></tr>
    </tbody>
  `,
  coda_h3_outside: "엔진 바깥",
  coda_p_outside: "이야기의 일부는 엔진 안이 아니라 그 옆에서 실행됩니다. <a href=\"#resonance\">10장</a>의 통계적 공명 사다리는 <code>physics/resonance/</code>에 있습니다. <a href=\"#measure\">11장</a>의 맥스웰 평균(MACS)은 실행이 끝난 뒤 <code>validation/differential/core.py</code>에서 엔진의 포획 곡선을 접어 얻습니다. 반면 열적으로 들뜬 표적에서의 포획과 항성 반응률은 엔진 자체가 계산합니다(<code>astro/stellar.py</code>, 선택 사항). <a href=\"#layers\">12장</a>의 고정 층은 <code>incognita/terra/</code>에 있습니다.",
  close: "닫기",
  chapters: "장",
  nav_board: "점수판", nav_data_short: "데이터",
  coda_repo: "코드, 라이브러리, 정리된 측정값은 공개되어 있습니다: <a href=\"https://github.com/seth-michael-weaver/incognita\">GitHub의 seth-michael-weaver/incognita</a>. <a href=\"data.html?lang=ko\" data-keep-lang>모든 핵종</a> 페이지에서 어떤 예측이든 직접 찾아보거나, 저장소를 복제해 실행해 볼 수 있습니다.",
  diagram: "도식",
});

Object.assign(WT.L.ui, { pause_sweep: "훑기 일시정지", play_sweep: "훑기 재생" });

/* course mode: audience note, chapter level tags, per-step links */
Object.assign(WT.L.ui, {
  audience: '<b>대상:</b> 호기심 있는 누구나. 앞의 장들은 물리 지식이 필요 없고, 뒤의 장들은 연구 수준까지 다룹니다. 각 장에는 <span class="lvl l0">입문</span>, <span class="lvl l1">중급</span>, <span class="lvl l2">고급</span>, <span class="lvl l3">전문가</span> 가운데 하나의 꼬리표가 붙어 있습니다. 수업에 쓰시려면 <a href="instructors.html" data-keep-lang>교수자용 안내서</a>를 보세요.',
  lvl0: "입문", lvl1: "중급", lvl2: "고급", lvl3: "전문가", lvl_title: "수준",
  step_link: "이 단계로 가는 링크 복사", link_copied: "링크 복사됨",
  xp_kicker: "2부 · 전문가",
  xp_h: "깊숙이 들어가기",
  xp_p: "지금까지의 장들은 각 단계를 그림으로 이야기했습니다. 이어지는 여섯 장은 같은 단계들을 열어 봅니다. 엔진이 계산하는 공식, 그 안에 든 근사, 그리고 그 근사가 한계에 부딪히는 곳입니다. 평가자, 모형 개발자, 대학원생을 위해 썼습니다. 그림은 예시용 입력으로 공식을 실시간으로 계산합니다.",
});
