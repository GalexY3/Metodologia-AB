function [fitness, phi, used, wasteTrend, advTrend, roleTrend] = evalInd(env, self)


settings.T = 1000;
settings.nRun = 12;
settings.decay = 0.1;
settings.epsilon = 0.1;
settings.selfPunishment = 0;
settings.visualize = 0;
settings.advAttackProb = env(2);
settings.livingCost = 0;
settings.self = self;

settings.wasteBaseline = 0;
settings.dirtMax = env(1)*6;
settings.wasteIncrease = settings.dirtMax/10;

nRun = settings.nRun;
phi = zeros(nRun, settings.T);
wasteTrend = zeros(nRun, settings.T);
advTrend = zeros(nRun, settings.T);
roleTrend = cell(1, nRun);
used = zeros(nRun, 4,4);
parfor i=1:nRun
    results = game(settings);
    phi(i,:) = results.phi;
    wasteTrend(i,:) = results.wasteTrend;
    advTrend(i,:) = results.advTrend;
    roleTrend{i} = results.roleTrend;
    used(i,:,:) = results.used;
end
mPhi = mean(phi);
fitness = mean(mPhi(end-100:end));