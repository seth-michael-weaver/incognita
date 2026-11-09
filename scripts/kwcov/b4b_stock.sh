#!/bin/bash
# B4b stock TALYS-2.25 runs, one at a time, trimmed
set -u
B=~/kwcov/stock/b4b
mkdir -p $B
run() {  # name, deck lines (\n separated), energies
  local name=$1 deck=$2 en=$3
  local d=$B/$name
  if [ -f $d/DONE ]; then echo "skip $name"; return; fi
  rm -rf $d; mkdir -p $d; cd $d
  printf "%b\n" "$deck" > talys.inp
  if [ -n "$en" ]; then printf "%b\n" "$en" > energies; echo "energy energies" >> talys.inp; fi
  while [ $(free -g | awk '/Mem:/{print $7}') -lt 8 ]; do sleep 30; done
  /usr/bin/time -f "%e s %M KB" flock /tmp/incognita_heavy.lock nice -n 10 ~/opt/talys-src/bin/talys < talys.inp > talys.out 2> time.txt
  grep -i "error" talys.out | head -5 > errors.txt
  # trim: keep sp*, xs*.tot, rp*.tot, binary.tot, *spec*.tot, talys.inp, energies, a gz of talys.out section 6b
  mkdir keep; mv talys.inp time.txt errors.txt keep/; [ -f energies ] && mv energies keep/
  mv sp* xs*.tot rp*.tot binary.tot nspec*.tot pspec*.tot gspec*.tot nn.tot np.tot nprod.tot keep/ 2>/dev/null
  awk '/6b. Exclusive spectra/{f=1} /6b2|7\. /{if(f)exit} f' talys.out | gzip > keep/excl_spectra.out.gz
  grep -n "Binary non-elastic" -A12 talys.out > keep/binary_out.txt
  find . -maxdepth 1 -type f -delete
  mv keep/* .; rmdir keep
  touch DONE
  echo "done $name $(cat time.txt | tail -1) $(ls | wc -l) files $(du -sh . | cut -f1)"
}
run fe56 "projectile n\nelement fe\nmass 56\nchannels y\nfilechannels y\noutspectra y\ncomponents y" "5.\n14."
run co59 "projectile n\nelement co\nmass 59\nchannels y\nfilechannels y\noutspectra y\ncomponents y" "14."
run fe56_endf "projectile n\nelement fe\nmass 56\nenergy 14\nendf y\nchannels y\nfilechannels y\noutspectra y" ""
run fe56_maxch2 "projectile n\nelement fe\nmass 56\nenergy 14\nmaxchannel 2\nchannels y\nfilechannels y\noutspectra y" ""
run u238 "projectile n\nelement u\nmass 238\nchannels y\nfilechannels y\noutspectra y\ncomponents y" "5.\n14."
echo ALLDONE
