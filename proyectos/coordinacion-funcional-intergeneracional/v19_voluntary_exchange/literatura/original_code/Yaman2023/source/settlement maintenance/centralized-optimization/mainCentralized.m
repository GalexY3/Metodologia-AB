function mainCentralized()


%define environmental hyperparameters
env = [0, 0;
        0, 1;
        0.5385, 0.5385;
        1, 0;
        1, 1];


%scaling the envi parameters
env(:,1) = env(:,1).*6;


results = cell(size(env,1),1);



for j=1:1
    for i=size(env,1)
        tic;
        results{i,j} = GAcentralized(env(i,1), env(i,2));
        results{i,j}.elapsedTime = toc;
        save results results
    end
end

delete(gcp)
