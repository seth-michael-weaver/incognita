! Instrumentation for the physics.hf.compound acceptance tests (task T9).
! NOT part of TALYS. Compiled into a private copy of TALYS-2.x (MIT, (c) A.J. Koning) with the
! three one-line hooks in comptarget.patch. Writes only; never changes a TALYS variable, and
! cn_reference.py verifies the instrumented run reproduces the reference binE*.out byte for byte.
subroutine cndump_inputs
  use A0_talys_mod
  implicit none
  integer :: type, Zix, Nix, nexout, l, ud, Ir, P, irad, NL, im
  open (unit = 97, file = 'cn_inputs.txt', status = 'unknown', position = 'append')
  write(97, '("EINC ", es17.9e3)') Einc
  write(97, '("SCAL ", 6es17.9e3)') CNfactor, xsflux, xsreacinc, Exinc, dExinc, targetspin
  write(97, '("INTS ", 12i6)') J2beg, J2end, targetspin2, targetP, lmaxinc, k0, Ltarget, wmode, WFCfactor, gammax, nmold, &
 &  nfisbar(0, 0)
  write(97, '("FLAG ", 5l2)') flagwidth, flagfission, flagcompang, flagurr, flagastro
  write(97, '("FNRM ", 8es17.9e3)') (Fnorm(type), type = -1, 6)
  write(97, '("MOLD ", 64es17.9e3)') (xmold(im), im = 1, nummold), (wmold(im), im = 1, nummold)
  do l = 0, lmaxinc
    write(97, '("TINC ", i4, 3es17.9e3)') l, (Tjlinc(ud, l), ud = -1, 1)
  enddo
  write(97, '("SCL2 ", es17.9e3, l2)') popeps, flagpreeq
  do type = 0, 6
    if (parskip(type)) cycle
    Zix = Zindex(0, 0, type)
    Nix = Nindex(0, 0, type)
    NL = Nlast(Zix, Nix, 0)
    write(97, '("TYPE ", 6i6, 2es17.9e3)') type, Zix, Nix, maxex(Zix, Nix), NL, spin2(type), parspin(type), S(0, 0, type)
    do nexout = 0, min(NL, numlev2)
      if (xsdirdisc(type, nexout) /= 0.) write(97, '("XSDD ", 2i6, es17.9e3)') type, nexout, xsdirdisc(type, nexout)
    enddo
    if (flagpreeq) then
      do nexout = NL + 1, maxex(Zix, Nix)
        if (preeqpopex(Zix, Nix, nexout) /= 0.) write(97, '("PEPX ", 2i6, es17.9e3)') type, nexout, &
 &        preeqpopex(Zix, Nix, nexout)
      enddo
    endif
    do nexout = 0, maxex(Zix, Nix)
      write(97, '("NEX  ", 4i6, 3es17.9e3)') type, nexout, lmaxhf(type, nexout), maxJ(Zix, Nix, nexout), &
 &      Ex(Zix, Nix, nexout), deltaEx(Zix, Nix, nexout), real(jdis(Zix, Nix, min(nexout, numlev2)))
      if (nexout <= NL) write(97, '("LEV  ", 3i6)') type, nexout, parlev(Zix, Nix, nexout)
      do P = -1, 1, 2
        do Ir = 0, numJ
          if (rho0(Ir, P, type, nexout) /= 0.) write(97, '("RHO  ", 4i6, es24.16e3)') type, nexout, Ir, P, &
 &          rho0(Ir, P, type, nexout)
        enddo
      enddo
      if (type == 0) then
        do l = 1, gammax
          do irad = 0, 1
            write(97, '("TGAM ", 4i6, 82es17.9e3)') type, nexout, l, irad, &
 &            ((Tgam(l, nexout, irad, Ir, P), Ir = 0, numJ), P = -1, 1, 2)
          enddo
        enddo
      else
        do l = 0, lmaxhf(type, nexout)
          write(97, '("TJL  ", 3i6, 3es17.9e3)') type, nexout, l, (Tjlnex(l, ud, type, nexout), ud = -1, 1)
        enddo
      endif
    enddo
  enddo
  close (97)
end subroutine cndump_inputs

