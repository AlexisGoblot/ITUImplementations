%% Author: Trinh Xuan Dung - DCU
%% Date: Feb 28th 2011
%% This script is used to find intersection point of 2 paths
% Path_1: Tx-Rx
% Path_2: walls
function [point_m] = intersection_points(path_1, path_2)

% Find coefs a, b of 2 paths: y = ax + b
a_1 = (path_1(4)-path_1(2))/((path_1(3)-path_1(1)));
b_1 = path_1(2) - a_1*path_1(1);

if path_2(1) ~= path_2(3)
    a_2 = (path_2(4)-path_2(2))/((path_2(3)-path_2(1)));
    b_2 = path_2(2) - a_2*path_2(1);
    
    if a_1 == a_2 % 2 paths are in parrallel
        intersection_point = [0 0];
    else
        intersection_point = [(b_2-b_1)/(a_1-a_2) a_1*(b_2-b_1)/(a_1-a_2)+b_1];
    end
else % path_2: x = b
    intersection_point = [path_2(1) a_1*path_2(1)+b_1];
end

% Round up the value of y-intersection point to fix the case of vert walls
if abs(intersection_point(2)-round(intersection_point(2))) < 10^-5
    intersection_point(2) = round(intersection_point(2));
end


% Check the intersection point on the wall or not
flag = 1;  % Flag = 1: on the wall, Flag = 0: not on the wall

if ((path_2(1) < intersection_point(1)) && (path_2(3) < intersection_point(1))) ||... 
   ((path_2(1) > intersection_point(1)) && (path_2(3) > intersection_point(1))) ||...
   ((path_2(2) < intersection_point(2)) && (path_2(4) < intersection_point(2))) ||...
   ((path_2(2) > intersection_point(2)) && (path_2(4) > intersection_point(2))) 
%    ((path_1(1) < intersection_point(1)) && (path_1(3) < intersection_point(1))) ||... 
%    ((path_1(1) > intersection_point(1)) && (path_1(3) > intersection_point(1)))
   
   flag = 0; 
end

if flag == 1
    point_m_x = intersection_point(1);
    point_m_y = intersection_point(2);
else
    point_m_x = 0;
    point_m_y = 0;
end

point_m = [point_m_x point_m_y path_2(5:8)];

