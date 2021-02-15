%% Step 1.1 : Information about the propagation enviroment	
    MHz             = 1000000.0 ;               % Definition of MHz
    f               = 947.0*MHz ;               % Frequency of operation
    omega           = 2.0*pi*f ;          
    epsilon0        = 8.854e-12; 
	mu0             = 4.0*pi*1.0e-7 ; 
	loss_tangent    = 0.211;                    % Permittivity - Material of the walls: brick
    epsilonr1       = 3.0;                      % Permittivity - Material of the walls: brick
 	epsilon1        = epsilonr1*(1-1i*loss_tangent)*epsilon0;  
    
    mur1 = 1.0; 
	mu1  = mur1*mu0 ;   
 
    k(1) = omega*sqrt(mu0*epsilon0);
	k(2) = omega*sqrt(mu1*epsilon1);

    % impedance of free-space and terrain
	eta(1) = sqrt(mu0/epsilon0);				
    eta(2) = sqrt(mu1/epsilon1);

    % wavelength of free-space and terrain
    wavelength(1) = 1.0/(f*sqrt(mu0*epsilon0)); 
	wavelength(2) = 1.0/(f*sqrt(mu1*epsilon1));
    
    wavelength(1) = 2.0*pi/k(1);
	wavelength(2) = 2.0*pi/k(2);
	
    % Location of antenna
    sourcex = 0.0 ;         % Location of Tx
	sourcey = 13.0;         % Height of Tx
    P0      = 1.0;
    Ie = sqrt(8*P0/(k(1)*eta(1)));
    
%% Step 1.2 : Other variables
    length      = 1;          
    TOL         = 1e-1; 

    height      = 1.5;      % Height of Rx
    N           = 1;    
    keep_looking_for_zero_point = 1;
    
    % Information about which models to run
	number_of_fb_iterations         = 5;        % Number of FB iteration
    forward_scattering              = 1;        % Run FS only (if set to 1)
    computing_error                 = 0;        % Compute relative error (if set to 1)
    
%% Step 1.3 : Now choose number of discretisations so that the sampling rate is sufficient. 
% 	DELTAX = length/N;
% 	while (DELTAX > wavelength(1)/4.0) 
%         N = N*2; 
%         DELTAX = length/N;             
%     end

    DELTAX = wavelength(1)/4;
%% Step 1.4 : Now set up some variables that depend on N ;
    log_const(1) =  1.781*k(1)/(4.0*exp(1.0)) ; 
	log_const(2) =  1.781*k(2)/(4.0*exp(1.0)) ; 

	a = DELTAX*(k(1)*eta(1)/4.0)*(1 - 1i*2.0/pi*log(log_const(1)*DELTAX));
	b = -0.5; 
	c = DELTAX*(k(2)*eta(2)/4.0)*(1 - 1i*2.0/pi*log(log_const(2)*DELTAX));
	d = 0.5 ; 

	self = [a b; c d];
	self_inverse = inv(self);
    
    % Load Information of the walls and Metro Route 200,201,202 
    walls   = load('./Data/building.txt');
    route0  = load('./Data/route0.rx');
    route1  = load('./Data/route1.rx');
    route2  = load('./Data/route2.rx');

    number_of_wall      = size(walls,1);
    number_of_building  = max(walls(:,6));

    Select_block        = 1;    % 1: Choose whole building; 2: Choose vertical edge
    % Step size of the metro route
    step_size_METRO = 1;
    save ./Data/global_variables.mat