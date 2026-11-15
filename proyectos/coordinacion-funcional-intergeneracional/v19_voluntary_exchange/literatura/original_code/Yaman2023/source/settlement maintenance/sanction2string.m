
fitness = [];

for j=1:5
    for i=1:30
        meanPhi = mean(results{i,j}.bestInd.phi);
        fitness(i,j) = mean(meanPhi(end-100:end)) - results{i,j}.settings.complexityRegularizationParameter*sum(sum(sign(abs(results{i,j}.bestInd.socialSanctioningMatrix))));
    end
end

si = [];fi = [];
for j=5:-1:1
    [s, sInx] = sort(fitness(:,j),'descend');
    si(:,j) = sInx;
    fi(:,j) = s;
end

lab = {"C", "F", "H", "S"};
f_nocost = fi;
strings = {};
st = {};
for l=5:-1:1
    for k=1:30
        SS = results{si(k,l),l}.bestInd.socialSanctioningMatrix;

        s = {};
        s2 = " ";
        for i=1:4
            for j=1:4
                if(SS(i,j)~=0)
                    s{end+1} = strcat(lab{i}, "-", lab{j}, ":", num2str(SS(i,j)));
                    %s2 = strcat(s2, " ", lab{i}, "-", lab{j}, ":", num2str(SS(i,j)));
                    if(SS(i,j) > 0)
                        s2 = strcat(s2, " ", "Role ",lab{i}," ought to encourage role ",lab{j}," by ",num2str(SS(i,j))," amount");
                    else
                        s2 = strcat(s2, " ", "Role ",lab{i}," ought to discourage role ",lab{j}," by ",num2str(SS(i,j))," amount");
                    end
                end
            end
        end
        st{k,l} = s;
        strings{k,l} = s2;
    end
end
strings = cell2table(strings);
writetable(strings,'test.csv')