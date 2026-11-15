function results = gameCentralized(settings)

T = settings.T;

greedyFarmerPayoff = settings.greedyFarmerPayoff;
considerateFarmerPayoff = settings.considerateFarmerPayoff;
upperBound = settings.upperBound;

%agent types,  2: farmer, 3: worker
ntype = 3;

selection = reshape(settings.genotype(1:100),[10,10]);

payoffTrend = cell(1,T);
selectionTrend = cell(1,T);
roleTrend = zeros(3,T);


n = 10; m = 10;

phi = zeros(1,T);%group average payoff

resource = ones(n,m).*100;

naturalGrowth = ones(n,m).*settings.naturalGrowth;
workerGrowthFactor = settings.workerGrowth;

resourceTrend = zeros(1,T);

for t = 1:T
    
    
    workerGrowth = zeros(n,m);
    workerGrowth(selection == 3) = workerGrowthFactor;
    dRes = (naturalGrowth + workerGrowth).*resource.*(1-resource./upperBound);
    resource = resource + dRes;
    
    trueRoles = selection;
    trueRoles(selection == 3) = 4;
    payoffs = zeros(size(resource));
    
    iR = randperm(n);
    jR = randperm(m);
    
    for i=iR
        for j=jR
            myType = selection(i,j);
            resourceUse = 0;
            if(myType == 1)
                resourceUse = greedyFarmerPayoff;
            elseif(myType == 2)
                resourceUse = considerateFarmerPayoff;
            end
            if(resourceUse ~= 0)
                is = [-1:1];
                is = is(randperm(3));
                js = [-1:1];
                js = js(randperm(3));
                for i1 = is
                    ii = i + i1;
                    if(ii<1), ii = n; end
                    if(ii>n), ii = 1; end
                    for j1=js
                        if(resourceUse == 0), break; end
                        jj = j + j1;
                        if(jj<1), jj = m; end
                        if(jj>n), jj = 1; end
                        if(resource(ii,jj) > 0)
                            if(resourceUse <= resource(ii,jj))
                                resource(ii,jj) = resource(ii,jj) - resourceUse;
                                payoffs(i,j) = payoffs(i,j) + resourceUse;
                                resourceUse = 0;
                            else
                                resourceUse = resourceUse - resource(ii,jj);
                                payoffs(i,j) = payoffs(i,j) + resource(ii,jj);
                                resource(ii,jj) = 0;
                            end
                        end
                    end
                    if(resourceUse == 0), break; end
                end
            end

        end
    end


    
    
    
    
    
    phi(t) = mean(mean(payoffs));
    resourceTrend(t) = mean(mean(resource));
    if(phi(t) == 0)
        break;
    end
    payoffTrend{t} = payoffs;
    selectionTrend{t} = selection;
    roleTrend(:,t) = [sum(sum(selection ==1)); sum(sum(selection ==2)); sum(sum(selection ==3));];
    
    if(settings.visualize && t>90000)
        subplot(3,2,1)
        visualizeAgents(trueRoles)
        subplot(3,2,2)
        heatmap(trueRoles)
        subplot(3,2,3)
        heatmap(round(payoffs))
        subplot(3,2,4)
        heatmap(round(resource))
        subplot(3,2,[5 6])
        plot(phi(1:t))
        drawnow
        %         visualizeAgents(grid, locations, types, dirt)
    end
    
    %     epsilon = epsilon*0.99;
    
end

% phi = mean(rewards);
results.phi = phi;
results.selection = selection;
results.trueRoles = trueRoles;
results.resourceTrend = resourceTrend;
results.roleTrend = roleTrend;
end

