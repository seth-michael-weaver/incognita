/* Where the elements come from: heavy elements made by neutron capture in stars (the s- and r-process).
 * Scenes (S.mode): "curve" (solar abundances, A = 1-209), "s" (chart of nuclides, the s-process path), "r" (the same chart, an
 * r-process path far from stability decaying back), "peaks" (abundances A = 56-209 with the magic-number peaks),
 * "sigN" (sigma x N for the s-only isotopes), "check" (INCOGNITA's 30 keV MACS against measured values).
 *
 * Numbers and where they come from:
 *  - Weak s-process (massive stars) adding to the A < 90 s-only isotopes: Kaeppeler et al. 2011 (below).
 *  - Solar-system abundances, AB (per mass number A, summed over isobars; atoms per 10^6 Si) and the per-nuclide values in ST:
 *    K. Lodders, H. Palme, H.-P. Gail, "Abundances of the elements in the Solar System", Landolt-Boernstein New Series VI/4B
 *    (Springer 2009) 712-770, arXiv:0901.1149, Table 10 "Nuclide abundances 4.56 Ga ago (normalized to N(Si) = 10^6 atoms)",
 *    rounded to 3 significant digits. The third number in AB is the Z of the most abundant isobar at that A.
 *  - MACS at kT = 30 keV (sigma, mb) and its 68 % factor in ST: INCOGNITA library v0.2.3 (library/v0.2.3/macs30_v023.csv in the
 *    repository): the production engine engine-20261022-3, a blind prediction (no nucleus's own capture data fitted; global
 *    parameters set on data from many nuclei, these included). Tier letter: M = the nucleus has capture data, A = ANCHORED
 *    (no capture data; the curve is scaled to a measured 30 keV MACS, so that value is not a prediction), I/E = unmeasured.
 *  - err in ST: log10(INCOGNITA MACS / compiled measured MACS) at 30 keV, from docs/walkthrough/data/board/k_pernuc.csv
 *    (err_ours, nuclides with in_scope = True, i.e. the compiled value is a measurement). The compiled values (KADoNiS) are
 *    not redistributed by the project, so only the ratio is shown. A development comparison, not a blind test (see the
 *    scoreboard's README).
 *  - Magic numbers N = 50, 82, 126; s-process abundance peaks at Sr-88 (A 88), Ba-138 (A 138), Pb-208 (A 208); r-process
 *    peaks near A 80, 130, 195 (both visible as local maxima in Lodders' table). sigma x N roughly constant between magic
 *    numbers ("local approximation"): F. Kaeppeler, R. Gallino, S. Bisterzo, W. Aoki, Rev. Mod. Phys. 83 (2011) 157;
 *    E. M. Burbidge, G. R. Burbidge, W. A. Fowler, F. Hoyle, Rev. Mod. Phys. 29 (1957) 547 (B2FH).
 *  - s-only isotopes (shielded from r-process decay by a stable isobar): the standard list as in Kaeppeler et al. 2011.
 *  - The s-path is computed here from the stable nuclides in the table: capture n while the next isotope is stable, beta-decay
 *    otherwise (a proton-rich unstable one, like Zn-65, is taken to capture first); branchings left out. It ends in the Pb-Bi cycle (Bi-209 -> Bi-210 -> Po-210 -> alpha -> Pb-206).
 *  - The r-process path is a sketch (marked "illustration"): neutron-rich nuclei with waiting points at N = 50 (Z ~ 28-30),
 *    N = 82 (Z ~ 46-48) and N = 126 (Z ~ 66-70); each decays by beta decay along its isobar (A fixed) to the most
 *    neutron-rich stable isobar. The 2017 neutron-star merger GW170817 and its kilonova (AT2017gfo) showed r-process
 *    nucleosynthesis in a merger (e.g. Kasen et al., Nature 551 (2017) 80). */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const log10 = (x) => Math.log(x) / Math.LN10;
  const SYM = ("n H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr " +
    "Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po").split(" ");
  const AB = "1,2.59e+10,1;2,503000,1;3,1.03e+06,2;4,2.51e+09,2;6,4.2,3;7,51.4,3;9,0.612,4;10,3.7,5;11,15.1,5;12,7.11e+06,6;13,79900,6;14,2.12e+06,7;15,7780,7;16,1.57e+07,8;17,5900,8;18,31500,8;19,804,9;20,3.06e+06,10;21,7330,10;22,225000,10;23,57700,11;24,810000,12;25,103000,12;26,113000,12;27,84600,13;28,922000,14;29,46800,14;30,30900,14;31,8300,15;32,400000,16;33,3160,16;34,17800,16;35,3920,17;36,78500,18;37,1250,17;38,14300,18;39,3500,19;40,58500,20;41,253,19;42,391,20;43,82,20;44,1260,20;45,34.4,21;46,206,22;47,184,22;48,1930,22;49,134,22;50,698,24;51,286,23;52,11000,24;53,1240,24;54,49900,26;55,9220,25;56,778000,26;57,18000,26;58,35800,28;59,2350,27;60,12900,28;61,559,28;62,1780,28;63,374,29;64,1080,30;65,167,29;66,362,30;67,53,30;68,243,30;69,22,31;70,32.3,32;71,14.6,31;72,31.7,32;73,8.8,32;74,41.8,32;75,6.1,33;76,14.8,32;77,5.15,34;78,16.2,34;79,5.43,35;80,34.8,34;81,5.28,35;82,12.4,36;83,6.45,36;84,31.9,36;85,5.12,37;86,11.9,36;87,3.71,37;88,19.2,38;89,4.63,39;90,5.55,40;91,1.21,40;92,2.22,40;93,0.78,41;94,2.11,40;95,0.404,42;96,0.826,42;97,0.245,42;98,0.655,42;99,0.227,44;100,0.474,42;101,0.304,44;102,0.576,44;103,0.37,45;104,0.483,44;105,0.303,46;106,0.391,46;107,0.254,47;108,0.373,46;109,0.236,47;110,0.356,48;111,0.201,48;112,0.415,48;113,0.2,48;114,0.476,48;115,0.182,49;116,0.642,50;117,0.277,50;118,0.873,50;119,0.309,50;120,1.18,50;121,0.179,51;122,0.289,50;123,0.177,51;124,0.442,52;125,0.335,52;126,0.895,52;127,1.1,53;128,1.61,52;129,1.5,54;130,1.83,52;131,1.19,54;132,1.44,54;133,0.371,55;134,0.635,54;135,0.295,56;136,0.782,54;137,0.502,56;138,3.21,56;139,0.457,57;140,1.04,58;141,0.172,59;142,0.362,60;143,0.103,60;144,0.211,60;145,0.075,60;146,0.147,60;147,0.041,62;148,0.079,60;149,0.037,62;150,0.068,60;151,0.0471,63;152,0.0717,62;153,0.0514,63;154,0.0678,62;155,0.0533,64;156,0.0738,64;157,0.0563,64;158,0.0898,64;159,0.0634,65;160,0.0881,64;161,0.0762,66;162,0.103,66;163,0.101,66;164,0.118,66;165,0.091,67;166,0.088,68;167,0.06,68;168,0.0713,68;169,0.0406,69;170,0.0466,68;171,0.0361,70;172,0.0556,70;173,0.0413,70;174,0.0824,70;175,0.037,71;176,0.0425,70;177,0.029,72;178,0.0425,72;179,0.0212,72;180,0.0549,72;181,0.021,73;182,0.0363,74;183,0.0196,74;184,0.0421,74;185,0.0207,75;186,0.0498,74;187,0.046,75;188,0.0904,76;189,0.11,76;190,0.179,76;191,0.25,77;192,0.288,76;193,0.421,77;194,0.42,78;195,0.431,78;196,0.323,78;197,0.195,79;198,0.137,78;199,0.077,80;200,0.106,80;201,0.06,80;202,0.137,80;203,0.054,81;204,0.097,82;205,0.129,81;206,0.614,82;207,0.68,82;208,1.95,82;209,0.138,83".split(";").map((s) => s.split(",").map(Number)); // [A, atoms per 1e6 Si, Z of main isobar]
  const ST = "26,54,49600,51,1.52,M,0.238;26,56,778000,33.1,1.52,M,;26,57,18000,43.5,1.52,M,0.04;26,58,2390,23.2,1.52,M,;27,59,2350,53.7,1.52,M,;28,58,33400,65.4,1.52,M,;28,60,12900,39.5,1.52,M,;28,61,559,103,1.52,M,0.102;28,62,1780,23.2,1.52,M,0.02;28,64,454,11.2,1.52,M,;29,63,374,112,1.52,M,;29,65,167,56.8,1.52,M,;30,64,630,70.5,1.52,M,;30,66,362,52.2,1.52,M,0.175;30,67,53,176,1.52,M,0.063;30,68,243,27.8,1.52,M,;30,70,8,9.34,1.52,A,-0.328;31,69,22,190,1.52,M,;31,71,14.6,138,1.52,M,;32,70,24.3,121,1.52,M,0.14;32,72,31.7,95.3,1.52,M,0.118;32,73,8.8,308,1.52,M,0.106;32,74,41.2,65.5,1.52,M,;32,76,8.5,21.5,1.52,A,0.176;33,75,6.1,382,1.52,M,;34,74,0.6,278,1.52,M,;34,76,6.32,164,1.52,A,0.014;34,77,5.15,492,1.52,M,0.073;34,78,16,96,1.52,M,0.206;34,80,33.5,30.7,1.52,M,;34,82,5.89,16.5,1.52,M,;35,79,5.43,566,1.52,M,;35,81,5.28,237,1.52,M,;36,78,0.2,368,1.52,M,;36,80,1.3,208,1.52,M,;36,82,6.51,80.2,1.52,M,;36,83,6.45,221,1.52,M,;36,84,31.8,38,1.52,M,;36,86,9.61,6.96,1.52,M,0.315;37,85,5.12,293,1.52,M,;37,87,2.11,26.3,1.52,M,;38,84,0.13,205,1.52,M,;38,86,2.3,76.3,1.52,M,;38,87,1.6,136,1.52,M,;38,88,19.2,9.93,1.52,M,;39,89,4.63,35.1,1.52,M,;40,90,5.55,27.1,1.28,M,0.151;40,91,1.21,84.8,1.23,M,;40,92,1.85,42,1.3,M,;40,94,1.87,29.7,1.35,M,;40,96,0.302,10.6,1.32,M,0;41,93,0.78,239,1.23,M,;42,92,0.37,70.8,1.34,M,;42,94,0.233,110,1.3,M,;42,95,0.404,300,1.23,M,;42,96,0.425,130,1.23,M,;42,97,0.245,298,1.23,M,;42,98,0.622,77.5,1.26,M,;42,100,0.25,98,1.29,M,;44,96,0.099,161,1.29,M,;44,98,0.033,193,1.45,I,;44,99,0.227,665,1.25,I,;44,100,0.224,227,1.25,M,;44,101,0.304,707,1.23,M,;44,102,0.562,216,1.25,M,;44,104,0.332,201,1.28,M,;45,103,0.37,783,1.23,M,;46,102,0.0139,369,1.23,A,-0.127;46,104,0.151,289,1.23,M,;46,105,0.303,995,1.23,M,;46,106,0.371,222,1.24,M,;46,108,0.359,259,1.26,M,;46,110,0.159,137,1.34,M,;47,107,0.254,759,1.23,M,;47,109,0.236,671,1.23,M,;48,106,0.02,342,1.37,M,;48,108,0.014,269,1.28,M,;48,110,0.197,250,1.23,M,;48,111,0.201,657,1.23,M,;48,112,0.38,229,1.24,M,;48,113,0.192,500,1.23,M,;48,114,0.452,120,1.24,M,;48,116,0.118,77.5,1.37,M,;49,113,0.008,620,1.32,I,;49,115,0.17,577,1.23,M,;50,112,0.035,200,1.27,M,;50,114,0.024,142,1.24,M,;50,115,0.012,363,1.23,M,;50,116,0.524,101,1.24,M,;50,117,0.277,339,1.23,M,;50,118,0.873,65.9,1.23,M,;50,119,0.309,203,1.23,M,;50,120,1.18,49.8,1.27,M,;50,122,0.167,35.2,1.28,M,;50,124,0.209,20.4,1.38,M,;51,121,0.179,545,1.23,M,;51,123,0.134,374,1.24,M,;52,120,0.005,519,1.23,A,-0.093;52,122,0.122,265,1.23,M,;52,123,0.043,609,1.23,M,;52,124,0.226,140,1.23,M,;52,125,0.335,340,1.23,M,;52,126,0.889,84.4,1.27,M,;52,128,1.49,54.1,1.29,M,;52,130,1.58,29.8,1.32,M,;53,127,1.1,699,1.23,M,;54,124,0.007,578,1.25,M,-0.073;54,126,0.006,359,1.23,A,-0.008;54,128,0.122,296,1.31,M,;54,129,1.5,602,1.24,M,;54,130,0.239,128,1.25,M,;54,131,1.19,354,1.27,I,;54,132,1.44,53.6,1.27,M,;54,134,0.527,29.8,1.45,M,;54,136,0.429,1.99,1.32,M,0.314;55,133,0.371,566,1.23,M,;56,130,0.005,450,1.37,M,;56,132,0.005,397,1.23,A,-0.247;56,134,0.108,143,1.25,M,;56,135,0.295,392,1.23,M,;56,136,0.351,68.3,1.27,M,;56,137,0.502,83.5,1.23,M,;56,138,3.21,4.99,1.25,M,;57,138,0,423,1.42,I,;57,139,0.457,48.5,1.23,M,0.176;58,136,0.002,300,1.23,A,-0.011;58,138,0.003,179,1.23,A,0.05;58,140,1.04,13.6,1.27,M,0.094;58,142,0.131,20.3,1.37,M,-0.165;59,141,0.172,109,1.23,M,-0.007;60,142,0.231,41.7,1.32,M,0.077;60,143,0.103,224,1.23,M,-0.038;60,144,0.203,62.7,1.24,M,-0.113;60,145,0.075,405,1.23,M,-0.02;60,146,0.147,90.5,1.29,M,-0.003;60,148,0.049,137,1.23,M,-0.029;60,150,0.048,170,1.38,M,0.028;62,144,0.008,94.1,1.29,M,0.01;62,147,0.041,851,1.23,M,-0.058;62,148,0.03,254,1.23,M,0.023;62,149,0.037,1710,1.23,M,-0.026;62,150,0.02,440,1.32,M,0.018;62,152,0.071,509,1.32,M,0.032;62,154,0.06,239,1.32,M,0.065;63,151,0.0471,2060,1.32,M,-0.227;63,153,0.0514,1990,1.32,M,-0.107;64,152,0.0007,908,1.32,M,-0.062;64,154,0.0078,1030,1.32,M,0.002;64,155,0.0533,1640,1.32,M,-0.207;64,156,0.0736,597,1.32,M,-0.012;64,157,0.0563,1150,1.32,M,-0.076;64,158,0.0894,272,1.32,M,-0.075;64,160,0.0787,146,1.32,M,-0.023;65,159,0.0634,1460,1.32,M,-0.033;66,156,0.0002,1630,1.38,M,-0.021;66,158,0.0004,968,1.37,I,;66,160,0.0094,871,1.32,M,-0.009;66,161,0.0762,1570,1.32,M,-0.095;66,162,0.103,467,1.32,M,0.021;66,163,0.101,1010,1.32,M,-0.042;66,164,0.114,244,1.32,M,0.062;67,165,0.091,1260,1.32,M,-0.007;68,162,0.0004,1610,1.32,M,-0.004;68,164,0.0042,1190,1.32,M,0.014;68,166,0.088,615,1.32,M,0.039;68,167,0.06,1330,1.32,M,-0.03;68,168,0.071,305,1.32,M,-0.045;68,170,0.039,215,1.32,M,0.076;69,169,0.0406,762,1.32,M,-0.17;70,168,0.0003,1330,1.32,M,0.014;70,170,0.0076,689,1.32,M,-0.046;70,171,0.0361,1330,1.32,M,0.042;70,172,0.0556,395,1.32,M,0.064;70,173,0.0413,755,1.32,M,0.001;70,174,0.0821,201,1.32,M,0.125;70,176,0.0333,172,1.32,M,0.172;71,175,0.037,1240,1.32,M,0.007;71,176,0.0011,2090,1.33,M,0.106;72,174,0.0003,983,1.32,A,-0.082;72,176,0.0081,470,1.32,M,-0.124;72,177,0.029,1310,1.32,M,-0.072;72,178,0.0425,314,1.32,M,-0.007;72,179,0.0212,970,1.32,M,0.023;72,180,0.0547,181,1.33,M,0.063;73,180,2.6e-06,2230,1.37,I,;73,181,0.021,862,1.32,M,0.052;74,180,0.0002,572,1.32,M,-0.089;74,182,0.0363,345,1.32,M,0.1;74,183,0.0196,538,1.32,M,0.02;74,184,0.042,266,1.34,M,;74,186,0.039,246,1.32,M,;75,185,0.0207,1450,1.32,M,;75,187,0.0374,1240,1.32,M,;76,184,0.0001,590,1.32,A,0.187;76,186,0.0108,641,1.32,M,;76,187,0.0086,976,1.32,M,;76,188,0.0904,618,1.32,M,;76,189,0.11,954,1.32,M,;76,190,0.179,408,1.32,M,;76,192,0.278,219,1.38,M,;77,191,0.25,1180,1.32,M,;77,193,0.421,763,1.32,M,;78,190,0.0002,508,1.32,A,0.043;78,192,0.01,459,1.32,M,-0.109;78,194,0.42,327,1.32,M,;78,195,0.431,536,1.32,M,-0.204;78,196,0.322,184,1.32,M,;78,198,0.091,89.6,1.35,M,;79,197,0.195,629,1.32,M,;80,196,0.001,204,1.32,A,0.171;80,198,0.046,241,1.32,M,;80,199,0.077,306,1.32,M,;80,200,0.106,92.1,1.32,M,;80,201,0.06,202,1.32,M,;80,202,0.137,57.4,1.32,M,;80,204,0.031,18.6,1.32,M,;81,203,0.054,176,1.32,M,;81,205,0.129,66.8,1.32,M,;82,204,0.066,84.7,1.32,M,;82,206,0.614,29.6,1.32,M,0.309;82,207,0.68,15.9,1.32,M,0.206;82,208,1.95,0.418,1.32,M,;83,209,0.138,8.72,1.32,M,0.533".split(";").map((s) => { const v = s.split(","); return { Z: +v[0], A: +v[1], N: +v[1] - +v[0], ab: +v[2], m: v[3] === "" ? null : +v[3], u: +v[4], tier: v[5], err: v[6] === "" ? null : +v[6] }; });
  const key = (Z, A) => Z * 1000 + A, STAB = new Map(ST.map((s) => [key(s.Z, s.A), s]));
  const nm = (Z, A) => `${SYM[Z]}-${A}`;
  const SONLY = [[32, 70], [34, 76], [36, 80], [36, 82], [38, 86], [38, 87], [42, 96], [44, 100], [46, 104], [48, 110], [50, 116], [52, 122], [52, 123], [52, 124], [54, 128], [54, 130], [56, 134], [56, 136], [60, 142], [62, 148], [62, 150], [64, 154], [66, 160], [70, 170], [71, 176], [72, 176], [76, 186], [76, 187], [78, 192], [80, 198], [82, 204]].map(([Z, A]) => STAB.get(key(Z, A)));
  SONLY.forEach((s) => (s.sonly = true));
  const CHK = ST.filter((s) => s.err != null);
  const RMS = Math.sqrt(CHK.reduce((a, s) => a + s.err * s.err, 0) / CHK.length);
  const MED = CHK.map((s) => Math.abs(s.err)).sort((a, b) => a - b)[CHK.length >> 1];

  // ---- the s-path: capture while the next isotope is stable, else beta decay ----
  const PATH = []; // {Z, A, k: "start" | "c" (capture) | "b" (beta) | "a" (alpha), st: stable?}
  { let Z = 26, A = 56; PATH.push({ Z, A, k: "start", st: true });
    for (let guard = 0; guard < 600; guard++) {
      A++; PATH.push({ Z, A, k: "c", st: STAB.has(key(Z, A)) });
      if (Z === 83 && A === 210) { PATH.push({ Z: 84, A, k: "b", st: false }); PATH.push({ Z: 82, A: 206, k: "a", st: true }); break; } // Bi-210 -> Po-210 -> alpha -> Pb-206: the cycle closes
      if (STAB.has(key(Z, A))) continue;
      // unstable: beta-decay towards a stable isobar of higher Z; on the proton-rich side (no such isobar) it captures again first
      let zs = Z + 1; while (zs <= 83 && !STAB.has(key(zs, A))) zs++;
      if (zs > 83) continue;
      while (Z < zs) { Z++; PATH.push({ Z, A, k: "b", st: STAB.has(key(Z, A)) }); }
    } }
  const KMAX = PATH.length - 1, K0 = PATH.findIndex((p) => p.Z === 56 && p.A === 138);

  // ---- the r-process sketch: (N, Z) points with waiting points at the magic numbers ----
  const RP = [];
  { const seg = (n0, z0, n1, z1) => { for (let n = n0; n <= n1; n++) RP.push({ N: n, Z: Math.round(lerp(z0, z1, (n - n0) / Math.max(1, n1 - n0))) }); };
    seg(36, 22, 49, 27); for (let z = 28; z <= 30; z++) RP.push({ N: 50, Z: z, w: 1 });
    seg(51, 31, 81, 45); for (let z = 46; z <= 48; z++) RP.push({ N: 82, Z: z, w: 1 });
    seg(83, 49, 125, 65); for (let z = 66; z <= 70; z++) RP.push({ N: 126, Z: z, w: 1 });
    RP.forEach((p) => { p.A = p.N + p.Z; let zs = p.Z + 1; while (zs <= 83 && !STAB.has(key(zs, p.A))) zs++; p.Zs = zs <= 83 ? zs : null; });
    for (let i = RP.length - 1; i >= 0; i--) if (RP[i].Zs == null || RP[i].Zs < 26) RP.splice(i, 1); }

  // ---- colours: MACS on a log scale, 1 mb (blue, captures poorly) to 3000 mb (red, captures easily) ----
  const RAMP = [[0, [44, 74, 168]], [0.3, [43, 160, 175]], [0.55, [120, 196, 110]], [0.75, [232, 197, 71]], [0.9, [240, 122, 43]], [1, [214, 51, 108]]];
  const mcol = (m, a = 1) => { const t = clamp((log10(Math.max(m, 0.1)) - 0) / 3.5, 0, 1); let i = 0; while (i < RAMP.length - 2 && t > RAMP[i + 1][0]) i++;
    const [t0, c0] = RAMP[i], [t1, c1] = RAMP[i + 1], q = (t - t0) / (t1 - t0); return `rgba(${c0.map((v, j) => Math.round(lerp(v, c1[j], q))).join(",")},${a})`; };
  const fmt = (x) => x >= 1e5 ? x.toExponential(1).replace("e+", " × 10^") : x >= 100 ? Math.round(x).toLocaleString("en-US") : x >= 10 ? x.toFixed(1) : x >= 1 ? x.toFixed(2) : x >= 0.01 ? x.toFixed(3) : x.toPrecision(2);
  const sup = (s) => s.replace(/\^(-?\d+)/, (m, d) => d.split("").map((c) => (c === "-" ? "⁻" : "⁰¹²³⁴⁵⁶⁷⁸⁹"[c])).join(""));
  // the comparison figures come from the scoreboard (its own MACS calculation), not from the σ shown: say so
  const boardTxt = (e) => ratioTxt(e) + " (" + (WT.ui ? WT.ui("nav_board", "Scoreboard") : "Scoreboard") + ")";
  const ratioTxt = (e) => { const r = Math.pow(10, e); return r >= 1 ? WT.trf("{a} % above measured", Math.round((r - 1) * 100)) : WT.trf("{a} % below measured", Math.round((1 - r) * 100)); };

  const geo = {}, R = rng(7);
  const drift = []; for (let i = 0; i < 70; i++) drift.push({ u: R(), v: R(), s: 0.5 + R(), p: R() * TAU });
  const twinkle = []; for (let i = 0; i < 90; i++) twinkle.push({ u: R(), v: R(), p: R() * TAU, s: 0.5 + R() * 1.5 });

  function setBtns(S) {
    document.querySelectorAll('#stars [data-act^="stv"]').forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.act === "stv" + S.sv)));
    document.querySelectorAll('#stars [data-act="stS"]').forEach((b) => b.setAttribute("aria-pressed", String(!!S.showS)));
    document.querySelectorAll('#stars [data-act="stR"]').forEach((b) => b.setAttribute("aria-pressed", String(!!S.showR)));
  }
  function grabSetup(cv, S) {
    let drag = false;
    const pick = (x, y) => { S.hx = x; S.hy = y; S.hoverT = S.time; };
    const kAt = (x, y) => { // nearest path node on the chart
      const c = geo.chart; if (!c) return null; let best = -1, bd = 1e9;
      PATH.forEach((p, i) => { const d = Math.hypot(c.X(p.A - p.Z) - x, c.Y(p.Z) - y); if (d < bd) { bd = d; best = i; } });
      return bd < c.cell * 4 ? best : null; };
    WT.grab(cv, {
      down(x, y) {
        pick(x, y);
        if (S.mode === "s") { const k = kAt(x, y); if (k != null) { drag = true; S.to("k", k); sync("k", k); return true; } }
        if (S.mode === "r" && geo.chart) { drag = true; return true; }
        return false;
      },
      move(x, y) { pick(x, y); if (!drag) return;
        if (S.mode === "s") { const k = kAt(x, y); if (k != null) { S.to("k", k); sync("k", k); } }
        else if (S.mode === "r") { const c = geo.chart, v = clamp((x - c.x0) / (c.x1 - c.x0) * 1.6 - 0.3, 0, 1); S.to("rt", 1 - v); sync("rt", 1 - v); } },
      up() { drag = false; }, cancel() { drag = false; },
      hover(x, y) { pick(x, y); cv.style.cursor = S.mode === "s" || S.mode === "r" ? "pointer" : "crosshair"; },
    });
  }
  const sync = (k, v) => document.querySelectorAll(`#stars [data-bind="${k}"]`).forEach((i) => (i.value = v));

  WT.chapter("stars", {
    level: 1, num: "Lesson 1", title: "Where the elements come from", short: "Stars",
    html: `
<div class="step">
  <h3>Fusion stops at iron</h3>
  <p>Stars fuse light nuclei up to iron; nearly everything heavier is built by adding neutrons.</p>
</div>
<div class="step">
  <h3>The slow path</h3>
  <p>In giant stars neutrons come rarely, so an unstable nucleus beta-decays first: the path zig-zags along the stable nuclei.</p>
  <div class="ctl"><label for="st-k">Neutron captures</label><input id="st-k" type="range" data-bind="k" min="0" max="${KMAX}" step="1" value="${K0}"></div>
</div>
<div class="step">
  <h3>The fast path</h3>
  <p>In a neutron-star merger neutrons flood in faster than nuclei can decay; afterwards the neutron-rich nuclei decay back to stability.</p>
  <div class="ctl"><label for="st-rt">Decay back</label><input id="st-rt" type="range" data-bind="rt" min="0" max="1" step="0.01" value="0"></div>
</div>
<div class="step">
  <h3>Magic numbers make peaks</h3>
  <p>Nuclei with 50, 82 or 126 neutrons hardly capture, so matter piles up there: s-peaks at strontium, barium and lead, r-peaks a little lighter.</p>
  <div class="btns"><button class="btn ghost" data-act="stS" aria-pressed="true">s-process peaks</button> <button class="btn ghost" data-act="stR" aria-pressed="true">r-process peaks</button></div>
</div>
<div class="step">
  <h3>Rare where capture is easy</h3>
  <p>For isotopes made only by the s-process, abundance Nₛ times capture cross section σ stays nearly flat between magic numbers. σ here is INCOGNITA's computed value at 30 keV.</p>
  <div class="btns"><button class="btn ghost" data-act="stvs" aria-pressed="false">σ</button> <button class="btn ghost" data-act="stvn" aria-pressed="false">Nₛ</button> <button class="btn ghost" data-act="stvsn" aria-pressed="true">σ × Nₛ</button></div>
</div>
<div class="step">
  <h3>Checked against measurements</h3>
  <p>INCOGNITA's 30 keV values divided by measured ones, for ${CHK.length} stable nuclides (<a href="scoreboard.html">scoreboard</a>).</p>
</div>`,
    setup(S) {
      S.set("mode", "curve"); S.set("k", K0); S.set("rt", 0); S.sv = "sn"; S.showS = 1; S.showR = 1;
      S.set("a0", 1); S.set("ws", 1); S.set("wn", 1); S.set("ylo", 0); S.set("yhi", 4); S.set("colA", 1);
      ["s", "n", "sn"].forEach((v) => S.on("stv" + v, () => { S.sv = v; view(S); setBtns(S); }));
      S.on("stS", () => { S.showS = S.showS ? 0 : 1; setBtns(S); });
      S.on("stR", () => { S.showR = S.showR ? 0 : 1; setBtns(S); });
    },
    steps: [
      (S) => { S.set("mode", "curve"); S.to("a0", 1); },
      (S) => { S.set("mode", "s"); S.to("colA", 1); },
      (S) => { S.set("mode", "r"); S.to("colA", 0.22); },
      (S) => { S.set("mode", "peaks"); S.to("a0", 56); },
      (S) => { S.set("mode", "sigN"); S.sv = "sn"; view(S); setBtns(S); },
      (S) => { S.set("mode", "check"); },
    ],
    frame(g, S, dt) {
      const { W, H, c } = g, phone = W < 600, fs = phone ? 11 : 13;
      if (!S.grabbed) { S.grabbed = true; grabSetup(g.ctx.canvas, S); }
      if (document.body.classList.contains("shot") && !S.snapped) { S.snapped = true; ["a0", "ws", "wn", "ylo", "yhi", "colA", "k", "rt"].forEach((k) => (S[k] = S.target[k])); }
      sky(g, S, phone);
      if (S.mode === "s" || S.mode === "r") chart(g, S, dt, phone, fs);
      else if (S.mode === "sigN") sigN(g, S, phone, fs);
      else if (S.mode === "check") check(g, S, phone, fs);
      else curve(g, S, phone, fs);
    },
  });
  function view(S) { // sigma, N or sigma x N: weights of log sigma and log N, and the y range
    const t = { s: [1, 0, 0.5, 3.5], n: [0, 1, -3, 1.5], sn: [1, 1, 0, 4] }[S.sv];
    S.to("ws", t[0]); S.to("wn", t[1]); S.to("ylo", t[2]); S.to("yhi", t[3]);
  }

  // faint twinkling background: it is about stars
  function sky(g, S, phone) {
    const { W, H, c } = g;
    twinkle.forEach((t) => { const a = 0.1 + 0.12 * Math.sin(S.time * t.s + t.p); if (a > 0.02) g.dot(t.u * W, t.v * H, phone ? 0.8 : 1.1, c.soft, a); });
  }

  // ---------- abundance curve (steps 0 and 3) ----------
  function curve(g, S, phone, fs) {
    const { W, H, c, ctx } = g, pk = S.mode === "peaks";
    const x0 = phone ? 34 : 64, x1 = W - (phone ? 10 : 24), y0 = H * (phone ? 0.13 : 0.12), y1 = H * (phone ? 0.8 : 0.84);
    const a0 = S.a0, a1 = 210, lo = lerp(-2.5, -2.3, (a0 - 1) / 55), hi = lerp(10.6, 6.2, (a0 - 1) / 55);
    const X = (A) => lerp(x0, x1, (A - a0) / (a1 - a0)), Y = (n) => lerp(y1, y0, (log10(n) - lo) / (hi - lo));
    geo.curve = { x0, x1, X };
    g.clip(x0 - 6, 0, W - x0 + 6, y1 + 6);
    // regions: fusion up to the iron peak, neutron capture beyond
    const fe = X(60.5), bb = X(4.5), fu = X(11.5); // Li, Be, B (A 6-11) are left unshaded: they come mostly from cosmic rays, not fusion
    if (bb > x0) { ctx.save(); ctx.fillStyle = g.rgba(c.photon, 0.1); ctx.fillRect(x0, y0, bb - x0, y1 - y0); ctx.restore(); }
    if (fe > x0) { ctx.save(); const gr = ctx.createLinearGradient(Math.max(fu, x0), 0, fe, 0); gr.addColorStop(0, g.rgba(c.warm, 0.05)); gr.addColorStop(1, g.rgba(c.warm, 0.14)); ctx.fillStyle = gr; ctx.fillRect(Math.max(fu, x0), y0, fe - Math.max(fu, x0), y1 - y0); ctx.restore(); }
    ctx.save(); const gr2 = ctx.createLinearGradient(Math.max(fe, x0), 0, x1, 0); gr2.addColorStop(0, g.rgba(c.neutron, 0.1)); gr2.addColorStop(1, g.rgba(c.neutron, 0.02)); ctx.fillStyle = gr2; ctx.fillRect(Math.max(fe, x0), y0, x1 - Math.max(fe, x0), y1 - y0); ctx.restore();
    // magic-number peaks (step 3)
    const pkA = pk ? 1 : 0;
    if (pk) {
      const mk = (A, col, top, txt, sub) => { const x = X(A); g.line(x, y0 + 4, x, y1, col, 1.5, 0.55, [3, 4]); g.glow(x, Y(AB.find((a) => a[0] === A)[1]), phone ? 14 : 22, col, 0.6);
        g.label(txt, x, top, { color: col, size: fs - 1, weight: 700, bg: true }); if (sub && !phone) g.label(sub, x, top + fs + 4, { color: col, size: fs - 2, bg: true }); };
      if (S.showR) [[80, "Se, Kr"], [130, "Te, Xe"], [195, "Pt"]].forEach(([A, t]) => mk(A, c.alpha, y1 - (phone ? 40 : 52), phone ? `r ${A}` : `r-peak ${t}`, phone ? "" : `A ≈ ${A}`));
      if (S.showS) [[88, "Sr", 50], [138, "Ba", 82], [208, "Pb", 126]].forEach(([A, t, n]) => mk(A, c.neutron, y0 + 12, phone ? `s ${t}` : `s-peak ${t}`, `N = ${n}`));
    }
    // the curve
    const pts = AB.filter((a) => a[0] >= a0 - 1).map((a) => [X(a[0]), Y(a[1])]);
    g.ground(pts, c.accent, (y1 - y0) * 0.5, 0.18); g.poly(pts, c.accent, phone ? 1.4 : 1.8, 0.9);
    AB.forEach((a) => { if (a[0] < a0 - 1) return; const x = X(a[0]), y = Y(a[1]), heavy = a[0] > 60; g.dot(x, y, phone ? 1.8 : pk ? 2.6 : 2.2, heavy ? c.neutron : a[0] <= 4 ? c.photon : a[0] <= 11 ? c.soft : c.warm, 0.95); });
    ctx.restore();
    // axes
    g.line(x0, y1, x1, y1, c.line, 1);
    const tks = pk ? [60, 80, 100, 120, 140, 160, 180, 200] : [1, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200];
    tks.forEach((A) => { if (A < a0 - 0.5) return; const x = X(A); g.line(x, y1, x, y1 + 4, c.faint, 1); g.label(String(A), x, y1 + 13, { color: c.soft, size: fs - 2 }); });
    g.label(phone ? "mass number A" : "mass number A (protons + neutrons)", (x0 + x1) / 2, y1 + (phone ? 27 : 32), { color: c.soft, size: fs - 1 });
    for (let e = Math.ceil(lo); e <= hi; e += pk ? 1 : 2) { const y = Y(Math.pow(10, e)); if (y < y0 - 2) continue; g.line(x0, y, x1, y, c.line, 1, 0.45, [2, 5]); g.label(sup("10^" + e).replace("10⁰", "1"), x0 - 6, y, { color: c.faint, size: fs - 2, align: "right", raw: true }); }
    g.label(phone ? "atoms per 10⁶ silicon" : "atoms per million silicon atoms (Solar System)", x0, y0 - (phone ? 14 : 18), { color: c.soft, size: fs - 1, align: "left" });
    if (!pk) {
      g.label(phone ? "Big Bang" : "Big Bang", bb + 4, y1 - 14, { color: c.photon, size: fs - 1, weight: 700, align: "left" });
      g.label(phone ? "fusion" : "fusion in stars", lerp(fu, fe, 0.5), y0 + 14, { color: c.warm, size: fs, weight: 700 });
      g.label(phone ? "neutron capture" : "made by neutron capture", lerp(fe, x1, 0.5), y0 + 14, { color: c.neutron, size: fs, weight: 700 });
      [[1, "H"], [4, "He"], [16, "O"], [56, "Fe"]].forEach(([A, s]) => { const a = AB.find((v) => v[0] === A); g.label(s, X(A) + (A === 1 ? 10 : 0), Y(a[1]) - (phone ? 11 : 14), { color: c.ink, size: fs, weight: 700 }); });
    }
    // readout at the cursor
    let A = null;
    if (S.hx != null && S.hx > x0 && S.hx < x1 && S.hy > y0 - 20 && S.hy < y1 + 20) A = Math.round(lerp(a0, a1, (S.hx - x0) / (x1 - x0)));
    const a = A != null && AB.find((v) => v[0] === A);
    const ty = H - (phone ? 14 : 22);
    if (a) {
      const x = X(a[0]), y = Y(a[1]); g.line(x, y, x, y1, c.ink, 1, 0.35); g.glow(x, y, 14, c.accent, 0.6); g.dot(x, y, 4, c.accent);
      g.label(WT.trf("A = {a}: mostly {b}, {c} atoms per million silicon", a[0], nm(a[2], a[0]), sup(fmt(a[1]))), W / 2, ty, { color: c.ink, size: fs + 1, weight: 600, serif: true, raw: true });
    } else g.label(pk ? (phone ? "peaks: sources Lodders et al. 2009" : "abundances: Lodders, Palme & Gail 2009") : (phone ? "Lodders et al. 2009" : "abundances: Lodders, Palme & Gail 2009 · point at the curve"), W / 2, ty, { color: c.soft, size: fs - 1 });
  }

  // ---------- chart of nuclides (steps 1 and 2) ----------
  const N0 = 28, N1 = 127, Z0 = 26, Z1 = 84;
  function chart(g, S, dt, phone, fs) {
    const { W, H, c, ctx } = g, rmode = S.mode === "r";
    const nN = N1 - N0 + 1, nZ = Z1 - Z0 + 1, top = phone ? 30 : 46, bottom = phone ? 62 : 92, left = phone ? 22 : 40, right = phone ? 6 : 16;
    const cell = Math.min((W - left - right) / nN, (H - top - bottom) / nZ);
    const x0 = left + (W - left - right - cell * nN) / 2, y1 = top + cell * nZ, x1 = x0 + cell * nN;
    const X = (N) => x0 + (N - N0 + 0.5) * cell, Y = (Z) => y1 - (Z - Z0 + 0.5) * cell;
    geo.chart = { x0, x1, X, Y, cell };
    // magic numbers
    [50, 82, 126].forEach((n) => { const x = X(n); g.line(x, top - 4, x, y1, c.faint, 1, 0.5, [3, 4]); g.label(`N = ${n}`, x, y1 + (phone ? 10 : 13), { color: c.soft, size: fs - 2, weight: 600 }); });
    [50, 82].forEach((z) => { const y = Y(z); g.line(x0, y, x1, y, c.faint, 1, 0.3, [3, 4]); });
    // stable nuclides coloured by INCOGNITA's MACS
    const ca = S.colA;
    ST.forEach((s) => { if (s.N < N0 || s.N > N1) return; const x = X(s.N), y = Y(s.Z), w = cell * 0.9;
      ctx.fillStyle = s.m != null ? mcol(s.m, 0.25 + 0.75 * ca) : g.rgba(c.faint, 0.4); ctx.fillRect(x - w / 2, y - w / 2, w, w); });
    // element labels
    [[26, "Fe"], [38, "Sr"], [50, "Sn"], [56, "Ba"], [82, "Pb"]].forEach(([z, s]) => g.label(s, x0 - 4, Y(z), { color: c.soft, size: fs - 2, align: "right" }));
    g.label(phone ? "neutrons N →" : "neutrons N →", x1, y1 + (phone ? 24 : 32), { color: c.soft, size: fs - 1, align: "right" });
    g.label(phone ? "↑ protons Z" : "↑ protons Z", x0 - (phone ? 2 : 4), top - (phone ? 12 : 16), { color: c.soft, size: fs - 1, align: "left" });
    // colour legend (MACS)
    { const lw = phone ? 96 : 170, lh = phone ? 5 : 7, lx = x1 - lw - (phone ? 16 : 22), ly = top - (phone ? 16 : 26);
      for (let i = 0; i < lw; i++) { ctx.fillStyle = mcol(Math.pow(10, 3.5 * i / lw), 0.25 + 0.75 * ca); ctx.fillRect(lx + i, ly, 1.2, lh); }
      [[1, "1"], [10, "10"], [100, "100"], [1000, "1000"]].forEach(([m, t]) => g.label(t, lx + lw * log10(m) / 3.5, ly + lh + (phone ? 7 : 9), { color: c.soft, size: fs - 3, align: m === 1 ? "left" : "center" }));
      g.label("mb", lx + lw + 6, ly + lh / 2, { color: c.soft, size: fs - 3, align: "left" });
      if (!phone) g.label("INCOGNITA: capture at 30 keV (MACS)", lx - 10, ly + 3, { color: c.soft, size: fs - 2, align: "right", alpha: 0.5 + 0.5 * ca }); }
    // drifting neutrons (alive): slow in the star, a flood in the merger
    const fast = rmode ? 1 - smooth(0.1, 0.5, S.rt) : 0;
    drift.forEach((d, i) => { if (!rmode && i > 24) return; const sp = rmode ? 0.05 + 0.4 * fast : 0.02;
      const x = x0 + ((d.u + S.time * sp * d.s) % 1) * (x1 - x0), y = top + d.v * (y1 - top) + Math.sin(S.time * d.s + d.p) * 6;
      g.dot(x, y, phone ? 1.3 : 1.8, c.neutron, rmode ? 0.15 + 0.5 * fast : 0.22); });
    if (rmode) rpath(g, S, phone, fs, X, Y, cell);
    spath(g, S, phone, fs, X, Y, cell, rmode);
    // readout
    const ty = Math.min(H - (phone ? 26 : 42), y1 + (phone ? 44 : 84));
    const hov = hoverNuc(S, X, Y, cell, x0, x1, top, y1);
    if (rmode) {
      const t = S.rt;
      g.label(t < 0.05 ? (phone ? "r-process: very neutron-rich nuclei" : "r-process: a flood of neutrons makes very neutron-rich nuclei") : t > 0.95 ? (phone ? "decayed back: r-made stable isotopes" : "decayed back: each lands on the most neutron-rich stable isobar") : (phone ? "beta decays, A fixed" : "beta decays carry them back, mass number A fixed"), W / 2, ty, { color: c.ink, size: fs + 1, weight: 600, serif: true });
      g.label(phone ? "seen in 2017: merger GW170817" : "seen in 2017: the neutron-star merger GW170817 and its kilonova", W / 2, ty + fs + 10, { color: c.alpha, size: fs - 1 });
      g.label("r-path: illustration", W - 6, H - 10, { color: c.faint, size: 10, align: "right" });
      if (hov) nucCard(g, hov, phone, fs, ty - (phone ? 30 : 40));
      return;
    }
    const p = PATH[Math.round(S.k)], s = STAB.get(key(p.Z, p.A));
    const lab = s ? (s.m != null ? WT.trf(phone ? "{a} · N = {b} · σ = {c} mb" : "{a} · N = {b} · INCOGNITA: σ = {c} mb at 30 keV", nm(p.Z, p.A), p.A - p.Z, fmt(s.m)) : nm(p.Z, p.A)) :
      p.k === "a" ? "" : WT.trf(phone ? "{a} · unstable: beta decay" : "{a} · unstable: it beta-decays before the next neutron", nm(p.Z, p.A));
    const magic = s && [50, 82, 126].includes(p.A - p.Z);
    g.label(p.Z >= 82 && Math.round(S.k) >= KMAX - 3 ? (phone ? "end: the lead–bismuth cycle" : "end of the road: Bi-210 → Po-210 → alpha decay back to Pb-206") : lab, W / 2, ty, { color: c.ink, size: fs + 1, weight: 600, serif: true, raw: true });
    g.label(magic ? (phone ? "magic N: captures poorly, matter piles up" : "magic neutron number: it captures poorly, so matter piles up here") : (phone ? "drag along the path" : "drag along the path, or use the slider"), W / 2, ty + fs + 10, { color: magic ? c.neutron : c.soft, size: fs - 1, weight: magic ? 600 : 500 });
    if (hov) nucCard(g, hov, phone, fs, ty - (phone ? 30 : 40));
  }
  function hoverNuc(S, X, Y, cell, x0, x1, top, y1) {
    if (S.hx == null || S.hx < x0 || S.hx > x1 || S.hy < top || S.hy > y1 || S.time - S.hoverT > 4) return null;
    let best = null, bd = cell * 0.9; ST.forEach((s) => { const d = Math.hypot(X(s.N) - S.hx, Y(s.Z) - S.hy); if (d < bd) { bd = d; best = s; } });
    return best && { s: best, x: X(best.N), y: Y(best.Z), cell };
  }
  function nucCard(g, h, phone, fs, y) {
    const { c } = g, s = h.s;
    g.ring(h.x, h.y, h.cell * 1.1, c.ink, 1.5);
    let t = s.m != null ? WT.trf("{a}: INCOGNITA σ = {b} mb", nm(s.Z, s.A), fmt(s.m)) : nm(s.Z, s.A);
    if (s.tier === "A") t += WT.tr(" (scaled to a measured value)");
    else if (s.err != null && !phone) t += " · " + boardTxt(s.err);
    g.label(t, g.W / 2, y, { color: c.ink, size: fs, weight: 600, bg: true, raw: true });
  }
  function spath(g, S, phone, fs, X, Y, cell, rmode) {
    const { c } = g, k = rmode ? KMAX : S.k, kf = Math.floor(k), fr = k - kf, al = rmode ? 0.3 : 1;
    const P = (p) => [X(p.A - p.Z), Y(p.Z)];
    const lw = phone ? 1.4 : 2;
    for (let i = 1; i <= Math.min(kf + 1, KMAX); i++) {
      const a = P(PATH[i - 1]), b = P(PATH[i]), q = i <= kf ? 1 : fr; if (q <= 0) break;
      const col = PATH[i].k === "c" ? c.ink : PATH[i].k === "a" ? c.alpha : c.proton;
      g.line(a[0], a[1], lerp(a[0], b[0], q), lerp(a[1], b[1], q), col, lw, al);
      if (!PATH[i].st && i <= kf) { const w = cell * 0.7; g.ctx.save(); g.ctx.globalAlpha = al * 0.8; g.ctx.strokeStyle = c.proton; g.ctx.lineWidth = 1; g.ctx.strokeRect(b[0] - w / 2, b[1] - w / 2, w, w); g.ctx.restore(); }
    }
    if (rmode) return;
    // the walker
    const a = P(PATH[kf]), b = P(PATH[Math.min(kf + 1, KMAX)]), wx = lerp(a[0], b[0], fr), wy = lerp(a[1], b[1], fr);
    const pulse = 0.5 + 0.5 * Math.sin(S.time * 4);
    g.glow(wx, wy, cell * (3 + pulse), c.accent, 0.55); g.ball(wx, wy, Math.max(3, cell * 0.75), c.accent);
    // a neutron arriving from the left at each capture
    const nxt = PATH[Math.min(kf + 1, KMAX)];
    if (nxt.k === "c") { const ph = (S.time * 0.8) % 1, nx = wx - cell * (6 - 5 * ph), ny = wy - cell * 2.5 * (1 - ph); g.ball(nx, ny, Math.max(2, cell * 0.45), c.neutron, 0.9 * (1 - ph * 0.3)); }
    // legend of moves
    if (!phone) {
      const lx = X(N0) + 4, ly = Y(80);
      g.line(lx, ly, lx + 20, ly, c.ink, 2.4); g.label("neutron capture", lx + 26, ly, { color: c.ink, size: fs - 2, align: "left" });
      g.line(lx + 8, ly + 22, lx + 20, ly + 10, c.proton, 2.4); g.label("beta decay (n → p)", lx + 26, ly + 16, { color: c.proton, size: fs - 2, align: "left" });
    }
  }
  function rpath(g, S, phone, fs, X, Y, cell) {
    const { c } = g, t = S.rt;
    // the sketch of the path, then nuclei sliding along their isobars
    if (t < 0.6) { const pts = RP.filter((p) => p.Z >= Z0).map((p) => [X(p.N), Y(p.Z)]); g.poly(pts, c.alpha, phone ? 4 : 7, 0.18 * (1 - t / 0.6)); }
    RP.forEach((p, i) => {
      const steps = p.Zs - p.Z, z = p.Z + steps * smooth(0, 1, clamp(t * 1.15 - (i % 7) * 0.02, 0, 1)), n = p.A - z;
      if (z < Z0 - 0.5) return;
      const x = X(n), y = Y(z), r = Math.max(1.6, cell * (p.w ? 0.62 : 0.42)), land = t > 0.97;
      if (t > 0.05 && !land) g.line(X(p.N), Y(Math.max(p.Z, Z0 - 0.5)), x, y, c.alpha, 1, 0.12);
      g.glow(x, y, r * (p.w ? 5 : 3), c.alpha, p.w ? 0.45 : 0.25); g.dot(x, y, r, c.alpha, 0.95);
      if (land) g.ring(x, y, cell * 0.8, c.alpha, 1.2, 0.9);
    });
    if (t < 0.3) {
      const lab = (n, z, s) => g.label(s, X(n) + (n > 100 ? -1 : 1) * (phone ? 4 : 8), Y(z) + (phone ? 10 : 14), { color: c.alpha, size: fs - 2, weight: 600, align: n > 100 ? "right" : "left", alpha: 1 - t / 0.3 });
      lab(50, 28, phone ? "wait" : "waiting point"); lab(82, 46, phone ? "wait" : "waiting point"); lab(126, 66, phone ? "wait" : "waiting point");
    }
  }

  // ---------- sigma x N (step 4) ----------
  function sigN(g, S, phone, fs) {
    const { W, H, c, ctx } = g;
    const x0 = phone ? 34 : 64, x1 = W - (phone ? 10 : 24), y0 = H * (phone ? 0.14 : 0.12), y1 = H * (phone ? 0.78 : 0.78);
    const X = (A) => lerp(x0, x1, (A - 64) / (210 - 64)), Yl = (v) => lerp(y1, y0, (v - S.ylo) / (S.yhi - S.ylo));
    const val = (s) => S.ws * log10(s.m) + S.wn * log10(s.ab);
    // magic numbers along the s-path
    [[88, 50], [138, 82], [208, 126]].forEach(([A, n]) => { const x = X(A); g.line(x, y0, x, y1, c.neutron, 1.2, 0.45, [3, 4]); g.label(`N = ${n}`, x, y0 - (phone ? 8 : 10), { color: c.neutron, size: fs - 2, weight: 600 }); });
    // grid
    for (let e = Math.ceil(S.ylo - 1e-6); e <= S.yhi + 1e-6; e++) { const y = Yl(e); if (y < y0 - 1 || y > y1 + 1) continue; g.line(x0, y, x1, y, c.line, 1, 0.45, [2, 5]); g.label(sup("10^" + e).replace("10⁰", "1"), x0 - 6, y, { color: c.faint, size: fs - 2, align: "right", raw: true }); }
    g.line(x0, y1, x1, y1, c.line, 1);
    [80, 100, 120, 140, 160, 180, 200].forEach((A) => { const x = X(A); g.line(x, y1, x, y1 + 4, c.faint, 1); g.label(String(A), x, y1 + 13, { color: c.soft, size: fs - 2 }); });
    g.label("mass number A", (x0 + x1) / 2, y1 + (phone ? 27 : 32), { color: c.soft, size: fs - 1 });
    const sn = S.ws > 0.5 && S.wn > 0.5;
    // segment means between magic numbers (sigma x N view): a flat bar per segment, from these points
    const segs = [[89, 138], [139, 208]]; // below A ~ 90 the weak s-process of massive stars adds in, so no flat stretch is drawn there
    if (sn) segs.forEach(([a, b]) => { const pts = SONLY.filter((s) => s.A >= a && s.A <= b); if (!pts.length) return; const m = pts.reduce((q, s) => q + val(s), 0) / pts.length;
      const xa = X(Math.min(...pts.map((s) => s.A))) - 6, xb = X(Math.max(...pts.map((s) => s.A))) + 6, y = Yl(m), al = smooth(0.5, 1, Math.min(S.ws, S.wn));
      ctx.save(); ctx.globalAlpha = 0.14 * al; ctx.fillStyle = c.accent; ctx.fillRect(xa, y - 7, xb - xa, 14); ctx.restore(); g.line(xa, y, xb, y, c.accent, 1.5, 0.6 * al); });
    // points, with INCOGNITA's 68 % band on sigma
    const pts = SONLY.map((s) => [X(s.A), Yl(val(s))]);
    g.poly(pts, c.accent, 1.2, 0.4);
    let hov = null, hd = phone ? 18 : 14;
    SONLY.forEach((s, i) => { const [x, y] = pts[i], du = S.ws * log10(s.u), yu = Yl(val(s) + du), yd = Yl(val(s) - du);
      g.line(x, yu, x, yd, c.accent, 1.2, 0.45);
      const col = mcol(s.m); if (s.tier === "A") g.ring(x, y, phone ? 3.6 : 4.8, c.ink, 1.6); else { g.glow(x, y, 12, c.accent, 0.25); g.dot(x, y, phone ? 3.6 : 4.8, col); g.ring(x, y, phone ? 3.6 : 4.8, c.ink, 0.8, 0.5); }
      if (S.hx != null) { const d = Math.hypot(S.hx - x, S.hy - y); if (d < hd) { hd = d; hov = s; } } });
    if (sn) g.label(phone ? "weak s-process too" : "plus a weaker s-process (massive stars)", X(78), Yl(1.6), { color: c.soft, size: fs - 2, alpha: smooth(0.5, 1, Math.min(S.ws, S.wn)) });
    // labels of a few
    if (!phone) [[38, 86], [56, 136], [62, 150], [71, 176], [82, 204]].forEach(([Z, A]) => { const s = STAB.get(key(Z, A)); g.label(nm(Z, A), X(A) + (A === 86 ? -14 : 0), Yl(val(s)) + (A === 176 ? 18 : -16), { color: c.soft, size: fs - 2 }); });
    const yl = { s: phone ? "σ (mb), INCOGNITA, 30 keV" : "σ: INCOGNITA's capture cross section at 30 keV (mb)", n: phone ? "Nₛ: atoms per 10⁶ Si" : "Nₛ: solar abundance, atoms per million silicon atoms", sn: phone ? "σ × Nₛ (mb × atoms per 10⁶ Si)" : "σ × Nₛ (mb × atoms per million Si)" }[S.sv];
    g.label(yl, x0, y0 - (phone ? 22 : 30), { color: c.soft, size: fs - 1, align: "left" });
    const ty = H - (phone ? 14 : 22);
    if (hov) { const x = X(hov.A), y = Yl(val(hov)); g.ring(x, y, 9, c.ink, 1.5);
      g.label(WT.trf("{a}: σ = {b} mb × Nₛ = {c} → σNₛ = {d}", nm(hov.Z, hov.A), fmt(hov.m), fmt(hov.ab), fmt(hov.m * hov.ab)) + (hov.tier === "A" ? WT.tr(" (σ scaled to a measured value)") : ""), W / 2, ty, { color: c.ink, size: fs, weight: 600, serif: true, raw: true }); }
    else g.label(S.sv === "sn" ? (phone ? "flat between magic numbers, steps down at each" : "nearly flat between magic numbers, a step down at each") : S.sv === "s" ? (phone ? "σ alone: scattered" : "σ alone jumps around from isotope to isotope") : (phone ? "Nₛ alone: scattered" : "Nₛ alone jumps around the other way"), W / 2, ty, { color: c.ink, size: fs, weight: 600, serif: true });
    g.label(phone ? "s-only isotopes · bars: INCOGNITA 68 %" : "s-only isotopes · σ: INCOGNITA (bars: its 68 % range; open circle: scaled to a measurement) · Nₛ: Lodders et al. 2009", W / 2, ty - (phone ? 18 : 22), { color: c.soft, size: fs - 2 });
  }

  // ---------- INCOGNITA vs measured (step 5) ----------
  function check(g, S, phone, fs) {
    const { W, H, c, ctx } = g;
    const x0 = phone ? 36 : 64, x1 = W - (phone ? 10 : 24), y0 = H * (phone ? 0.14 : 0.12), y1 = H * (phone ? 0.76 : 0.76), L = 0.6;
    const X = (A) => lerp(x0, x1, (A - 50) / (212 - 50)), Y = (e) => lerp(y1, y0, (clamp(e, -L, L) + L) / (2 * L));
    // bands: within 25 % and within a factor 2
    ctx.save(); ctx.fillStyle = g.rgba(c.fission, 0.1); ctx.fillRect(x0, Y(log10(1.25)), x1 - x0, Y(log10(0.8)) - Y(log10(1.25))); ctx.restore();
    [[1, "×1", 1.6], [1.25, "+25 %", 1], [0.8, "−20 %", 1], [2, "×2", 1], [0.5, "×½", 1]].forEach(([r, t, w]) => { const y = Y(log10(r)); g.line(x0, y, x1, y, r === 1 ? c.ink : c.line, w, r === 1 ? 0.6 : 0.6, r === 1 ? null : [2, 5]); g.label(t, x0 - 6, y, { color: c.soft, size: fs - 2, align: "right", raw: true }); });
    g.line(x0, y1, x1, y1, c.line, 1);
    [60, 80, 100, 120, 140, 160, 180, 200].forEach((A) => { const x = X(A); g.line(x, y1, x, y1 + 4, c.faint, 1); g.label(String(A), x, y1 + 13, { color: c.soft, size: fs - 2 }); });
    g.label("mass number A", (x0 + x1) / 2, y1 + (phone ? 27 : 32), { color: c.soft, size: fs - 1 });
    g.label(phone ? "INCOGNITA ÷ measured, 30 keV" : "INCOGNITA's 30 keV capture rate (MACS) ÷ measured", x0, y0 - (phone ? 16 : 22), { color: c.soft, size: fs - 1, align: "left" });
    let hov = null, hd = phone ? 16 : 12;
    CHK.forEach((s, i) => { const x = X(s.A), y = Y(s.err), r = phone ? 3 : 4.2, bob = Math.sin(S.time * 1.5 + i) * 0.6;
      const col = s.sonly ? c.neutron : c.accent; g.glow(x, y + bob, r * 3, col, 0.3); g.dot(x, y + bob, r, col, s.sonly ? 1 : 0.75); if (s.sonly) g.ring(x, y + bob, r + 2.5, c.ink, 1.2, 0.8);
      if (Math.abs(s.err) > L) g.label(s.err > 0 ? "▲" : "▼", x, y + (s.err > 0 ? -10 : 10), { color: c.soft, size: 9 });
      if (S.hx != null) { const d = Math.hypot(S.hx - x, S.hy - y); if (d < hd) { hd = d; hov = s; } } });
    const ty = H - (phone ? 14 : 22);
    if (hov) { g.ring(X(hov.A), Y(hov.err), 10, c.ink, 1.5); g.label(hov.tier === "A" ? WT.trf("{a}: INCOGNITA's engine {b} (the library then scales to it)", nm(hov.Z, hov.A), ratioTxt(hov.err)) : WT.trf("{a}: INCOGNITA σ = {b} mb, {c}", nm(hov.Z, hov.A), fmt(hov.m), boardTxt(hov.err)), W / 2, ty, { color: c.ink, size: fs, weight: 600, serif: true, raw: true }); }
    else g.label(WT.trf(phone ? "{a} nuclides · typical difference {b} %" : "{a} stable nuclides · typical difference {b} % (median), rms {c} %", CHK.length, Math.round((Math.pow(10, MED) - 1) * 100), Math.round((Math.pow(10, RMS) - 1) * 100)), W / 2, ty, { color: c.ink, size: fs, weight: 600, serif: true, raw: true });
    g.label(phone ? "ringed: s-only · measured: KADoNiS" : "ringed: s-only isotopes · measured: compiled values (KADoNiS) · a development comparison, not a blind test", W / 2, ty - (phone ? 18 : 22), { color: c.soft, size: fs - 2 });
  }
})();
