function [fitness, phi, scores, wasteTrend, advTrend, roleTrend, selection, nPunishments, nRewards, socialSanctioningMatrix, usedRules] = evalIndGAS(settings)

settings.wasteMax = settings.env(1)*6;
settings.advAttackProb = settings.env(2);
settings.wasteIncrease = settings.wasteMax/10;

nRun = settings.nRun;
phi = zeros(nRun, settings.T);
wasteTrend = zeros(nRun, settings.T);
advTrend = zeros(nRun, settings.T);
roleTrend = cell(1, nRun);
nPunishments = zeros(1,nRun);
nRewards = zeros(1,nRun);
selection = cell(1,nRun);
usedRules = cell(1,nRun);
averageUsedRules = zeros(4,4);
mxFitness = -inf;
for i=1:nRun
    results = game_settlement(settings);
    phi(i,:) = results.phi;
    wasteTrend(i,:) = results.wasteTrend;
    advTrend(i,:) = results.advTrend;
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
if(size(phi,1)>1)
    mPhi = mean(phi);
else
    mPhi = phi;
end
scores = mean(phi(:,end-100,end),2);
fitness = mean(mPhi(end-100:end)) - settings.complexityRegularizationParameter*sum(sum(sign(abs(socialSanctioningMatrix))));