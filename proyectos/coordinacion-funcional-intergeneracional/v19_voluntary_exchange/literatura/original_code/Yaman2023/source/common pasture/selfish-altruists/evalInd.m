function [fitness, phi, resourceTrend, roleTrend] = evalInd2(testEnv, self)


settings.T = 1000;
settings.nRun = 28;
settings.decay = 0.1;
settings.epsilon = 0.1;
settings.visualize = 0;
settings.self = self;

settings.greedyFarmerPayoff = 10;
settings.considerateFarmerPayoff = 5;
settings.upperBound = 100;

settings.naturalGrowth = testEnv(1)*0.5;
settings.workerGrowth = testEnv(2)*0.5;

nRun = settings.nRun;
phi = zeros(nRun, settings.T);
resourceTrend = zeros(nRun, settings.T);
%selection = cell(nRun, 1);
roleTrend = cell(nRun, 1);
% used = zeros(nRun, 4,4);

parfor i=1:nRun
    results = game(settings);
    phi(i,:) = results.phi;
    resourceTrend(i,:) = results.resourceTrend;
%     used(i,:) = results.used;
    %selection{i} = results.selection;
    roleTrend{i} = results.roleTrend;
end
mPhi = mean(phi);
fitness = mean(mPhi(end-100:end));