subroutine cndump_jp(J2, parity)
  use A0_talys_mod
  implicit none
  integer :: J2, parity, J, ih
  J = J2 / 2
  open (unit = 97, file = 'cn_inputs.txt', status = 'unknown', position = 'append')
  write(97, '("JP   ", 3i6, es24.16e3)') J2, parity, tnum, denomhf
  if (flagfission .and. nfisbar(0, 0) /= 0) then
    write(97, '("TFIS ", 2i6, es24.16e3)') J2, parity, tfis(J, parity)
    do ih = 0, numhill
      write(97, '("TFHA ", 3i6, 2es24.16e3)') J2, parity, ih, tfisA(J, parity, ih), rhofisA(J, parity, ih)
    enddo
  endif
  close (97)
end subroutine cndump_jp

subroutine cndump_pop
  use A0_talys_mod
  implicit none
  integer :: type, Zix, Nix, nexout, Ir, P
  open (unit = 97, file = 'cn_inputs.txt', status = 'unknown', position = 'append')
  write(97, '("XSBI ", 8es24.16e3)') (xsbinary(type), type = -1, 6)
  do type = 0, 6
    if (parskip(type)) cycle
    Zix = Zindex(0, 0, type)
    Nix = Nindex(0, 0, type)
    do nexout = 0, maxex(Zix, Nix)
      do P = -1, 1, 2
        do Ir = 0, numJ
          if (xspop(Zix, Nix, nexout, Ir, P) /= 0.) write(97, '("POP  ", 4i6, es24.16e3)') type, nexout, Ir, P, &
 &          xspop(Zix, Nix, nexout, Ir, P)
        enddo
      enddo
    enddo
  enddo
  write(97, '("END  ")')
  close (97)
end subroutine cndump_pop

! ---- continuum (multiple emission) decay: compound.f90 inputs and daughter increments -------------
! Written only for the residual nucleus named by the environment variable CNDUMP_ZN="Zcomp Ncomp"
! (index form, e.g. "0 1" = target after neutron emission), for every mother bin at every energy.
module cndump_multi_state
  use A0_talys_mod, only: dbl   ! NOT A0_kinds_mod: both declare `dbl`, and using both makes it ambiguous
  implicit none
  real(dbl), allocatable, save :: snap(:, :, :, :)   ! (type 0:6, nexout, J, parity) xspop before
  integer, save :: selZ = -1, selN = -1
  logical, save :: init = .false.
end module cndump_multi_state

logical function cnmulti_selected(Zcomp, Ncomp)
  use cndump_multi_state
  implicit none
  integer :: Zcomp, Ncomp, st
  character(len=32) :: v
  if (.not. init) then
    call get_environment_variable('CNDUMP_ZN', v, status=st)
    if (st == 0) read(v, *) selZ, selN
    init = .true.
  endif
  cnmulti_selected = (Zcomp == selZ .and. Ncomp == selN)
end function cnmulti_selected

