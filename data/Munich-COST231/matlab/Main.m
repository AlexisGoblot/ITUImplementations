%% This code is developed to compute the pathloss from the 2D vertical cut
%% of Munich City 
%% DCU - 07/2013. 
%% Author: Dung Trinh. Email: xuan.trinh2@mail.dcu.ie

clear all
clc
close all

% Define configuration and varibles for simulation
Global_Variables;          % Define variables
% Plot walls
Plot_City;               % Plot the 2D horizontal map of Munich city

%% Run Simulation 

for path_counter = 20:20
    fprintf('Running simulation for Counter: %d \n', path_counter);
    Tx      = ([1281.36 1381.27 0 0 1 515]);                                % Location of TX
    Rx      = [route1((path_counter-1)*step_size_METRO+1,2:3) 0 0 1 515];   % Location of RX
    
    %% Step 1: Find interaction points
    find_interaction_points;    
    
    %% Step 2: Extract height and build 2D map
    extract_2D_map;
    
    %% Step 3: Process profile
    process_profile;
    
   end