function v182_run_original(base)
  root = fullfile(base, 'literatura', 'original_code', 'Yaman2023', 'source');
  out = fullfile(base, 'results', 'V182_OCTAVE_VALIDATION');
  addpath(fullfile(base, 'validation_octave'));
  addpath(fullfile(out, 'instrumented_source'));
  fixtures = dir(fullfile(out, 'fixture_*.mat'));
  global V182_TAPE V182_COUNTERS;
  for k = 1:length(fixtures)
    f = load(fullfile(out, fixtures(k).name));
    V182_TAPE = f;
    V182_COUNTERS = zeros(1, 4);
    settings.T = double(f.T); settings.alpha = .1;
    settings.epsilon = 0; settings.visualize = 0;
    if f.game == 0
      settings.socialNorm = reshape(f.matrix, 1, []);
      settings.wasteBaseline = 0; settings.wasteMax = f.env(1)*6;
      settings.wasteIncrease = settings.wasteMax/10;
      settings.advAttackProb = f.env(2);
      results = v182_replay_settlement(settings);
    else
      settings.genotype = reshape(f.matrix, 1, []);
      settings.naturalGrowth = f.env(1)*.5;
      settings.workerGrowth = f.env(2)*.5;
      settings.greedyFarmerPayoff = 10;
      settings.considerateFarmerPayoff = 5; settings.upperBound = 100;
      results = v182_replay_pasture(settings);
    end
    counters = V182_COUNTERS;
    save('-mat7-binary', fullfile(out, ['output_' fixtures(k).name]), 'results', 'counters');
    fprintf('ORIGINAL_REPLAY %s counters=%s\n', fixtures(k).name, mat2str(counters));
    fflush(stdout);
  end
  % Execute unmodified archived pasture functions, without launching 30 workers.
  addpath(fullfile(root, 'common pasture'));
  clear settings;
  settings.T = 110; settings.alpha = .1; settings.epsilon = 0;
  settings.visualize = 0; settings.greedyFarmerPayoff = 10;
  settings.considerateFarmerPayoff = 5; settings.upperBound = 100;
  settings.naturalGrowth = .5; settings.workerGrowth = .5;
  settings.genotype = zeros(1,9); settings.socialNorm = zeros(1,9);
  rng(182115); first = game_pasture(settings);
  settings.socialNorm = [-2 0 .5 0 1 0 0 0 0];
  rng(182115); ignored = game_pasture(settings);
  wiring_same_phi = isequal(first.phi, ignored.phi);
  wiring_same_roles = isequal(first.roleTrend, ignored.roleTrend);
  settings.genotype = settings.socialNorm;
  rng(182115); changed = game_pasture(settings);
  wiring_genotype_changes_phi = ~isequal(first.phi, changed.phi);
  % A negative rule actually used exposes signed-count versus L0 fitness.
  settings.env = [1 1]; settings.nRun = 1;
  settings.complexityRegularizationParameter = .2;
  settings.genotype = [0 0 -1 0 0 0 0 0 0];
  rng(182116);
  [fitness, phi, scores, resourceTrend, roleTrend, selection, npun, nrew, matrix, used] = evalIndGAP(settings);
  tail = mean(mean(phi(:, end-100:end)));
  l0_expected = tail - .2*sum(sum(matrix ~= 0));
  signed_expected = tail - .2*sum(sum(sign(matrix)));
  raw_fitness = fitness;
  octave_version = version;
  save('-mat7-binary', fullfile(out, 'original_wiring_and_regularizer.mat'),
       'wiring_same_phi', 'wiring_same_roles', 'wiring_genotype_changes_phi',
       'raw_fitness', 'l0_expected', 'signed_expected', 'matrix', 'used', 'npun',
       'octave_version');
  fprintf('ORIGINAL_WIRING same_phi=%d same_roles=%d genotype_changes=%d\n', wiring_same_phi, wiring_same_roles, wiring_genotype_changes_phi);
  fprintf('ORIGINAL_REGULARIZER actual=%.15g l0=%.15g signed=%.15g\n', raw_fitness, l0_expected, signed_expected);
end
