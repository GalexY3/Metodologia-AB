function results = GAcentralized(maxWaste, advAttackProb)



settings.T = 150;
settings.nRun = 2;
settings.maxGenerations = 175;
settings.decay = 0.1;
settings.epsilon = 0;
settings.visualize = 0;
settings.maxWaste = maxWaste; 
settings.wasteStep = settings.maxWaste/10;
settings.advAttackProb = advAttackProb;



np = 28*4;
dim = 100;
pop = randi([1, 4], np, dim);
fitness = zeros(np,1);
bestFitness = -inf;
bestInd = [];
bestPhi = [];
phis = cell(np,1);
parfor i=1:np
    settings2 = settings;
    settings2.genotype = pop(i,:);
    [fitness(i), phis{i}] = evalIndCentralized(settings2);
end


for i=1:np
    if(fitness(i) > bestFitness)
        bestFitness = fitness(i);
        bestInd = pop(i,:);
        bestPhi = phis{i};
        %         [bestFitness bestInd]
    end
end
fitnessTrend = bestFitness;
% subplot(2,1,1)
% plot(fitnessTrend)
% subplot(2,1,2)
% plot((bestPhi))

for t = 2:settings.maxGenerations
    
    pop2 = pop;
    fitness2 = fitness;
    phis2 = phis;
    
    if(min(fitness) == 0)
        nFit = (fitness+0.01)./sum(fitness+0.01);
    else
        nFit = (fitness)./sum(fitness);
    end
    
    
    cFit = cumsum(nFit);
    
    parfor i=1:np
        p1 = find(rand<=cFit,1);
        o1 = pop(p1,:);
        if(rand<0.9)
            p2 = find(rand<=cFit,1);
            while p1==p2
                p2 = find(rand<=cFit,1);
            end
            o2 = pop(p2,:);
            cp = randi([2,99]);
            o1(cp+1:end) = o2(cp+1:end);
        end
        
        select = rand(1,length(o1)) < 1/length(o1);
        o1(select) = randi([1,4],1,sum(select));
        while o1 == pop(p1,:)
            select = rand(1,length(o1)) < 1/length(o1);
            o1(select) = randi([1,4],1,sum(select));
        end
            
        
        
        settings2 = settings;
        settings2.genotype = o1;
        [newFitness, newPhis] = evalIndCentralized(settings2);
        fitness2(i) = newFitness;
        pop2(i,:) = o1;
        phis2{i} = newPhis;
    end
    
    pop = [pop; pop2];
    fitness = [fitness; fitness2];
    phis(end+1:2*np) = phis2;
    
    [sf, sInx] = sort(fitness,'descend');
    pop = pop(sInx,:);
    fitness = fitness(sInx);
    phis = phis(sInx);
    
    pop(np+1:end,:) = [];
    fitness(np+1:end,:) = [];
    phis(np+1:end,:) = [];
    
    for i=1:np
        if(fitness(i) > bestFitness)
            bestFitness = fitness(i);
            bestInd = pop(i,:);
            bestPhi = phis{i};
        end
    end
    fitnessTrend(t) = bestFitness;
%     subplot(2,1,1)
%     plot(fitnessTrend)
%     subplot(2,1,2)
%     plot((bestPhi))
%     drawnow
    
    
end

results.settings = settings;
results.fitnessTrend = fitnessTrend;
results.bestInd = bestInd;
results.bestPhi = bestPhi;
results.fitness = fitness;
results.pop = pop;


end