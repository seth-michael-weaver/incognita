! Instrumentation for the physics.hf.preeq multiple pre-equilibrium acceptance test (task EXCL3).
! NOT part of TALYS. Compiled into a private copy of TALYS-2.x (MIT, (c) A.J. Koning) with the
! two one-line hooks in apply_hooks.sh. Writes only; never changes a TALYS variable, so the
! instrumented binary must reproduce the reference binE*.out / xs*.tot unchanged.
!
! mpdump_in  : everything multipreeq2.f90 reads, at entry (before its own sumfeed cut), plus a
!              snapshot of every xspopph2 row the routine can write, so mpdump_out can print
!              deltas instead of 2 x 7**4 x numex absolute values.
! mpdump_out : multipreeq2.f90's outputs, at the point where it has finished feeding and is about
!              to set Dmulti -- so xspopex(Zcomp,Ncomp,nex) is still the pre-depletion value.
!
! Every real field is preceded by 1x, because TALYS's es17.9e3 fields abut when the second is
! negative.
module mpdump_mod
  use A0_talys_mod
  implicit none
  real(sgl), save :: mother0(0:numparx, 0:numparx, 0:numparx, 0:numparx)
  real(sgl), save :: daughter0(2, 0:numex, 0:numparx, 0:numparx, 0:numparx, 0:numparx)
  integer, save   :: dZix(2), dNix(2)
  logical, save   :: dlive(2)
end module mpdump_mod

subroutine mpdump_in(Zcomp, Ncomp, nex)
  use A0_talys_mod
  use mpdump_mod
  implicit none
  integer :: Zcomp, Ncomp, nex, type, Zix, Nix, ipp, ihp, ipn, ihn, nexout, nen, J, NL
  real(sgl) :: sumfeed, Eex, dEx, Eo, Tswave, damp, dampo
  real(sgl) :: ignatyuk
  if (Zcomp == 0 .and. Ncomp == 0) return
  sumfeed = 0.
  do ipp = 0, maxpar
    do ihp = 0, maxpar
      do ipn = 0, maxpar
        do ihn = 0, maxpar
          sumfeed = sumfeed + xspopph2(Zcomp, Ncomp, nex, ipp, ihp, ipn, ihn)
        enddo
      enddo
    enddo
  enddo
  mother0 = xspopph2(Zcomp, Ncomp, nex, 0:numparx, 0:numparx, 0:numparx, 0:numparx)
  daughter0 = 0.
  dlive = .false.
  open (unit = 93, file = 'mp_inputs.txt', status = 'unknown', position = 'append')
  write(93, '("MPIN ", 4i6, 5(1x, es23.15e3))') nin, Zcomp, Ncomp, nex, Einc, Exinc, dExinc, &
 &  dble(xspopex(Zcomp, Ncomp, nex)), sumfeed
  damp = ignatyuk(Zcomp, Ncomp, Exinc, 0) / alev(Zcomp, Ncomp)
  write(93, '("MPSC ", 3i6, 2l2, 7(1x, es23.15e3))') maxpar, numparx, mpreeqmode, flaggshell, &
 &  flag2comp, gp(Zcomp, Ncomp), gn(Zcomp, Ncomp), alev(Zcomp, Ncomp), damp, Efermi, &
 &  gp(0, 0), gn(0, 0)
  do ipp = 0, maxpar
    do ihp = 0, maxpar
      do ipn = 0, maxpar
        do ihn = 0, maxpar
          if (xspopph2(Zcomp, Ncomp, nex, ipp, ihp, ipn, ihn) /= 0.) write(93, &
 &          '("MPPH ", 4i4, 1x, es23.15e3)') ipp, ihp, ipn, ihn, &
 &          xspopph2(Zcomp, Ncomp, nex, ipp, ihp, ipn, ihn)
        enddo
      enddo
    enddo
  enddo
  do J = 0, numJ
    if (RnJ(2, J) /= 0.) write(93, '("MPRJ ", i4, 2(1x, es23.15e3))') J, RnJ(2, J), RnJsum(2)
  enddo
  do type = 1, 2
    Zix = Zindex(Zcomp, Ncomp, type)
    Nix = Nindex(Zcomp, Ncomp, type)
    NL = Nlast(Zix, Nix, 0)
    write(93, '("MPTY ", 6i6, 1l2, 4(1x, es23.15e3))') type, Zix, Nix, NL, nexmax(type), &
 &    maxex(Zix, Nix), parskip(type), S(Zcomp, Ncomp, type), gp(Zix, Nix), gn(Zix, Nix), &
 &    alev(Zix, Nix)
    if (parskip(type)) cycle
    if (Zix > numZph .or. Nix > numNph) cycle
    dlive(type) = .true.
    dZix(type) = Zix
    dNix(type) = Nix
    daughter0(type, 0:numex, 0:numparx, 0:numparx, 0:numparx, 0:numparx) = &
 &    xspopph2(Zix, Nix, 0:numex, 0:numparx, 0:numparx, 0:numparx, 0:numparx)
    do nexout = NL + 1, nexmax(type)
      dEx = deltaEx(Zix, Nix, nexout)
      Eex = Ex(Zix, Nix, nexout)
      Eo = Exinc - Eex - S(Zcomp, Ncomp, type)
      call locate(egrid, ebegin(type), eend(type), Eo, nen)
      Tswave = Tjl(type, nen, 1, 0)
      dampo = ignatyuk(Zix, Nix, Eex, 0) / alev(Zix, Nix)
      write(93, '("MPBN ", 4i6, 5(1x, es23.15e3))') type, nexout, nen, maxJ(Zix, Nix, nexout), &
 &      Eex, dEx, Eo, Tswave, dampo
    enddo
  enddo
  write(93, '("MPEI ")')
  close (93)
