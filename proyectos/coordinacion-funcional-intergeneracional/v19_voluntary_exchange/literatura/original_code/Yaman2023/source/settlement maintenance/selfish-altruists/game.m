function results = game(settings)

decay = settings.decay;
T = settings.T;
epsilon = settings.epsilon;
payoffTrend = cell(1,T);
selectionTrend = cell(1,T);
roleTrend = zeros(4,T);
wasteTrend = zeros(1,T);
advTrend = zeros(1,T);

%agent types, 1: Cleaner, 2: Forage, 3: Hunter, 4:
%Soldier
ntype = 4;

% SI = reshape(settings.genotype(1:16), [4,4]);
% apply = reshape(settings.genotype(17:end), [4,4])>0;

% SI = SI.*apply;
SI = zeros(4,4);
     

total = zeros(4,4);
used = zeros(4,4);

n = 10; m = 10;
agents = cell(n,m);

for i=1:n
    for j=1:m
        agents{i,j}.expectedReward = ones([1,ntype]).*10;
    end
end



phi = zeros(1,T);%group average payoff

waste = zeros(size(agents));

for t = 1:T
    
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
    
%     selectionTrend(t,:,:) = selection;
    
    
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
    
    
    payoffs = max(0, payoffs - waste);
    payoffs = payoffs - settings.livingCost;
    
    
    
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
    
    
    waste = min(settings.dirtMax, waste + settings.wasteIncrease);
    
    
    nAdvAttack = 0;
    
    for i=1:n
        for j=1:m
            if(selection(i,j) == 1 && payoffs(i,j) >= 0)
                for i1 = -1:1
                    ii = i + i1;
                    if(ii<1), ii = n; end
                    if(ii>n), ii = 1; end
                    for j1=-1:1
                        jj = j + j1;
                        if(jj<1), jj = m; end
                        if(jj>n), jj = 1; end
                        waste(ii,jj) = settings.wasteBaseline;
                        
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
                        if(selection(ii,jj) == 4 && payoffs(ii,jj)>=0), protected = true; break; end
                        
                    end
                    if(protected), break; end
                end
                if(~protected && payoffs(i,j)>0), payoffs(i,j) = 0; nAdvAttack = nAdvAttack+1; end
            end
        end
    end
    
    
    advTrend(t) = nAdvAttack; 
    
    
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
    payoffTrend{t} = payoffs;
    wasteTrend(t) = mean(mean(waste));
    selectionTrend{t} = selection;
    roleTrend(:,t) = [sum(sum(selection ==1)); sum(sum(selection ==2)); sum(sum(selection ==3)); sum(sum(selection ==4))];
    
    if(settings.visualize && mod(t,10)==0)
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
results.wasteTrend = wasteTrend;
results.advTrend = advTrend;
results.roleTrend = roleTrend;
end

