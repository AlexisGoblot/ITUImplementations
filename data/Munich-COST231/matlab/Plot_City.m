%% This script is developed to plot the map of Munich City
% Plot the buildings
figure;
count_temp = 1;

Tx      = round([1281.36 1381.27 0 0 1 515]);                           % Location of TX
plot(Tx(1),Tx(2),'o','color','black');
hold on;
plot(route0(:,2),route0(:,3),'LineWidth',3,'color','red');      % Plot the METRO ROUTE 200
plot(route1(:,2),route1(:,3),'LineWidth',3,'color','black');    % Plot the METRO ROUTE 201
plot(route2(:,2),route2(:,3),'LineWidth',3,'color','green');    % Plot the METRO ROUTE 202
legend('METRO ROUTE 200','METRO ROUTE 201','METRO ROUTE 202');
legend('Transmitter','METRO ROUTE 202');
for m = 1:number_of_wall
    if m>1 && walls(m,6) ~= walls(m-1,6)
        count_temp = count_temp + 1;
    end
    wall_x = [walls(m,1) walls(m,3)];
    wall_y = [walls(m,2) walls(m,4)];
    wall_z = [walls(m,8) walls(m,8)];
    h = plot(wall_x,wall_y);
    rand('seed',count_temp)
    set(h,'Color',[rand rand rand]);
    hold on;
end

% Plot the METRO ROUTE

% Plot the starting and ending points of the METRO ROUTE
plot(route0(1,2),route0(1,3),'o','color','red');
plot(route0(size(route0,1),2),route0(size(route0,1),3),'rs','color','red');
plot(route1(1,2),route1(1,3),'o','color','black');
plot(route1(size(route1,1),2),route1(size(route1,1),3),'rs','color','black');
plot(route2(1,2),route2(1,3),'o','color','black');
plot(route2(size(route2,1),2),route2(size(route2,1),3),'rs','color','black');

title('Map of Munich City');