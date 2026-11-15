function out = v182_tape_rand()
  global V182_TAPE V182_COUNTERS;
  V182_COUNTERS(4) = V182_COUNTERS(4) + 1;
  out = V182_TAPE.uniforms(V182_COUNTERS(4));
end
