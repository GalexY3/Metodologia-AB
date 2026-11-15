function results = GA_settlement(settings)

seed = settings.seed;
rng(seed)


maxIter = 500;
dim = 16;


socialNorm = unifrnd(-6, +6, 1, dim);
select = rand(1,dim) < 0.5;
socialNorm(select) = 0;


fitnessTrend = zeros(1,maxIter);



%evaluate the social norm
settings.socialNorm = socialNorm;
[fitness, phi, scores, wasteTrend, advTrend, roleTrend, selection, nPunishments, nRewards, socialSanctioningMatrix, usedRules] = evalIndGAS(settings);
fitnessTrend(1,1) = fitness(1);

socialNorm = reshape(socialSanctioningMatrix, [1,dim]);

results.settings = settings;
results.fitnessTrend = fitnessTrend;
results.fitness = fitness;
results.genotype = socialNorm;


%save the best individual
bestInd.phi = phi;
bestInd.scores = scores;
bestInd.wasteTrend = wasteTrend;
bestInd.advTrend = advTrend;
bestInd.roleTrend = roleTrend;
bestInd.selection = selection;
bestInd.nPunishments = nPunishments;
bestInd.nRewards = nRewards;
bestInd.socialSanctioningMatrix = socialSanctioningMatrix;
bestInd.usedRules = usedRules;
results.bestInd = bestInd;


%evolutionary process of social norms 
for t=2:maxIter
    indx = [1:length(socialNorm)];
    newSocialNorm = socialNorm;
    mutated = false;
    %mutate rule
    while ~mutated
        if(rand < settings.mutateProb)
            u = indx(newSocialNorm~=0);
            newSocialNorm(u) = newSocialNorm(u) + normrnd(0,settings.mutationRate,1,length(u));
            mutated = true;
        end
        if(rand < settings.addRuleProb)
            u = indx(newSocialNorm==0);
            if(~isempty(u))
                rInx = randi([1,length(u)]);
                newSocialNorm(u(rInx)) = normrnd(0,1);
                mutated = true;
            end
        end
        if(rand < settings.deleteRuleProb)
            u = indx(newSocialNorm~=0);
            if(~isempty(u))
                rInx = randi([1,length(u)]);
                newSocialNorm(u(rInx)) = 0;
                mutated = true;
            end
        end
    end

    %boundery values
    newSocialNorm(newSocialNorm<-6) = -6;
    newSocialNorm(newSocialNorm>6) = 6;

    settings.socialNorm = newSocialNorm;
    [newFitness, phi, scores, wasteTrend, advTrend, roleTrend, selection, nPunishments, nRewards, socialSanctioningMatrix, usedRules] = evalIndGAS(settings);
    newSocialNorm = reshape(socialSanctioningMatrix, [1,16]);


    if(newFitness >= fitness)
        fitness = newFitness;
        socialNorm = newSocialNorm;
        bestInd.phi = phi;
        bestInd.scores = scores;
        bestInd.wasteTrend = wasteTrend;
        bestInd.advTrend = advTrend;
        bestInd.roleTrend = roleTrend;
        bestInd.selection = selection;
        bestInd.nPunishments = nPunishments;
        bestInd.nRewards = nRewards;
        bestInd.socialSanctioningMatrix = socialSanctioningMatrix;
        bestInd.usedRules = usedRules;
        results.bestInd = bestInd;
    end

    fitnessTrend(t) = fitness;


    %if(mod(t,2)==0)
    %    save(strcat('runningGAS_',num2str(seed),'.mat'))
    %    plot((fitnessTrend(1:t)))
    %    drawnow
    %    reshape(gen(1:16),[4,4])
    %end






end

results.settings = settings;
results.fitnessTrend = fitnessTrend;
results.fitness = fitness;
results.socialNorm = socialNorm;