/* Why nuclei hold together: binding energy per nucleon B/A against mass number A, from measured masses (AME2020: for each A
 * the most tightly bound measured isobar; values marked # (estimated) left out). Split: n + U-235 -> U-236 -> two fragments
 * A1 + A2 = 236 (the emitted neutrons ignored); energy released Q = A1 b(A1) + A2 b(A2) - 236 b(236), with b the most-bound
 * isobar of each A (real fragments are neutron-rich and reach these by beta decay; the sum is the same order: ~200 MeV).
 * Fuse: two equal light nuclei A1 + A1 -> 2 A1, Q = 2 A1 b(2 A1) - 2 A1 b(A1): positive up to the peak (Ni-62 is the most tightly bound: 8.795 MeV per nucleon; Fe-58 and Fe-56 follow closely). */
(function () {
  const { TAU, clamp, lerp, smooth, rng } = WT.util;
  const BA = [[2,1.1123,1,"H"],[3,2.8273,1,"H"],[4,7.0739,2,"He"],[5,5.5121,2,"He"],[6,5.3323,3,"Li"],[7,5.6064,3,"Li"],[8,7.0624,4,"Be"],[9,6.4627,4,"Be"],[10,6.4976,4,"Be"],[11,6.9277,5,"B"],[12,7.6801,6,"C"],[13,7.4698,6,"C"],[14,7.5203,6,"C"],[15,7.6995,7,"N"],[16,7.9762,8,"O"],[17,7.7507,8,"O"],[18,7.7671,8,"O"],[19,7.779,9,"F"],[20,8.0322,10,"Ne"],[21,7.9717,10,"Ne"],[22,8.0805,10,"Ne"],[23,8.1115,11,"Na"],[24,8.2607,12,"Mg"],[25,8.2235,12,"Mg"],[26,8.3339,12,"Mg"],[27,8.3316,13,"Al"],[28,8.4477,14,"Si"],[29,8.4486,14,"Si"],[30,8.5207,14,"Si"],[31,8.4812,15,"P"],[32,8.4931,16,"S"],[33,8.5138,15,"P"],[34,8.5835,16,"S"],[35,8.5379,16,"S"],[36,8.5754,16,"S"],[37,8.5703,17,"Cl"],[38,8.6143,18,"Ar"],[39,8.5626,18,"Ar"],[40,8.5953,18,"Ar"],[41,8.5761,19,"K"],[42,8.6166,20,"Ca"],[43,8.6007,20,"Ca"],[44,8.6582,20,"Ca"],[45,8.6305,20,"Ca"],[46,8.669,20,"Ca"],[47,8.6651,21,"Sc"],[48,8.723,22,"Ti"],[49,8.7112,22,"Ti"],[50,8.7557,22,"Ti"],[51,8.7421,23,"V"],[52,8.776,24,"Cr"],[53,8.7602,24,"Cr"],[54,8.778,24,"Cr"],[55,8.765,25,"Mn"],[56,8.7904,26,"Fe"],[57,8.7703,26,"Fe"],[58,8.7923,26,"Fe"],[59,8.768,27,"Co"],[60,8.7808,28,"Ni"],[61,8.765,28,"Ni"],[62,8.7946,28,"Ni"],[63,8.7635,28,"Ni"],[64,8.7775,28,"Ni"],[65,8.7571,29,"Cu"],[66,8.7596,30,"Zn"],[67,8.7375,29,"Cu"],[68,8.7557,30,"Zn"],[69,8.7246,31,"Ga"],[70,8.7298,30,"Zn"],[71,8.7176,31,"Ga"],[72,8.7317,32,"Ge"],[73,8.705,32,"Ge"],[74,8.7252,32,"Ge"],[75,8.7009,33,"As"],[76,8.7115,34,"Se"],[77,8.696,33,"As"],[78,8.7178,34,"Se"],[79,8.6956,34,"Se"],[80,8.7108,34,"Se"],[81,8.6959,35,"Br"],[82,8.7107,36,"Kr"],[83,8.6957,36,"Kr"],[84,8.7174,36,"Kr"],[85,8.6986,36,"Kr"],[86,8.712,36,"Kr"],[87,8.711,37,"Rb"],[88,8.7326,38,"Sr"],[89,8.714,39,"Y"],[90,8.71,40,"Zr"],[91,8.6933,40,"Zr"],[92,8.6927,40,"Zr"],[93,8.6716,40,"Zr"],[94,8.6668,40,"Zr"],[95,8.6487,42,"Mo"],[96,8.654,42,"Mo"],[97,8.6351,42,"Mo"],[98,8.6352,42,"Mo"],[99,8.6136,43,"Tc"],[100,8.6194,44,"Ru"],[101,8.6014,44,"Ru"],[102,8.6074,44,"Ru"],[103,8.5844,44,"Ru"],[104,8.5874,44,"Ru"],[105,8.5727,45,"Rh"],[106,8.58,46,"Pd"],[107,8.5609,46,"Pd"],[108,8.567,46,"Pd"],[109,8.5479,47,"Ag"],[110,8.5513,48,"Cd"],[111,8.5371,48,"Cd"],[112,8.5447,48,"Cd"],[113,8.527,48,"Cd"],[114,8.5315,48,"Cd"],[115,8.5165,49,"In"],[116,8.5231,50,"Sn"],[117,8.5096,50,"Sn"],[118,8.5165,50,"Sn"],[119,8.4994,50,"Sn"],[120,8.5045,50,"Sn"],[121,8.4852,50,"Sn"],[122,8.4879,50,"Sn"],[123,8.4723,51,"Sb"],[124,8.4733,52,"Te"],[125,8.4582,51,"Sb"],[126,8.4632,52,"Te"],[127,8.4461,52,"Te"],[128,8.4488,52,"Te"],[129,8.436,53,"I"],[130,8.4377,54,"Xe"],[131,8.4237,54,"Xe"],[132,8.4276,54,"Xe"],[133,8.4126,54,"Xe"],[134,8.4137,54,"Xe"],[135,8.4013,55,"Cs"],[136,8.4028,56,"Ba"],[137,8.3918,56,"Ba"],[138,8.3934,56,"Ba"],[139,8.378,57,"La"],[140,8.3763,58,"Ce"],[141,8.3554,58,"Ce"],[142,8.3471,58,"Ce"],[143,8.3305,60,"Nd"],[144,8.3269,60,"Nd"],[145,8.3092,60,"Nd"],[146,8.3041,60,"Nd"],[147,8.2844,61,"Pm"],[148,8.2796,62,"Sm"],[149,8.2635,62,"Sm"],[150,8.2616,62,"Sm"],[151,8.244,62,"Sm"],[152,8.2441,62,"Sm"],[153,8.2287,63,"Eu"],[154,8.2268,62,"Sm"],[155,8.2167,63,"Eu"],[156,8.2153,64,"Gd"],[157,8.2035,64,"Gd"],[158,8.2018,64,"Gd"],[159,8.1888,65,"Tb"],[160,8.1841,66,"Dy"],[161,8.1745,65,"Tb"],[162,8.1735,66,"Dy"],[163,8.1618,66,"Dy"],[164,8.1587,66,"Dy"],[165,8.147,67,"Ho"],[166,8.1419,68,"Er"],[167,8.1317,68,"Er"],[168,8.1296,68,"Er"],[169,8.117,68,"Er"],[170,8.112,68,"Er"],[171,8.1019,69,"Tm"],[172,8.0974,70,"Yb"],[173,8.0874,70,"Yb"],[174,8.0838,70,"Yb"],[175,8.0709,70,"Yb"],[176,8.0641,70,"Yb"],[177,8.0534,71,"Lu"],[178,8.0494,72,"Hf"],[179,8.0385,72,"Hf"],[180,8.0349,72,"Hf"],[181,8.0234,73,"Ta"],[182,8.0183,74,"W"],[183,8.0083,74,"W"],[184,8.0051,74,"W"],[185,7.9929,74,"W"],[186,7.9886,74,"W"],[187,7.978,75,"Re"],[188,7.9739,76,"Os"],[189,7.963,76,"Os"],[190,7.9621,76,"Os"],[191,7.9506,76,"Os"],[192,7.9485,76,"Os"],[193,7.9381,77,"Ir"],[194,7.9359,78,"Pt"],[195,7.9266,78,"Pt"],[196,7.9265,78,"Pt"],[197,7.916,78,"Pt"],[198,7.9142,78,"Pt"],[199,7.9069,79,"Au"],[200,7.9059,80,"Hg"],[201,7.8976,80,"Hg"],[202,7.8969,80,"Hg"],[203,7.8875,80,"Hg"],[204,7.8855,80,"Hg"],[205,7.8784,81,"Tl"],[206,7.8754,82,"Pb"],[207,7.8699,82,"Pb"],[208,7.8675,82,"Pb"],[209,7.8486,82,"Pb"],[210,7.836,82,"Pb"],[211,7.8198,83,"Bi"],[212,7.8102,84,"Po"],[213,7.794,84,"Po"],[214,7.7851,84,"Po"],[215,7.7682,84,"Po"],[216,7.7588,84,"Po"],[217,7.7446,85,"At"],[218,7.7388,86,"Rn"],[219,7.7238,86,"Rn"],[220,7.7173,86,"Rn"],[221,7.7033,87,"Fr"],[222,7.6967,88,"Ra"],[223,7.6853,88,"Ra"],[224,7.6799,88,"Ra"],[225,7.6676,88,"Ra"],[226,7.662,88,"Ra"],[227,7.6507,89,"Ac"],[228,7.6451,90,"Th"],[229,7.6347,90,"Th"],[230,7.631,90,"Th"],[231,7.6201,90,"Th"],[232,7.615,90,"Th"],[233,7.6049,91,"Pa"],[234,7.6007,92,"U"],[235,7.5909,92,"U"],[236,7.5865,92,"U"],[237,7.5761,92,"U"],[238,7.5701,92,"U"],[239,7.5606,93,"Np"],[240,7.556,94,"Pu"],[241,7.5464,94,"Pu"],[242,7.5413,94,"Pu"],[243,7.531,94,"Pu"],[244,7.5248,94,"Pu"],[245,7.5158,96,"Cm"],[246,7.5115,96,"Cm"],[247,7.5019,96,"Cm"],[248,7.4967,96,"Cm"],[249,7.486,97,"Bk"],[250,7.48,98,"Cf"],[251,7.4705,98,"Cf"],[252,7.4653,98,"Cf"],[253,7.4548,98,"Cf"],[254,7.4492,98,"Cf"],[255,7.4378,99,"Es"],[256,7.4318,100,"Fm"],[257,7.4222,100,"Fm"],[258,7.4097,101,"Md"],[259,7.4,102,"No"],[260,7.3426,106,"Sg"],[261,7.3714,104,"Rf"],[262,7.3412,106,"Sg"],[264,7.2984,108,"Hs"],[265,7.2962,108,"Hs"],[266,7.2983,108,"Hs"],[269,7.2502,110,"Ds"],[270,7.2538,110,"Ds"]];   // [A, B/A (MeV), Z, symbol] from AME2020 (mass_1.mas20)
  const B = {}; BA.forEach((d) => (B[d[0]] = d));
  const bOf = (A) => { if (B[A]) return B[A][1]; let lo = A, hi = A; while (lo > 1 && !B[lo]) lo--; while (hi < 300 && !B[hi]) hi++; return B[lo] && B[hi] ? lerp(B[lo][1], B[hi][1], (A - lo) / (hi - lo || 1)) : 0; };
  const nameOf = (A) => (B[A] ? `${B[A][3]}-${A}` : `A = ${A}`);

  WT.chapter("binding", {
    num: "Chapter 3", title: "Why nuclei hold together", short: "Binding",
    html: `
<div class="step">
  <p>Higher on the curve means more tightly bound.</p>
  <div class="ctl"><label for="bi-a">Mass number A</label><input id="bi-a" type="range" data-bind="pick" data-instant min="2" max="260" step="1" value="56"><output data-show="pick" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Split uranium: both pieces sit higher. About 200 MeV.</p>
  <div class="ctl"><label for="bi-f">Lighter fragment A</label><input id="bi-f" type="range" data-bind="frag" data-instant min="70" max="118" step="1" value="95"><output data-show="frag" data-fmt="0"></output></div>
</div>
<div class="step">
  <p>Fuse light nuclei: energy out only if the product sits higher.</p>
  <div class="ctl"><label for="bi-u">Each light nucleus A</label><input id="bi-u" type="range" data-bind="fuse" data-instant min="2" max="60" step="1" value="2"><output data-show="fuse" data-fmt="0"></output></div>
</div>`,
    setup(S) { S.set("mode", 0); S.set("pick", 56); S.set("frag", 95); S.set("fuse", 2); },
    steps: [(S) => S.set("mode", 0), (S) => S.set("mode", 1), (S) => S.set("mode", 2)],
    frame(g, S) {
      const { W, H, c, ctx } = g, phone = W < 600, fs = phone ? 11 : 13;
      const x0 = W * (phone ? 0.12 : 0.09), x1 = W * 0.96, y0 = H * (phone ? 0.14 : 0.08), y1 = H * (phone ? 0.7 : 0.72), BMIN = 0, BMAX = 9.8;
      const X = (a) => x0 + (x1 - x0) * a / 270, Y = (b) => lerp(y1, y0, (b - BMIN) / (BMAX - BMIN));
      // axes
      for (let b = 0; b <= 9; b += 3) { g.line(x0, Y(b), x1, Y(b), c.line, 1, 0.6, b ? [2, 5] : null); g.label(String(b), x0 - 7, Y(b), { color: c.faint, size: fs - 2, align: "right" }); }
      [0, 50, 100, 150, 200, 250].forEach((a) => g.label(String(a), X(a), y1 + 12, { color: c.faint, size: fs - 2 }));
      g.label("mass number A →", x1, y1 + 28, { color: c.soft, size: fs - 1, align: "right" });
      g.label(phone ? "binding per nucleon (MeV)" : "binding energy per nucleon (MeV)", x0, y0 - 12, { color: c.soft, size: fs - 1, align: "left" });
      // the curve: measured points as a lit ridge
      const pts = BA.map((d) => [X(d[0]), Y(d[1])]);
      g.ground(pts.filter((p, i) => BA[i][0] >= 12), c.fission, H * 0.12, 0.16);
      g.poly(pts.filter((p, i) => BA[i][0] >= 12), c.fission, 2, 0.8);
      BA.forEach((d, i) => { if (d[0] < 12) g.dot(pts[i][0], pts[i][1], 2.6, c.fission, 0.9); });
      // the most tightly bound measured nucleus (Ni-62), labelled above the curve so the slider's label below never covers it
      const top = BA.reduce((m, d) => (d[1] > m[1] ? d : m)), peak = Y(top[1]);
      g.glow(X(top[0]), peak, 30, c.fission, 0.3); g.dot(X(top[0]), peak, 3.5, c.fission, 1);
      g.label(`${top[3]}-${top[0]}: most tightly bound`, X(top[0]) + 12, peak - (phone ? 20 : 18), { color: c.fission, size: fs - 1, weight: 600, bg: true, align: "left" });
      g.label("measured masses (AME2020)", x1, Y(1.2), { color: c.faint, size: fs - 2, align: "right" });
      const marker = (a, col, lab, up) => { const b = bOf(a); g.glow(X(a), Y(b), 18, col, 0.4); g.ball(X(a), Y(b), 6, col); if (lab) g.label(lab, X(a), Y(b) + (up ? -18 : 18), { color: col, size: fs - 1, weight: 600, bg: true }); return b; };
      const ry = H * 0.92;
      if (S.mode === 0) {
        const a = Math.round(S.pick), b = marker(a, c.accent, nameOf(a), b0(a));
        g.label(`${nameOf(a)}: ${b.toFixed(3)} MeV per nucleon · ${(a * b).toFixed(0)} MeV in all`, W * 0.5, ry, { color: c.ink, size: fs + 2, weight: 600, serif: true });
      } else if (S.mode === 1) {
        const a1 = Math.round(S.frag), a2 = 236 - a1, bp = bOf(236), b1 = bOf(a1), b2 = bOf(a2), Q = a1 * b1 + a2 * b2 - 236 * bp;
        g.line(X(a1), Y(bp), X(236), Y(bp), c.faint, 1, 0.7, [3, 4]);
        [a1, a2].forEach((a) => g.arrow(X(a), Y(bp), X(a), Y(bOf(a)) + 8, c.warm, 2, 0.9));
        marker(236, c.proton, "U-236", true); marker(a1, c.warm, nameOf(a1), true); marker(a2, c.warm, nameOf(a2), true);
        g.label(`${nameOf(236)} → ${nameOf(a1)} + ${nameOf(a2)}: about ${Q.toFixed(0)} MeV released`, W * 0.5, ry, { color: Q > 0 ? c.ink : c.soft, size: fs + 2, weight: 600, serif: true });

      } else {
        const a1 = Math.round(S.fuse), a2 = 2 * a1, b1 = bOf(a1), b2 = bOf(a2), Q = a2 * b2 - a2 * b1;
        g.arrow(X(a1), Y(b1), X(a2) - 4, Y(b2) + (b2 >= b1 ? 6 : -6), Q > 0 ? c.warm : c.cool, 2, 0.9);
        marker(a1, c.accent, nameOf(a1), false); marker(a2, Q > 0 ? c.warm : c.cool, nameOf(a2), true);
        g.label(`${nameOf(a1)} + ${nameOf(a1)} → ${nameOf(a2)}: ${Q >= 0 ? "about " + Q.toFixed(1) + " MeV released" : "costs " + (-Q).toFixed(1) + " MeV"}`, W * 0.5, ry, { color: Q > 0 ? c.ink : c.cool, size: fs + 2, weight: 600, serif: true });
      }
    },
  });
  function b0(a) { return a < 30; }
})();