end subroutine mpdump_in

subroutine mpdump_out(Zcomp, Ncomp, nex, summpe)
  use A0_talys_mod
  use mpdump_mod
  implicit none
  integer :: Zcomp, Ncomp, nex, type, Zix, Nix, ipp, ihp, ipn, ihn, nexout
  real(dbl) :: summpe
  real(sgl) :: d
  if (Zcomp == 0 .and. Ncomp == 0) return
  open (unit = 93, file = 'mp_inputs.txt', status = 'unknown', position = 'append')
  write(93, '("MPOU ", 3i6, 4(1x, es23.15e3))') Zcomp, Ncomp, nex, summpe, &
 &  dble(xspopex(Zcomp, Ncomp, nex)), dble(xsmpe(1, nex)), dble(xsmpe(2, nex))
  do type = 1, 2
    do nexout = 0, numex
      if (mpecontrib(type, nex, nexout) /= 0.) write(93, '("MPMC ", 2i6, 1x, es23.15e3)') &
 &      type, nexout, mpecontrib(type, nex, nexout)
    enddo
  enddo
  do ipp = 0, numparx
    do ihp = 0, numparx
      do ipn = 0, numparx
        do ihn = 0, numparx
          d = xspopph2(Zcomp, Ncomp, nex, ipp, ihp, ipn, ihn) - mother0(ipp, ihp, ipn, ihn)
          if (d /= 0.) write(93, '("MPDM ", 4i4, 1x, es23.15e3)') ipp, ihp, ipn, ihn, d
        enddo
      enddo
    enddo
  enddo
  do type = 1, 2
    if ( .not. dlive(type)) cycle
    Zix = dZix(type)
    Nix = dNix(type)
    do nexout = 0, numex
      do ipp = 0, numparx
        do ihp = 0, numparx
          do ipn = 0, numparx
            do ihn = 0, numparx
              d = xspopph2(Zix, Nix, nexout, ipp, ihp, ipn, ihn) - &
 &              daughter0(type, nexout, ipp, ihp, ipn, ihn)
              if (d /= 0.) write(93, '("MPDD ", 6i4, 1x, es23.15e3)') type, nexout, ipp, ihp, &
 &              ipn, ihn, d
            enddo
          enddo
        enddo
      enddo
    enddo
  enddo
  write(93, '("MPEO ")')
  close (93)
end subroutine mpdump_out
