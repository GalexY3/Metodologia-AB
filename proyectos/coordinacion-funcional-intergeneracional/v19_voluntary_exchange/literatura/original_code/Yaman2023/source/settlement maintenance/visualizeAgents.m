function visualizeAgents(selection)


grid = zeros(size(selection,1),size(selection,2),3);

for i=1:size(grid,1)
    for j=1:size(grid,2)
        
        if(selection(i,j) == 1)
            grid(i,j,:) = [1 0 0];
        elseif(selection(i,j) == 2)
            grid(i,j,:) = [0 1 0];
        elseif(selection(i,j) == 3)
            grid(i,j,:) = [0 0 1];
        elseif(selection(i,j) == 4)
            grid(i,j,:) = [0 1 1];
        end
    end
end
image(grid)
drawnow;