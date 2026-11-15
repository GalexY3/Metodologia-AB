

%parameter for defining experiment that is based on  selfish:1, selfish/altruist:2, altrusits:3
resInx = 3; % selfish:1, selfish/altruist:2, altrusits:3


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
[fitness, phi, resourceTrend, roleTrend] = evalInd(env(envInx,:), self(resInx));

phi = resourceTrend;

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
