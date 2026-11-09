#!/bin/bash
# GAP isomeric targets: stock TALYS-2.25 runs, one at a time, trimmed (docs/hf/ISOMERIC_TARGETS.md)
set -u
B=~/kwcov/stock/biso
mkdir -p $B
run() {  # name, deck lines (\n separated), energies
  local name=$1 deck=$2 en=$3
  local d=$B/$name
  if [ -f $d/DONE ]; then echo "skip $name"; return; fi
  rm -rf $d; mkdir -p $d; cd $d
  printf "%b\n" "$deck" > talys.inp
  printf "%b\n" "$en" > energies; echo "energy energies" >> talys.inp
  while [ $(free -g | awk '/Mem:/{print $7}') -lt 8 ]; do sleep 30; done
  /usr/bin/time -f "%e s %M KB" flock /tmp/incognita_heavy.lock nice -n 10 ~/opt/talys-src/bin/talys < talys.inp > talys.out 2> time.txt
  grep -i "error" talys.out | head -5 > errors.txt
  mkdir keep; mv talys.inp time.txt errors.txt energies keep/
  mv *.tot *.L[0-9][0-9] keep/ 2>/dev/null
  rm -f keep/sp*.tot keep/*spec*.tot
  awk '/Summary of target/{f=1} f{print; n++} n>12{exit}' talys.out > keep/target_out.txt
  grep -n "Excited target level" -A2 talys.out > keep/isomer_lines.txt
  grep -n "Binary non-elastic" -A14 talys.out > keep/binary_out.txt
  find . -maxdepth 1 -type f -delete
  mv keep/* .; rmdir keep
  touch DONE
  echo "done $name $(tail -1 time.txt) $(ls | wc -l) files $(du -sh . | cut -f1)"
}
H="projectile n\nchannels y\nfilechannels y\nfileresidual y\noutdiscrete y"
run fe56_gs  "$H\nelement fe\nmass 56" "1.\n5.\n14."
run fe56_l1  "$H\nelement fe\nmass 56\nltarget 1" "1.\n5.\n14."
run fe56_l2  "$H\nelement fe\nmass 56\nltarget 2" "1.\n5.\n14."
run am242_gs "$H\nelement am\nmass 242" "1.\n5.\n14."
run am242_m  "$H\nelement am\nmass 242\nltarget 2" "1.\n5.\n14."
# Hf-178m2 (level 109) is out of stock range: numlev = 40, "maxlevelstar = 109, Range 0 <= maxlevelstar <= 40"
echo ALLDONE
