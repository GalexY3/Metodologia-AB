%load('resultsSepAll.mat')

%define environmental hyperparameters
env = [0, 0;
        0, 1;
        0.5385, 0.5385;
        1, 0;
        1, 1];

%select the environment to run
envInx = 5;

env(envInx,:)

self = [1 0.5 0];

[fitness, phi, used, wasteTrend, advTrend, roleTrend] = evalInd(env(envInx,:), self(resInx));
%phi = results{inx(envInx),resInx}.phi; %plot phi
%phi = results{inx(envInx),resInx}.resourceTrend; %plot resourceTrend

phi = wasteTrend;

hold on





if resInx == 1
    color = [255, 165,0]./255; %selfish
elseif resInx == 2
    color = [128, 0,0]./255; %selfish/altruist
else
    color = [0, 128,128]./255; %altriusts
end
med = mean(phi(:,1:1000));
stdX = std(phi(:,1:1000));
cPhi = 1:numel(med);    
x2 = [cPhi, fliplr(cPhi)];
std_dev = stdX;
curve1 = med + 1.*std_dev;
curve2 = med - 1.*std_dev;
inBetween = [curve1, fliplr(curve2)];
f = fill(x2, inBetween, color, 'FaceAlpha',0.1, 'EdgeColor','none');
set(get(get(f(1),'Annotation'),'LegendInformation'),'IconDisplayStyle','off');
plot(med, 'Color', color, 'LineWidth', 1.5)

% set(gca,'fontsize',20)
% xlim([0,1000])
% ylim([0,10])
% yticks([5 10])
% yticklabels({'5','10'})