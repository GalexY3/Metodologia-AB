function results = GAcentralized(naturalGrowth, workerGrowth)



settings.T = 10000;
settings.nRun = 7;
settings.decay = 0.1;
settings.epsilon = 0;
settings.visualize = 0;
settings.naturalGrowth = naturalGrowth;
settings.workerGrowth = workerGrowth;
settings.maxGenerations = 175;
settings.greedyFarmerPayoff = 10;
settings.considerateFarmerPayoff = 5;
settings.upperBound = 100;





np = 28*4;
dim = 100;% + 2*4*4;
pop = randi([1, 3], np, dim);
fitness = zeros(np,1);
bestFitness = -inf;
bestRoles = [];
bestInd = [];
bestPhi = [];
phis = cell(np,1);
roles = cell(np,1);
parfor i=1:np
    settings2 = settings;
    settings2.genotype = pop(i,:);
    [fitness(i), phis{i}, roles{i}] = evalIndCentralized(settings2);
end



for i=1:np
    if(fitness(i) > bestFitness)
        bestFitness = fitness(i);
        bestInd = pop(i,:);
        bestPhi = phis{i};
        bestRoles = roles{i};
        %         [bestFitness bestInd]
    end
end
fitnessTrend = bestFitness;
% subplot(1,3,1)
% plot(fitnessTrend)
% subplot(1,3,2)
% plot((bestPhi))
% subplot(1,3,3)
% visualizeAgents((bestRoles))
% drawnow

for t = 2:settings.maxGenerations
    
    pop2 = pop;
    fitness2 = fitness;
    phis2 = phis;
    roles2 = roles;
    
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
        o1(select) = randi([1,3],1,sum(select));
        while o1 == pop(p1,:)
            select = rand(1,length(o1)) < 1/length(o1);
            o1(select) = randi([1,3],1,sum(select));
        end
            
        
        
        settings2 = settings;
        settings2.genotype = o1;
        [newFitness, newPhis, newRoles] = evalIndCentralized(settings2);
        fitness2(i) = newFitness;
        pop2(i,:) = o1;
        phis2{i} = newPhis;
        roles2{i} = newRoles;
    end
    
    pop = [pop; pop2];
    fitness = [fitness; fitness2];
    phis(end+1:2*np) = phis2;
    roles(end+1:2*np) = roles2;
    
    [sf, sInx] = sort(fitness,'descend');
    pop = pop(sInx,:);
    fitness = fitness(sInx);
    phis = phis(sInx);
    roles = roles(sInx);
    
    pop(np+1:end,:) = [];
    fitness(np+1:end,:) = [];
    phis(np+1:end,:) = [];
    roles(np+1:end,:) = [];
    
    for i=1:np
        if(fitness(i) > bestFitness)
            bestFitness = fitness(i);
            bestInd = pop(i,:);
            bestPhi = phis{i};
            bestRoles = roles{i};
        end
    end
    
    fitnessTrend(t) = bestFitness;
    % if(mod(t,10)==0)
    %     subplot(1,3,1)
    %     plot(fitnessTrend)
    %     subplot(1,3,2)
    %     plot((bestPhi))
    %     subplot(1,3,3)
    %     visualizeAgents((bestRoles))
    %     drawnow
    % end
    
    if(mod(t,100)==0)
        save runningGAInnate
    end
    
end

results.settings = settings;
results.fitnessTrend = fitnessTrend;
results.bestInd = bestInd;
results.bestPhi = bestPhi;
results.fitness = fitness;
results.pop = pop;


end