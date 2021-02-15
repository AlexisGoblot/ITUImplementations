%% This script is develop to find the interaction points from Tx to Rx

    a_1 = (Rx(2)-Tx(2))/(Rx(1)-Tx(1));      % Coefficent a of equation y = ax+b
    Tx_Rx = [a_1 Tx(2) - a_1*Tx(1)];        % Coefficent b of equation y = ax+b

    % Step 1  : Find potential walls
    potential_walls = [walls];

    % Step 2  : Find real walls and intersection points
    % Collect info of the paths (start and end points)
    intersec_points = [];
    path_1 = [Tx(1) Tx(2) Rx(1) Rx(2)];

    for m = 1:size(potential_walls,1)
        path_2 = potential_walls(m,:);
        [temp] = intersection_points(path_1,path_2);
        if (temp(1) ~= 0) && (temp(2) ~= 0)
            intersec_points = [intersec_points; temp];
        end
    end
    
    % Re-order the intersection points using bubble sorting
    intersec_points = [Tx; intersec_points; Rx];
    if Tx(1) < Rx(1)
        for m = 1:size(intersec_points,1)
            for n = m+1:size(intersec_points,1)
               if  intersec_points(m,1) > intersec_points(n,1)
                   temp = intersec_points(m,:);
                   intersec_points(m,:) = intersec_points(n,:);
                   intersec_points(n,:) = temp;
               end
            end
        end

    else
        for m = 1:size(intersec_points,1)
            for n = m+1:size(intersec_points,1)
               if  intersec_points(m,1) < intersec_points(n,1)
                   temp = intersec_points(m,:);
                   intersec_points(m,:) = intersec_points(n,:);
                   intersec_points(n,:) = temp;
               end
            end
        end
    end

    % Change the order of walls overlapped
    for m = 3:size(intersec_points,1)-1
       if intersec_points(m,1) == intersec_points(m-1,1) && intersec_points(m,2) == intersec_points(m-1,2)
            if intersec_points(m,4) == intersec_points(m-2,4) || intersec_points(m-1,4) == intersec_points(m+1,4)
                temp = intersec_points(m,:);
                intersec_points(m,:) = intersec_points(m-1,:);
                intersec_points(m-1,:) = temp;
            end
       end
    end
    
    % KEEP ONE BUILDING BEHIND THE RX - REMOVES THE OTHERS
    temp = []; flag = 0; temp_id = 0; no_hit = 0;
    for ct1 = 1:size(intersec_points,1)
       if intersec_points(ct1,3) == 0
          flag = flag + 1;
          temp_id = intersec_points(ct1+1,4);
       end
       
       if flag == 3
          temp = [temp; intersec_points(ct1,:)];
          if intersec_points(ct1,4) == temp_id
            no_hit = no_hit + 1; 
          end
          if no_hit == 2
            if intersec_points(ct1,1) == intersec_points(ct1+1,1) && intersec_points(ct1,2) == intersec_points(ct1+1,2)
                temp_id = intersec_points(ct1+1,4);
                no_hit = 0;     % Restarting
            else
                temp = [temp; intersec_points(ct1+1,:)];
                flag = 0;
            end
          end

       elseif flag == 1
           temp = [temp; intersec_points(ct1,:)];
       elseif flag == 2
           temp = [temp; intersec_points(ct1,:)];
           size_intersect_Tx_Rx = size(temp,1);
           flag = 3; 
       end
    end
    
    intersec_points = [temp];

    % Remove the walls so thin
    if size(intersec_points,1) ~= 0 
        temp_1 = [intersec_points(1,:)];
        for m = 2:size(intersec_points,1)-1 
            distance(1) = sqrt(power(intersec_points(m+1,1)-intersec_points(m,1),2) + power(intersec_points(m+1,2)-intersec_points(m,2),2));
            distance(2) = sqrt(power(intersec_points(m,1)-intersec_points(m-1,1),2) + power(intersec_points(m,2)-intersec_points(m-1,2),2));
            if (distance(1) < 0) && intersec_points(m+1,4) == intersec_points(m,4)
                size_intersect_Tx_Rx = size_intersect_Tx_Rx - 1;
            elseif (distance(2) < 0) && intersec_points(m-1,4) == intersec_points(m,4)
                size_intersect_Tx_Rx = size_intersect_Tx_Rx - 1;
            else
                temp_1 = [temp_1; intersec_points(m,:)];
            end
        end
        temp_1 = [temp_1;intersec_points(size(intersec_points,1),:)];
        intersec_points = temp_1;
    end    
    
for m = 1:size(intersec_points,1)
    plot(intersec_points(m,1),intersec_points(m,2),'o','color','black');
    hold on;
end