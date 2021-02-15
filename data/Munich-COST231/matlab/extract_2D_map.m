%% This script is developed to extract 2D vertical map from the information of interaction
%% points

    map = [];
    flag = 0;
    for m = 2:size_intersect_Tx_Rx - 1
        distance(m) = sqrt(power(intersec_points(m,1)-intersec_points(m-1,1),2) + power(intersec_points(m,2)-intersec_points(m-1,2),2));
        total_distance = sqrt(power(intersec_points(m,1)-intersec_points(1,1),2) + power(intersec_points(m,2)-intersec_points(1,2),2));

        distance_1  = sqrt(power(intersec_points(m,1)-intersec_points(m-1,1),2) + power(intersec_points(m,2)-intersec_points(m-1,2),2));
        distance_2  = sqrt(power(intersec_points(m,1)-intersec_points(m+1,1),2) + power(intersec_points(m,2)-intersec_points(m+1,2),2));

        if intersec_points(m,1) == intersec_points(m-1,1) && intersec_points(m,2) == intersec_points(m-1,2)
            map = [map; total_distance intersec_points(m,6) + intersec_points(m,3)];
        elseif intersec_points(m,1) == intersec_points(m+1,1) && intersec_points(m,2) == intersec_points(m+1,2)
            map = [map; total_distance intersec_points(m,6) + intersec_points(m,3)];
        else
            if flag == 0
                if distance_1 < 0 % Fix the bug of distance between building (so small)
                    m;
                    map = [map; total_distance intersec_points(m-1,6) + intersec_points(m-1,3)];
                    map = [map; total_distance intersec_points(m,6)   + intersec_points(m,3)];
                elseif distance_2 < 0
                    map = [map; total_distance intersec_points(m,6)   + intersec_points(m,3)];
                else
                    map = [map; total_distance intersec_points(m,6)];
                    map = [map; total_distance intersec_points(m,6) + intersec_points(m,3)];
                    if intersec_points(m,4) ~= intersec_points(m-1,4) && intersec_points(m,4) ~= intersec_points(m+1,4)
                        tt = m;
                        flag = 1;
                    end
                end
                
            elseif flag == 1
                if intersec_points(m,4) == intersec_points(tt,4)
                    map = [map; total_distance intersec_points(m,6) + intersec_points(m,3)];
                    map = [map; total_distance intersec_points(m,6)];
                    flag = 0;
                else
                    map = [map; total_distance intersec_points(m,6) + intersec_points(m,3)];
                end
            end
        end
    end

    distance_Rx = sqrt(power(Rx(1)-Tx(1),2) + power(Rx(2)-Tx(2),2));
    distance_Rx_store = distance_Rx;
    map1 = [0 Tx(6); map; distance_Rx Rx(6)];
%     map1 = [0 Tx(6); map; distance_Rx map(size(map,1)-1,2)];

    map = [];
    flag = 0;
    for m = size_intersect_Tx_Rx+1:size(intersec_points,1)-1
        distance(m) = sqrt(power(intersec_points(m,1)-intersec_points(m-1,1),2) + power(intersec_points(m,2)-intersec_points(m-1,2),2));
        total_distance = sqrt(power(intersec_points(m,1)-intersec_points(1,1),2) + power(intersec_points(m,2)-intersec_points(1,2),2));

        distance_1  = sqrt(power(intersec_points(m,1)-intersec_points(m-1,1),2) + power(intersec_points(m,2)-intersec_points(m-1,2),2));
        distance_2  = sqrt(power(intersec_points(m,1)-intersec_points(m+1,1),2) + power(intersec_points(m,2)-intersec_points(m+1,2),2));

        if intersec_points(m,1) == intersec_points(m-1,1) && intersec_points(m,2) == intersec_points(m-1,2)
            map = [map; total_distance intersec_points(m,6) + intersec_points(m,3)];
        elseif intersec_points(m,1) == intersec_points(m+1,1) && intersec_points(m,2) == intersec_points(m+1,2)
            map = [map; total_distance intersec_points(m,6) + intersec_points(m,3)];
        else
            if flag == 0
                if distance_1 < 0 % Fix the bug of distance between building (so small)
                    m;
                    map = [map; total_distance intersec_points(m-1,6) + intersec_points(m-1,3)];
                    map = [map; total_distance intersec_points(m,6)   + intersec_points(m,3)];
                elseif distance_2 < 0
                    map = [map; total_distance intersec_points(m,6)   + intersec_points(m,3)];
                else
                    map = [map; total_distance intersec_points(m,6)];
                    map = [map; total_distance intersec_points(m,6) + intersec_points(m,3)];
                    if intersec_points(m,4) ~= intersec_points(m-1,4) && intersec_points(m,4) ~= intersec_points(m+1,4)
                        tt = m;
                        flag = 1;
                    end
                end
                
            elseif flag == 1
                if intersec_points(m,4) == intersec_points(tt,4)
                    map = [map; total_distance intersec_points(m,6) + intersec_points(m,3)];
                    map = [map; total_distance intersec_points(m,6)];
                    flag = 0;
                else
                    map = [map; total_distance intersec_points(m,6) + intersec_points(m,3)];
                end
            end
        end
    end
    
    distance_Rx = sqrt(power(intersec_points(size(intersec_points,1),1)-Tx(1),2) + power(intersec_points(size(intersec_points,1),2)-Tx(2),2));
    map = [map; distance_Rx intersec_points(size(intersec_points,1),6)];
    map = [map1; map];
    
    % Reoder the 2D map
    for m = 2:size(map,1)-1
        if map(m-1,2) == map(m+1,2) && map(m,2) < map(m+1,2) && map(m+1,1) == map(m,1)
            temp        = map(m,:);
            map(m,:)    = map(m+1,:);
            map(m+1,:)  = temp;
        end
    end
    map(find(map(:,1)==distance_Rx_store),2) = map(find(map(:,1)==distance_Rx_store)-1,2);
    figure;
    plot(map(:,1), map(:,2),'x')
    hold on;
    plot(map(:,1), map(:,2))