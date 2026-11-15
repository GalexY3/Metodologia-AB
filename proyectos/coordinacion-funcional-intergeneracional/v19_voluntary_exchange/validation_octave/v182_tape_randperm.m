function out = v182_tape_randperm(n)
  global V182_TAPE V182_COUNTERS;
  if n == 3
    ix = 1; table = V182_TAPE.p3;
  elseif n == 4
    ix = 2; table = V182_TAPE.p4;
  elseif n == 10
    ix = 3; table = V182_TAPE.p10;
  else
    error('Unexpected permutation length');
  end
  V182_COUNTERS(ix) = V182_COUNTERS(ix) + 1;
  out = double(table(V182_COUNTERS(ix), :)) + 1;
end
