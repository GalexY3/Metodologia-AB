function results = gameCentralized(settings)

decay = settings.decay;
T = settings.T;


%agent types, 1: Cleaner, 2: Altruistic Forage, 3: Selfish Forager, 4:
%Hunter
ntype = 4;

selection = reshape(settings.genotype(1:100),[10,10]);

% socialIncentive = reshape(settings.genotype(101:116),[4,4]);
% apply = reshape(settings.genotype(117:end), [4,4])>0;
% socialIncentive = socialIncentive.*apply;


payoffTrend = cell(1,T);
selectionTrend = cell(1,T);
roleTrend = zeros(4,T);
wasteTrend = zeros(1,T);
advTrend = zeros(1,T);


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
%     payoffs = payoffs./dirt;
%     payoffs = payoffs - 1;
    
%     iR = randperm(n);
%     jR = randperm(m);
    
    
    
%     for i=iR
%         for j=jR
%             myType = selection(i,j);
%             
%             
%             for i1 = -1:1
%                 ii = i + i1;
%                 if(ii<1), ii = n; end
%                 if(ii>n), ii = 1; end
%                 for j1=-1:1
%                     if(i1 == 0 && j1 == 0), continue; end
%                     jj = j + j1;
%                     if(jj<1), jj = m; end
%                     if(jj>n), jj = 1; end
%                     neighbor = selection(ii,jj);
%                     
%                     out = socialIncentive(myType, neighbor);
%                     
%                     if(out == 0), continue; end
%                     
%                     
%                     payoffs(i,j) = payoffs(i,j) - settings.selfPunishment;
%                     
%                     if(out > 0 && payoffs(i,j) >= out)% + settings.selfPunishment)
%                         payoffs(i,j) = payoffs(i,j) - out;
% %                         payoffs(i,j) = payoffs(i,j) - settings.selfPunishment;
%                         payoffs(ii,jj) = payoffs(ii,jj) + out;
%                     elseif(out < 0 && payoffs(ii,jj) >= abs(out))% + settings.selfPunishment)
%                        payoffs(i,j) = payoffs(i,j) + abs(out);
% %                         payoffs(i,j) = payoffs(i,j) - settings.selfPunishment;
%                         payoffs(ii,jj) = payoffs(ii,jj) - abs(out);
%                     end  
%                 end
%             end
%         end
%     end
    
    
    waste = min(settings.maxWaste, waste + settings.wasteStep);
    wasteTrend(t) = mean(mean(wasteTrend));
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
                        waste(ii,jj) = 0;%max(1, dirt(i1:i2,j1:j2) - 1);
                        
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
                if(~protected && payoffs(i,j)>0), payoffs(i,j) = 0; nAdvAttack = nAdvAttack+1;end
            end
            
        end
    end
    
    
    advTrend(t) = nAdvAttack; 
    
    
    phi(t) = mean(mean(payoffs));
    payoffTrend{t} = payoffs;
    selectionTrend{t} = selection;
    roleTrend(:,t) = [sum(sum(selection ==1)); sum(sum(selection ==2)); sum(sum(selection ==3)); sum(sum(selection ==4))];
    
    if(settings.visualize)
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
    
    %     epsilon = epsilon*0.99;
    
end

% phi = mean(rewards);
results.phi = phi;
results.selection = selection;
results.wasteTrend = wasteTrend;
results.advTrend = advTrend;
results.roleTrend = roleTrend;
end

