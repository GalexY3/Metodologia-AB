%load('resGAS_1_cost0.2.mat')

sanction2string

%figure
hold on
j=1;


settings = results{si(1,j),j}.settings;
settings.socialNorm = reshape(results{si(1,j),j}.bestInd.socialSanctioningMatrix,[1,16]);
settings.T = 1000;
settings.env
[fitness, phi, scores, wasteTrend, advTrend, roleTrend, selection, nPunishments, nRewards, socialSanctioningMatrix, usedRules] = evalIndGAS(settings);


% for i=2:size(results,1)
%     ft(i,:) = results{i,j}.fitnessTrend;
% end
color = [253 22 254]./256;
med = mean(phi);
stdX = std(phi);
cPhi = 1:numel(med);
x2 = [cPhi, fliplr(cPhi)];
std_dev = stdX;
curve1 = med + 1.*std_dev;
curve2 = med - 1.*std_dev;
inBetween = [curve1, fliplr(curve2)];
f = fill(x2, inBetween, color, 'FaceAlpha',0.1, 'EdgeColor','none');
set(get(get(f(1),'Annotation'),'LegendInformation'),'IconDisplayStyle','off');
plot(med, 'Color', color, 'LineWidth', 1.5)
box off
set(gca,'fontsize',40)

% ylim([0,100])
% yticks([0 50 100])
% yticklabels({'0', '50','100'})
%
% xlim([0,1000])
% ylim([0,6.1])
% yticks([0 6 ])
% yticklabels({'0', '6'})

xticklabels({})