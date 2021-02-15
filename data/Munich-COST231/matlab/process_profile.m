    % Step 3.1 : Compute seg_vector, seg_normal, centre  
    terrain_file = map;
    point_normal = [];
    
    % Initialisation of the parameters
    group_counter = 1;
    start(group_counter,:) = terrain_file(1,:);
    
    discretisation_counter = 0;
    zc = [];
    for m = 1:size(terrain_file,1)-1
        segment_number = floor(sqrt((terrain_file(m,1)-terrain_file(m+1,1))^2 + (terrain_file(m,2)-terrain_file(m+1,2))^2)/DELTAX);
        the_unit_vector = (terrain_file(m+1,:)-terrain_file(m,:))/(sqrt((terrain_file(m,1)-terrain_file(m+1,1))^2 + (terrain_file(m,2)-terrain_file(m+1,2))^2));
        
        for n = 1:segment_number
            discretisation_counter = discretisation_counter + 1;
            zc(discretisation_counter,:) = terrain_file(m,:) + the_unit_vector*(n-1)*DELTAX;
            point_normal(discretisation_counter,:) = [-the_unit_vector(2) the_unit_vector(1)];
        end
    end        
    
    % Step 3.3 : Set antenna location
    za = zc(1,:) + [sourcex sourcey];

    %% Separate the blocks
if Select_block == 1    % Choose whole building as a block
    % Sweep forward to identify the first points of the buildings
    tt = 0;
    block_location1 = [];
    flag = 1;
    for ct1 = 1:discretisation_counter-1
        if flag == 1
            if zc(ct1+1,1) - zc(ct1,1) == 0 && zc(ct1+1,2) > zc(ct1,2)
                flag = 2;
                tt = tt + 1;
                block_location1(tt) = ct1;
            end
        elseif flag == 2
            if (zc(ct1+1,1) > zc(ct1,1)) && zc(ct1,1) == zc(ct1-1,1) && zc(ct1,2) < zc(ct1-1,2)
                flag = 1;
            end
        end
    end
    
    % Sweep backward to identify the second points of the buildings
    tt = 0;
    block_location2 = [];
    flag = 1;
    for ct1 = discretisation_counter-1:-1:2
        if flag == 1
            if zc(ct1-1,1) - zc(ct1,1) == 0 && zc(ct1-1,2) > zc(ct1,2)
                flag = 2;
                tt = tt + 1;
                block_location2(tt) = ct1;
            end
        elseif flag == 2
            if (zc(ct1-1,1) < zc(ct1,1)) && zc(ct1,1) == zc(ct1+1,1) && zc(ct1,2) < zc(ct1+1,2)
                flag = 1;
            end
        end
    end
    block_location2 = fliplr(block_location2);
    block_location =[];
    for ct1 = 1:size(block_location1,2)
        block_location( (ct1-1)*2 + 1) = block_location1(ct1);
        block_location( (ct1-1)*2 + 2) = block_location2(ct1);
    end 
    
    block_location(1:2:size(block_location,2)) = block_location(1:2:size(block_location,2)) - 1;
    block_location(2:2:size(block_location,2)) = block_location(2:2:size(block_location,2)) + 1;
    
    % Block FBM
    size_block_location = size(block_location,2);
    if size_block_location ~= 0         % Fix the case of LOS
        N = [1:block_location(1)];
        for m = 2:2:size_block_location-1
            N = [N block_location(m):1:block_location(m+1)];  
        end
        N = [N block_location(size_block_location):1:discretisation_counter];
    else    
        N = 1:discretisation_counter;
    end
    
else % Choose vertical edge of the building as a block
    tt = 0;
    block_location = [];
    
    for ct1 = 2:discretisation_counter-1
       if (zc(ct1,1) - zc(ct1-1,1)~=0 && zc(ct1,1) - zc(ct1+1,1)==0) ||...
          (zc(ct1,1) - zc(ct1+1,1)~=0 && zc(ct1,1) - zc(ct1-1,1)==0)    
            tt = tt + 1;
            block_location(tt) = ct1;
       end 
    end
    
    
    % Block FBM
    size_block_location = size(block_location,2);
    
    if size_block_location~=0
        N = [1:block_location(1)-1];
        for m = 2:2:size_block_location-1
            if block_location(m)+ 1 < block_location(m+1)-1
                N = [N block_location(m)+1:1:block_location(m+1)-1];  
            end
        end
        N = [N block_location(size_block_location)+1:1:discretisation_counter];
    
    else
        N = 1:discretisation_counter;
    end
end
    N1 = [1 block_location-1 discretisation_counter];
