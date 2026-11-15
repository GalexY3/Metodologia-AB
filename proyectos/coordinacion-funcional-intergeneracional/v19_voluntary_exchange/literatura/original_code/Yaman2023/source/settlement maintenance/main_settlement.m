% Multiple runs of the evolutionary processes of the social norms

function main_settlement()
parpool('local',30);

%lifetime learning steps
settings.T = 500;
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
settings.wasteBaseline = 0;


%environmental hyperparameters
envs = [0 0; 0 1; 1 0; 0.5 0.5; 1 1];


counter = 1;
K = 30;


%complexity regularization parameter
settings.complexityRegularizationParameter = 0.05;

results = cell(K,5);
for j=1:5
    settings.env = envs(j,:);
    j
    parfor i=1:K
        tic;
        settings2 = settings;
        settings2.seed = i;
        results{i,j} = GA_settlement(settings2);
        results{i,j}.elapsedTime = toc;
        
    end
    save(strcat('resSettlement_',num2str(counter),'_cost',num2str(settings.complexityRegularizationParameter),'.mat'), 'results')
    %counter = counter + 1;
end
delete(gcp)
