function [fitness, phi, wasteTrend, advTrend, roleTrend] = evalIndCentralized(settings)



nRun = settings.nRun;
phi = zeros(nRun, settings.T);
wasteTrend = zeros(nRun, settings.T);
advTrend = zeros(nRun, settings.T);
roleTrend = cell(1,nRun);

for i=1:nRun
    results = gameCentralized(settings);
    phi(i,:) = results.phi;
    wasteTrend(i,:) = results.wasteTrend;
    advTrend(i,:) = results.advTrend;
    roleTrend{i} = results.roleTrend;
end
if(nRun == 1)
    mPhi = phi;
else
    mPhi = mean(phi);
end
fitness = mean(mPhi(end-100:end));