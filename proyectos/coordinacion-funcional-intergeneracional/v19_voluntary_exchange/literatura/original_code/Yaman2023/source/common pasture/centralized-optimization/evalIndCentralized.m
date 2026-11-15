function [fitness, phi, resourceTrend, roleTrend] = evalIndCentralized(settings)

nRun = settings.nRun;
phi = zeros(nRun, settings.T);
resourceTrend = zeros(nRun, settings.T);
roleTrend = cell(nRun);

for i=1:nRun
    results = gameCentralized(settings);
    phi(i,:) = results.phi;
    resourceTrend(i,:) = results.resourceTrend;
    roleTrend{i} = results.roleTrend;
end
mPhi = mean(phi);
fitness = mean(mPhi(end-100:end));