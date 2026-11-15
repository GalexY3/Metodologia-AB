function results = game(settings)

decay = settings.decay;
T = settings.T;
epsilon = settings.epsilon;
payoffTrend = cell(1,T);
selectionTrend = cell(1,T);
roleTrend = zeros(3,T);
resourceTrend = zeros(1,T);


greedyFarmerPayoff = settings.greedyFarmerPayoff;
considerateFarmerPayoff = settings.considerateFarmerPayoff;
upperBound = settings.upperBound;



ntype = 3;

% SI = reshape(settings.genotype(1:16), [ntype,ntype]);
% apply = reshape(settings.genotype(17:end), [ntype,ntype])>0;

% SI = SI.*apply;
SI = zeros(ntype,ntype);
     

total = zeros(ntype,ntype);
used = zeros(ntype,ntype);

n = 10; m = 10;
agents = cell(n,m);

for i=1:n
    for j=1:m
        agents{i,j}.expectedReward = ones([1,ntype]).*10;
    end
end



phi = zeros(1,T);%group average payoff

resource = ones(n,m).*100;



naturalGrowth = ones(n,m).*settings.naturalGrowth;
workerGrowthFactor = settings.workerGrowth;

for t = 1:T
    
    selection = zeros(size(agents));
    
    for i=1:n
        for j=1:m
            r = randperm(length(agents{i,j}.expectedReward));
            [mV, mInx] = max(agents{i,j}.expectedReward(r));
            selection(i,j) = r(mInx);
            
            if(rand < epsilon)
                randSelect = randi([1,ntype]);
                while randSelect==selection(i,j)
                    randSelect = randi([1,ntype]);
                end
                selection(i,j) = randSelect;
            end
        end
    end
    
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
    
    
    
%     selectionTrend(t,:,:) = selection;
    
    
    
    
%     iR = randperm(n);
%     jR = randperm(m);
%     
%     
%     
%     for i=iR
%         for j=jR
%             mytype = selection(i,j);
%             is = [-1:1];
%             is = is(randperm(3));
%             for i1 = is
%                 ii = i + i1;
%                 if(ii<1), ii = n; end
%                 if(ii>n), ii = 1; end
%                 
%                 js = [-1:1];
%                 js = js(randperm(3));
%                 for j1= js
%                     if(i1 == 0 && j1 == 0), continue; end
%                     jj = j + j1;
%                     if(jj<1), jj = m; end
%                     if(jj>n), jj = 1; end
%                     neighborType = selection(ii,jj);
%                     
%                     
%                     out = SI(mytype, neighborType);
%                     out(out>5) = 5;
%                     out(out<-5) = -5;
%                     %                     probs = (out(1:8)+5)./10;
%                     %                     costs = out(9:16);
%                     if(out == 0), continue; end
%                     
%                     
%                     total(mytype, neighborType) = total(mytype, neighborType) + 1;
%                     payoffs(i,j) = payoffs(i,j) - settings.selfPunishment;
%                     
%                     if(out > 0 && payoffs(i,j) >= out)% + settings.selfPunishment)
%                         
%                         used(mytype, neighborType) = used(mytype, neighborType) + 1;
%                         payoffs(i,j) = payoffs(i,j) - out;
% %                         payoffs(i,j) = payoffs(i,j) - settings.selfPunishment;
%                         payoffs(ii,jj) = payoffs(ii,jj) + out;
%                     elseif(out < 0 && payoffs(ii,jj) >= abs(out))% + settings.selfPunishment)
%                         used(mytype, neighborType) = used(mytype, neighborType) + 1;
%                         payoffs(i,j) = payoffs(i,j) + abs(out);
% %                         payoffs(i,j) = payoffs(i,j) - settings.selfPunishment;
%                         payoffs(ii,jj) = payoffs(ii,jj) - abs(out);
%                     end
%                     
%                     
%                 end
%             end
%             
%             
%         end
%     end
      
    
    
    
    for i=1:n
        for j=1:m
            myPayoff = payoffs(i,j);
            avePayoff = 0;
            for i1 = -1:1
                ii = i + i1;
                if(ii<1), ii = n; end
                if(ii>n), ii = 1; end
                for j1=-1:1
                    if(i1 == 0 && j1 ==0), continue; end
                    jj = j + j1;
                    if(jj<1), jj = m; end
                    if(jj>n), jj = 1; end
                    avePayoff = avePayoff + payoffs(ii,jj);
                end
            end
                
            agents{i,j}.expectedReward(selection(i,j)) = ...
                agents{i,j}.expectedReward(selection(i,j)) +...
                decay*(((avePayoff/8)*(1-settings.self)+myPayoff*settings.self) - agents{i,j}.expectedReward(selection(i,j)));
        end
    end
    
    phi(t) = mean(mean(payoffs));
    resourceTrend(t) = mean(mean(resource));
    payoffTrend{t} = payoffs;
    selectionTrend{t} = selection;
    roleTrend(:,t) = [sum(sum(selection ==1)); sum(sum(selection ==2)); sum(sum(selection ==3));];
    
    if(settings.visualize && t > 900)
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
    
    epsilon = epsilon*0.99;
    
end

% phi = mean(rewards);
results.phi = phi;
u = used./total;
u(total == 0) = 0;
results.used = u;
results.SI = SI;
results.selection = selection;
results.roleTrend = roleTrend;
results.resourceTrend = resourceTrend;
end

