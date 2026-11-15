% Multiple runs of the evolutionary processes of the social norms

function main_pasture()
parpool('local',30);

%lifetime learning steps
settings.T = 5000;
%multiple runs 
settings.nRun = 15;
%learning rate
settings.alpha = 0.1;
%exploration rate
settings.epsilon = 0;
settings.visualize = 0;


%Social norm perturbation parameters
settings.mutateProb = 0.5;
settings.mutationRate = 1;
settings.addRuleProb = 0.5;
settings.deleteRuleProb = 0.1;

%game parameters
settings.greedyFarmerPayoff = 10;
settings.considerateFarmerPayoff = 5;
settings.upperBound = 100;


%environmental hyperparameters
envs = [0 0; 0 1; 1 0; 0.5 0.5; 1 1];


%complexity regularization parameter
settings.complexityRegularizationParameter = 0.2;


K = 30;
results = cell(K,5);
for j=[3] %1:1:5
    settings.env = envs(j,:);
    j
    parfor i=1:K
        tic;
        settings2 = settings;
        settings2.seed = i;
        results{i,j} = GA_pasture(settings2);
        results{i,j}.elapsedTime = toc;
        
    end
    save(strcat("resPasture_",num2str(counter),"_cost",num2str(settings.complexityRegularizationParameter),".mat"), 'results')
end
delete(gcp)


