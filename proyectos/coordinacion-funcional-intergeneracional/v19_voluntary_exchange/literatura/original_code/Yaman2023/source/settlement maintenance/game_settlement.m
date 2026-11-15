function results = game_settlement(settings)

alpha = settings.alpha;
T = settings.T;
epsilon = settings.epsilon;

roleTrend = zeros(4,T);
nRew = 0;
nPun = 0;

%agent types, 1: Cleaner, 2: Forage, 3: Hunter, 4: Soldier
ntype = 4;

socialSanctioningMatrix = reshape(settings.socialNorm(1:16), [4,4]);



     

total = zeros(4,4);
used = zeros(4,4);
usedTrend = zeros(4,4,T);

n = 10; m = 10;
agents = cell(n,m);

for i=1:n
    for j=1:m
        agents{i,j}.expectedReward = ones([1,ntype]).*10;
        agents{i,j}.expectedRewardTrend = ones([1,ntype]).*10;
        agents{i,j}.selectionTrend = [];
        agents{i,j}.payoffTrend = [];
    end
end



phi = zeros(1,T);%group average payoff
wasteTrend = zeros(1,T);
advTrend = zeros(1,T);

waste = ones(size(agents)).*settings.wasteBaseline;

nSanctionTrend = zeros(1,T);

for t = 1:T
    nSanction = 0;

    payoffs = zeros(size(agents));
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
    
    
    
    for i=1:n
        for j=1:m
            
            if(selection(i,j) == 2)
                payoffs(i,j) = payoffs(i,j) + 3;
            elseif(selection(i,j) == 3)
                n3type = 0;
                for i1 = -1:1
                    ii = i + i1;
                    if(ii<1), ii = n; end
                    if(ii>n), ii = 1; end
                    for j1=-1:1
                        jj = j + j1;
                        if(jj<1), jj = m; end
                        if(jj>n), jj = 1; end
                        if(selection(ii,jj) == 3), n3type = n3type + 1; end
                        if(n3type >=5), break; end
                    end
                    if(n3type >=5), break; end
                end
                
                if(n3type >= 5)
                    payoffs(i,j) =  payoffs(i,j) + 6;
                end
            end
        end
    end
    
    
    %payoffs = payoffs/waste;
    payoffs = max(0, payoffs - waste);
%     payoffs = payoffs - settings.livingCost;
    
    
    
    iR = randperm(n);
    jR = randperm(m);
    
    
    
    for i=iR
        for j=jR
            mytype = selection(i,j);
            is = [-1:1];
            is = is(randperm(3));
            for i1 = is
                ii = i + i1;
                if(ii<1), ii = n; end
                if(ii>n), ii = 1; end
                
                js = [-1:1];
                js = js(randperm(3));
                for j1= js
                    if(i1 == 0 && j1 == 0), continue; end
                    jj = j + j1;
                    if(jj<1), jj = m; end
                    if(jj>n), jj = 1; end
                    neighborType = selection(ii,jj);
                    
                    
                    out = socialSanctioningMatrix(mytype, neighborType);
                    out(out>5) = 5;
                    out(out<-5) = -5;
                    %                     probs = (out(1:8)+5)./10;
                    %                     costs = out(9:16);
                    if(out == 0), continue; end
                    
                    
                    total(mytype, neighborType) = total(mytype, neighborType) + 1;
%                     payoffs(i,j) = payoffs(i,j) - settings.selfPunishment;
                    
                    if(out > 0 && payoffs(i,j) >= out)% + settings.selfPunishment)
                        usedTrend(mytype, neighborType, t) = usedTrend(mytype, neighborType, t) + 1;
                        used(mytype, neighborType) = used(mytype, neighborType) + 1;
                        payoffs(i,j) = payoffs(i,j) - out;
