load('resultsFinalCost0.2.mat')

saction2sting

%figure
hold on
j=5;
ft = results{si(1,j),j}.bestInd.wasteTrend;
% for i=2:size(results,1)
%     ft(i,:) = results{i,j}.fitnessTrend;
% end

color = [253 22 254]./256; 
med = mean(ft);
stdX = std(ft);
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

ylim([0,100])
yticks([0 50 100])
yticklabels({'0', '50','100'})

xlim([0,1000])
ylim([0,10])
yticks([0 5 10])
yticklabels({'0', '5','10'})

xticklabels({})