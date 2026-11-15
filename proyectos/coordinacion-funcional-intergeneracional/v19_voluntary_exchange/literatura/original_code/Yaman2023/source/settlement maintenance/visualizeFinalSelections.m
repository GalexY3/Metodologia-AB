sanction2string

j=5;
k = 1;
for i=1:1
    figure
    visualizeAgents(results{si(i,j),j}.bestInd.selection{1})
    xticklabels({})
    yticklabels({})
end

return

figure
plot(mean(results{si(1,j),j}.bestInd.phi), LineWidth=1.5)
lab = {"1"};

hold on

for i=2:k
    plot(mean(results{si(i,j),j}.bestInd.phi), LineWidth=1.5)
    lab{i} = num2str(i);
end
legend(lab, 'NumColumns',3)
set(gca,'FontSize',20)
ylabel("Average payoff")
xlabel("Time step")
xlim([0, size(results{si(1,j), j}.bestInd.phi,2)])