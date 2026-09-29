! Instrumentation for the physics.hf.emission acceptance test A-mult (task T10).
! NOT part of TALYS. Compiled into a private copy of TALYS-2.x (MIT, (c) A.J. Koning) with the
! two one-line hooks in apply_hooks.sh. Writes only; never changes a TALYS variable, so the
! instrumented binary must reproduce the reference xs*.tot / rp*.tot / binE*.out unchanged.
!
! chdump_binary   : everything binary.f90 reads, at entry to binary.f90 (before it adds the
!                   direct and pre-equilibrium addends to the compound population).
! chdump_channels : everything channels.f90 / totalxs.f90 / residual.f90 read, at the moment
!                   talysreaction.f90 calls channels.
!
! Every real field is preceded by 1x. TALYS's own es17.9e3 fields abut when the second is
! negative (T9 hit this); an explicit separator makes whitespace splitting safe.
subroutine chdump_binary
  use A0_talys_mod
  implicit none
  integer :: type, Zix, Nix, nex, NL, J, P, nmax
  real(sgl) :: ald, Eex, sc
  real(sgl) :: ignatyuk, spincut
  open (unit = 95, file = 'bin_inputs.txt', status = 'unknown', position = 'append')
  write(95, '("EINC ", i6, 1x, es23.15e3)') nin, Einc
  write(95, '("INTS ", 8i6)') k0, Ltarget, targetspin2, targetP, pespinmodel, maxJph, numJ, Ninclow
  write(95, '("FLAG ", 4l2)') flagpreeq, flagfission, flagracap, flaginitpop
  write(95, '("SCAL ", 9(1x, es23.15e3))') popeps, xseps, xsreacinc, xselasinc, xsdirdiscsum, &
 &  xspreeqsum, xsgrsum, xsracape, pardis
  write(95, '("XSBI ", 8(1x, es23.15e3))') (xsbinary(type), type = -1, 6)
  do type = 0, 6
    if (parskip(type)) cycle
    Zix = Zindex(0, 0, type)
    Nix = Nindex(0, 0, type)
    NL = Nlast(Zix, Nix, 0)
    nmax = maxex(Zix, Nix)
    write(95, '("TYPE ", 5i6, 5(1x, es23.15e3))') type, Zix, Nix, nmax, NL, &
 &    xsdirdisctot(type), xspreeqtot(type), xsgrtot(type), xscompcont(type), dble(xspopnuc(Zix, Nix))
    do nex = 0, nmax
      Eex = Ex(Zix, Nix, nex)
      if (nex > NL) then
        ald = ignatyuk(Zix, Nix, Eex, 0)
        sc = spincut(Zix, Nix, ald, Eex, 0, 0)
      else
        ald = 0.
        sc = 0.
      endif
      write(95, '("NEX  ", 3i6, 6(1x, es23.15e3))') type, nex, maxJ(Zix, Nix, nex), Eex, &
 &      deltaEx(Zix, Nix, nex), dble(xspopex(Zix, Nix, nex)), preeqpopex(Zix, Nix, nex), ald, sc
      if (nex <= min(NL, numlev2)) write(95, '("LEV  ", 3i6, 2(1x, es23.15e3))') type, nex, &
 &      parlev(Zix, Nix, nex), jdis(Zix, Nix, nex), xsdirdisc(type, nex)
      do P = -1, 1, 2
        do J = 0, numJ
          if (xspop(Zix, Nix, nex, J, P) /= 0.) write(95, '("POP  ", 4i6, 1x, es23.15e3)') &
 &          type, nex, J, P, xspop(Zix, Nix, nex, J, P)
        enddo
      enddo
    enddo
  enddo
  write(95, '("END  ")')
  close (95)
end subroutine chdump_binary