subroutine cnmulti_inputs(Zcomp, Ncomp, nex, popepsA, odd)
  use A0_talys_mod
  use cndump_multi_state
  implicit none
  integer :: Zcomp, Ncomp, nex, odd, type, Zix, Nix, nexout, l, ud, Ir, P, irad, NL, J
  real(sgl) :: popepsA
  logical :: cnmulti_selected
  if (.not. cnmulti_selected(Zcomp, Ncomp)) return
  if (.not. allocated(snap)) allocate(snap(0:6, 0:numex, 0:numJ, -1:1))
  snap = 0.
  open (unit = 97, file = 'cn_multi.txt', status = 'unknown', position = 'append')
  write(97, '("MBIN ", 4i6, 6es17.9e3, l2)') Zcomp, Ncomp, nex, odd, Einc, Exinc, dExinc, Exmax(Zcomp, Ncomp), &
 &  popepsA, Dmulti(nex), flagfullhf
  write(97, '("MINT ", 5i6, l2)') maxJ(Zcomp, Ncomp, nex), gammax, Nlast(Zcomp, Ncomp, 0), nfisbar(Zcomp, Ncomp), numJ, &
 &  flagfission
  do P = -1, 1, 2
    do J = 0, numJ
      if (xspop(Zcomp, Ncomp, nex, J, P) /= 0.) write(97, '("MPOP ", 2i6, es24.16e3)') J, P, xspop(Zcomp, Ncomp, nex, J, P)
    enddo
  enddo
  do type = 0, 6
    if (parskip(type)) cycle
    Zix = Zindex(Zcomp, Ncomp, type)
    Nix = Nindex(Zcomp, Ncomp, type)
    NL = Nlast(Zix, Nix, 0)
    write(97, '("TYPE ", 6i6, 2es17.9e3)') type, Zix, Nix, nexmax(type), NL, spin2(type), parspin(type), S(Zcomp, Ncomp, type)
    do nexout = 0, nexmax(type)
      snap(type, nexout, :, :) = xspop(Zix, Nix, nexout, :, :)
      write(97, '("NEX  ", 4i6, 3es17.9e3)') type, nexout, lmaxhf(type, nexout), maxJ(Zix, Nix, nexout), &
 &      Ex(Zix, Nix, nexout), deltaEx(Zix, Nix, nexout), real(jdis(Zix, Nix, min(nexout, numlev2)))
      if (nexout <= NL) write(97, '("LEV  ", 3i6)') type, nexout, parlev(Zix, Nix, nexout)
      do P = -1, 1, 2
        do Ir = 0, numJ
          if (rho0(Ir, P, type, nexout) /= 0.) write(97, '("RHO  ", 4i6, es24.16e3)') type, nexout, Ir, P, &
 &          rho0(Ir, P, type, nexout)
        enddo
      enddo
      if (type == 0) then
        do l = 1, gammax
          do irad = 0, 1
            write(97, '("TGAM ", 4i6, 82es17.9e3)') type, nexout, l, irad, &
 &            ((Tgam(l, nexout, irad, Ir, P), Ir = 0, numJ), P = -1, 1, 2)
          enddo
        enddo
      else
        do l = 0, lmaxhf(type, nexout)
          write(97, '("TL   ", 3i6, 4es17.9e3)') type, nexout, l, Tlnex(l, type, nexout), &
 &          (Tjlnex(l, ud, type, nexout), ud = -1, 1)
        enddo
      endif
    enddo
  enddo
  close (97)
end subroutine cnmulti_inputs

subroutine cnmulti_jp(Zcomp, Ncomp, J2, parity)
  use A0_talys_mod
  implicit none
  integer :: Zcomp, Ncomp, J2, parity, J
  logical :: cnmulti_selected
  if (.not. cnmulti_selected(Zcomp, Ncomp)) return
  J = J2 / 2
  open (unit = 97, file = 'cn_multi.txt', status = 'unknown', position = 'append')
  write(97, '("MJP  ", 2i6, es24.16e3)') J2, parity, denomhf
  if (flagfission .and. nfisbar(Zcomp, Ncomp) /= 0) write(97, '("MFIS ", 2i6, 3es24.16e3)') J2, parity, &
 &  tfisdown(J, parity), tfis(J, parity), tfisup(J, parity)
  close (97)
end subroutine cnmulti_jp

subroutine cnmulti_pop(Zcomp, Ncomp, nex)
  use A0_talys_mod
  use cndump_multi_state
  implicit none
  integer :: Zcomp, Ncomp, nex, type, Zix, Nix, nexout, Ir, P
  real(dbl) :: d
  logical :: cnmulti_selected
  if (.not. cnmulti_selected(Zcomp, Ncomp)) return
  open (unit = 97, file = 'cn_multi.txt', status = 'unknown', position = 'append')
  do type = 0, 6
    if (parskip(type)) cycle
    Zix = Zindex(Zcomp, Ncomp, type)
    Nix = Nindex(Zcomp, Ncomp, type)
    do nexout = 0, nexmax(type)
      do P = -1, 1, 2
        do Ir = 0, numJ
          d = xspop(Zix, Nix, nexout, Ir, P) - snap(type, nexout, Ir, P)
          if (d /= 0.) write(97, '("DPOP ", 4i6, es24.16e3)') type, nexout, Ir, P, d
        enddo
      enddo
    enddo
  enddo
  write(97, '("MEND ", 3i6)') Zcomp, Ncomp, nex
  close (97)
end subroutine cnmulti_pop
