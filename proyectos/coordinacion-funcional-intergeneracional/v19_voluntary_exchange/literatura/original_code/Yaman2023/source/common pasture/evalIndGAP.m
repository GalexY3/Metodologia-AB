function [fitness, phi, scores, resourceTrend, roleTrend, selection, nPunishments, nRewards, socialSanctioningMatrix, usedRules] = evalIndGAP(settings)


settings.naturalGrowth = settings.env(1)*0.5;
settings.workerGrowth = settings.env(2)*0.5;


nRun = settings.nRun;
phi = zeros(nRun, settings.T);
resourceTrend = zeros(nRun, settings.T);
roleTrend = cell(nRun);
nPunishments = zeros(1,nRun);
nRewards = zeros(1,nRun);
selection = cell(1,nRun);
usedRules = cell(1,nRun);
mxFitness = -inf;
averageUsedRules = zeros(3,3);
for i=1:nRun
    results = game_pasture(settings);
    phi(i,:) = results.phi;
    resourceTrend(i,:) = results.resourceTrend;
    roleTrend{i} = results.roleTrend;
    usedRules{i} = results.used;
    averageUsedRules = averageUsedRules + results.used;
    nPunishments(i) = results.nPun;
    nRewards(i) = results.nRew;
    selection{i} = results.selection;
    if(mean(phi(i,end-100:end))>mxFitness)
        mxFitness = mean(phi(i,end-100:end));
    end
end

results.averageUsedRules = averageUsedRules./nRun;
results.socialSanctioningMatrix = results.socialSanctioningMatrix.*sign(averageUsedRules);
socialSanctioningMatrix = results.socialSanctioningMatrix;

if(nRun>1)
    mPhi = mean(phi);
else
    mPhi = (phi);
end
scores = mean(phi(:,end-100,end),2);
fitness = mean(mPhi(end-100:end))- settings.complexityRegularizationParameter*sum(sum(sign(socialSanctioningMatrix)));