%                         payoffs(i,j) = payoffs(i,j) - settings.selfPunishment;
                        payoffs(ii,jj) = payoffs(ii,jj) + out;
                        nRew = nRew + 1;
                        nSanction = nSanction + 1;
                    elseif(out < 0 && payoffs(ii,jj) >= abs(out))% + settings.selfPunishment)
                        usedTrend(mytype, neighborType, t) = usedTrend(mytype, neighborType, t) + 1;
                        used(mytype, neighborType) = used(mytype, neighborType) + 1;
                        payoffs(i,j) = payoffs(i,j) + abs(out);
%                         payoffs(i,j) = payoffs(i,j) - settings.selfPunishment;
                        payoffs(ii,jj) = payoffs(ii,jj) - abs(out);
                        nPun = nPun + 1;
                        nSanction = nSanction + 1;
                    end
                    
                    
                end
            end
            
            
        end
    end
    nSanctionTrend(t) = nSanction;

    
    waste = min(settings.wasteMax, waste + settings.wasteIncrease);
    advAttacks = 0;
    for i=1:n
        for j=1:m
            if(selection(i,j) == 1)% && payoffs(i,j) >= 0)
                for i1 = -1:1
                    ii = i + i1;
                    if(ii<1), ii = n; end
                    if(ii>n), ii = 1; end
                    for j1=-1:1
                        jj = j + j1;
                        if(jj<1), jj = m; end
                        if(jj>n), jj = 1; end
                        waste(ii,jj) = settings.wasteBaseline;%max(1, waste(i1:i2,j1:j2) - 1);
                        
                    end
                end
            end
            
            % adversarial attack if there is no protection
            if(rand < settings.advAttackProb)
                protected = false;
                for i1 = -1:1
                    ii = i + i1;
                    if(ii<1), ii = n; end
                    if(ii>n), ii = 1; end
                    for j1=-1:1
                        jj = j + j1;
                        if(jj<1), jj = m; end
                        if(jj>n), jj = 1; end
                        if(selection(ii,jj) == 4), protected = true; break; end % && payoffs(ii,jj)>=0), protected = true; break; end
                        
                    end
                    if(protected), break; end
                end
                if(~protected && payoffs(i,j)>0), payoffs(i,j) = 0; advAttacks = advAttacks + 1; end
            end
        end
    end
    
    
    
    
    for i=1:n
        for j=1:m
            agents{i,j}.expectedReward(selection(i,j)) = ...
                agents{i,j}.expectedReward(selection(i,j)) +...
                alpha*(payoffs(i,j) - agents{i,j}.expectedReward(selection(i,j)));

            agents{i,j}.expectedRewardTrend = [agents{i,j}.expectedRewardTrend; ...
                agents{i,j}.expectedReward];

            agents{i,j}.selectionTrend = [agents{i,j}.selectionTrend selection(i,j)];

            agents{i,j}.payoffTrend = [agents{i,j}.payoffTrend payoffs(i,j)];
        end
    end
    
    phi(t) = mean(mean(payoffs));
    wasteTrend(t) = mean(mean(waste));
    advTrend(t) = mean(mean(advAttacks));
    
    roleTrend(:,t) = [sum(sum(selection ==1)); sum(sum(selection ==2)); sum(sum(selection ==3)); sum(sum(selection ==4))];
    
    if(settings.visualize && t>400)
        subplot(3,2,1)
        visualizeAgents(selection)
        subplot(3,2,2)
        heatmap(selection)
        subplot(3,2,3)
        heatmap(round(payoffs))
        subplot(3,2,4)
        heatmap(round(waste))
        subplot(3,2,[5 6])
        plot(phi(1:t))
        drawnow
        %         visualizeAgents(grid, locations, types, waste)
    end
    
    %epsilon = epsilon*0.99;
    
end

% phi = mean(rewards);
results.phi = phi;
u = used./total;
u(total == 0) = 0;
results.used = u;
results.socialSanctioningMatrix = socialSanctioningMatrix;
results.selection = selection;
results.roleTrend = roleTrend;
results.wasteTrend = wasteTrend;
results.advTrend = advTrend;
results.nRew = nRew;
results.nPun = nPun;

%phi(end)
%figure
%visualizeAgents(selection)
%drawnow
end