subroutine chdump_channels
  use A0_talys_mod
  implicit none
  integer :: Zcomp, Ncomp, Zix, Nix, type, nex, nexout, Z, N, A, nmax
  integer :: in, ip, id, it, ih, ia
  real(sgl) :: f
  open (unit = 96, file = 'ch_inputs.txt', status = 'unknown', position = 'append')
  write(96, '("EINC ", i6, 1x, es23.15e3)') nin, Einc
  write(96, '("GLOB ", 8i6, 5(1x, es23.15e3))') k0, Ltarget, maxZ, maxN, Zinit, Ninit, maxchannel, &
 &  Ninclow, xseps, targetE, specmass(parZ(k0), parN(k0), k0), xsreacinc, xsnonel
  write(96, '("FLAG ", 3l2)') flagfission, flaginitpop, flagchannels
  write(96, '("PINC ", 8l2)') (parinclude(type), type = -1, 6)
  write(96, '("PSKP ", 7l2)') (parskip(type), type = 0, 6)
  write(96, '("BIN  ", 8(1x, es23.15e3))') (xsbinary(type), type = -1, 6)
  do in = 0, numin
  do ip = 0, numip
  do id = 0, numid
  do it = 0, numit
  do ih = 0, numih
  do ia = 0, numia
    if (chanopen(in, ip, id, it, ih, ia)) write(96, '("COPN ", 6i4)') in, ip, id, it, ih, ia
  enddo
  enddo
  enddo
  enddo
  enddo
  enddo
  if (idnumfull) write(96, '("FULL ")')
  do Zcomp = 0, maxZ
    do Ncomp = 0, maxN
      Z = ZZ(Zcomp, Ncomp, 0)
      N = NN(Zcomp, Ncomp, 0)
      A = AA(Zcomp, Ncomp, 0)
      write(96, '("NUC  ", 7i6, 4(1x, es23.15e3))') Zcomp, Ncomp, Z, N, A, maxex(Zcomp, Ncomp), &
 &      Nlast(Zcomp, Ncomp, 0), xspopnuc(Zcomp, Ncomp), Qres(Zcomp, Ncomp, 0), &
 &      dble(xsgamdistot(Zcomp, Ncomp)), dble(skipCN(Zcomp, Ncomp))
      do nex = 0, min(Nlast(Zcomp, Ncomp, 0), numlev2)
        write(96, '("LEV  ", 3i6, 2(1x, es23.15e3))') Zcomp, Ncomp, nex, edis(Zcomp, Ncomp, nex), &
 &        tau(Zcomp, Ncomp, nex)
      enddo
      do type = -1, 6
        if (type >= 0) then
          if (parskip(type)) cycle
        endif
        f = xsfeed(Zcomp, Ncomp, type)
        if (f /= 0.) write(96, '("XFD  ", 3i6, 1x, es23.15e3)') Zcomp, Ncomp, type, f
      enddo
      do type = 0, 6
        if (parskip(type)) cycle
        write(96, '("SEP  ", 5i6, 1x, es23.15e3)') Zcomp, Ncomp, type, Zindex(Zcomp, Ncomp, type), &
 &        Nindex(Zcomp, Ncomp, type), S(Zcomp, Ncomp, type)
      enddo
      nmax = min(maxex(Zcomp, Ncomp) + 1, numex + 1)
      do nex = 0, nmax
        if (popexcl(Zcomp, Ncomp, nex) /= 0. .or. fisfeedex(Zcomp, Ncomp, nex) /= 0.) &
 &        write(96, '("PEX  ", 3i6, 2(1x, es23.15e3))') Zcomp, Ncomp, nex, &
 &        popexcl(Zcomp, Ncomp, nex), fisfeedex(Zcomp, Ncomp, nex)
      enddo
      do nex = 0, min(maxex(Zcomp, Ncomp), numex)
        if (xspopex(Zcomp, Ncomp, nex) /= 0.) write(96, '("PXE  ", 3i6, 1x, es23.15e3)') &
 &        Zcomp, Ncomp, nex, xspopex(Zcomp, Ncomp, nex)
      enddo
      if (Zcomp > numZchan .or. Ncomp > numNchan) cycle
      do type = 0, 6
        if (parskip(type)) cycle
        Zix = Zindex(Zcomp, Ncomp, type)
        Nix = Nindex(Zcomp, Ncomp, type)
        do nex = 0, nmax
          do nexout = 0, min(maxex(Zix, Nix), numex)
            if (feedexcl(Zcomp, Ncomp, type, nex, nexout) /= 0.) &
 &            write(96, '("FEED ", 5i6, 1x, es23.15e3)') Zcomp, Ncomp, type, nex, nexout, &
 &            feedexcl(Zcomp, Ncomp, type, nex, nexout)
          enddo
        enddo
      enddo
    enddo
  enddo
  write(96, '("END  ")')
  close (96)
end subroutine chdump_channels
