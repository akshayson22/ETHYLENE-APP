clc,clear

%product parameters

Wp=0.27703; %Weight of fruit, kg
density=0.001; %density of avocados, kg mL-1
Vf=Wp/density; %Volume of fruit, mL

%packaging parameters

%LengthofPackage=10; cm
%WidthofPackage=5; cm
%DepthofPackage=3; cm
%Vp=LengthofPackage*WidthofPackage*DepthofPackage; cm3
%SurfaceAreaPackage=2*(LengthofPackage+WidthofPackage)*DepthofPackage; %surface area of package, cm2
Vp=2488; % Volume of package, mL

V=Vp-Vf; % Headspace volume, mL

%storage parameters

Test_days= 12; %storage duration, day
StorageTemperature=10; %storage temperature, C
AirVelocity= 7.2; %cooling air velocity, cm s-1
L= 0.003; %packaging film thickness, cm
Perfodiameter= [0.085	0.0775	0.0735]; %perforation diameter, cm (multiple perforation in square bracket with space)
T=StorageTemperature+273.15; %storage temperature, K
R=8.314472;  %gas constant, J mol-1 K-1

%O2 consumption or respiration rate (Ro2)

ko2ref=5.96*10^8; %koref in chemical kinetics equation, mL kg-1 h-1
ao2=0.75; %exponent for rr in chemical kinetics equation
Eao2=36275; %activation energy, J mol-1
ko2= ko2ref*exp(-(Eao2/(R*T))); %Arrhenius equation for new ko2, mL kg-1 h-1

%C2H4 production or ethylene production rate (Rc2h4)

kc2h4ref=1.19*10^12; %kc2h4ref in chemical kinetics equation, µL kg-1 h-1
ac2h4=0.93; %exponent for epr in chemical kinetics equation
Eac2h4=63836; %activation energy, J mol-1
kc2h4= kc2h4ref*exp(-(Eac2h4/(R*T))); %Arrhenius equation for new kc2h4,µL kg-1 h-1 

%scavenger parameters

mryan=0.00; %weight of ryan ethylene scavenger, g
Earyan=22871.97195; %activation enegry,J mol-1 K-1
Kryanref= 0.695197; %reference rate constant at 21C temperature, h-1
Kryan=Kryanref*exp(-(Earyan/R)*((1/(T))-(1/294.81))); %Pseudo-first-order rate constant at temperature T, h-1
qryanmax0=2.842475151; %maximum absorption capacity of ryan ethylene scavenger at T; L kg-1 of scavenger
qryanmax=qryanmax0*(mryan/1000)*(10^6)/(V/1000); %absorption capacity of ryan ethylene scavenger for weight of mryan and volume of V, ppm

%tranmission rate for ethylene and oxygen through perforations

Transethy=zeros(1,length(Perfodiameter)); %ethylene tranmission rate, cm3 h-1
Transoxy=zeros(1,length(Perfodiameter)); %oxygen tranmission rate, cm3 h-1

for i=1:length(Perfodiameter)

    %ethylene tranmission rate, cm3 h-1 
    
    Transethy(i)= ((0.04*AirVelocity)+(((2.4382*10^-6)*(T^1.81))/((AirVelocity^0.05)*(L^0.25)*(Perfodiameter(i)^0.8))))*(0.78539816339*(Perfodiameter(i)^2))*3600;

    %oxygen tranmission rate, cm3 h-1 
    
    Transoxy(i)= (((T^1.724)*1.00909*10^-5)/(Perfodiameter(i)))*(0.78539816339*(Perfodiameter(i)^2))*3600;

end

PerfoSum=sum(Perfodiameter);

if PerfoSum <=0
    TotalTransethy=0;
    TotalTransoxy=0;

else
    TotalTransethy= sum(Transethy);
    TotalTransoxy= sum(Transoxy);
end

%Permeability of film (if necessary)

%PermeabilityOfPackagingfilmC2H4=1.23; cm3/cm2 h 
%PermeabilityOfPackagingfilmO2=1.23; cm3/cm2 h 
%TotalTransethy= PermeabilityOfPackagingfilmC2H4*SurfaceAreaPackage; 
%TotalTransoxy= PermeabilityOfPackagingfilmO2*SurfaceAreaPackage;

%Number of steps for loop

dur=Test_days*24; %Experiment duration, h
t=1/3600; %Time interval, h
NS=dur/t; %Number of steps
times = t+zeros(1,NS+1);
timesinhr =cumsum(times);

%initialize matrix for loop
Ro2 = zeros(1,NS+1);
TransmissionRateOxy = zeros(1,NS+1);
ChangeInOxy = zeros(1,NS+1);
yo2 = zeros(1,NS+1);
Rc2h4 = zeros(1,NS+1);
TransmissionRateEthy = zeros(1,NS+1);
ChangeInEthy = zeros(1,NS+1);
yc2h4 = zeros(1,NS+1);

%ethylene and oxygen mass balance using transmission and repsiration rate

for i=1:NS

    yo2(1)=0.209;
    yc2h4(1)=0;
       
    Ro2(i)=-(ko2*(yo2(i)^ao2))*Wp*t/V;
        
        if PerfoSum <=0
            TransmissionRateOxy (i) =0;

        else
            TransmissionRateOxy(i)=(TotalTransoxy*t*(yo2(1)-yo2(i)))/V;
        end 
    
    ChangeInOxy(i)=Ro2(i)+TransmissionRateOxy(i);
    yo2(i+1)=yo2(i)+ChangeInOxy(i);
        if yo2(i+1)<0
            yo2(i+1)=0;
        end

    Rc2h4(i)=(kc2h4*(yo2(i)^ac2h4))*Wp*t/(V/1000);
         
        if PerfoSum <=0
            TransmissionRateEthy (i) =0;

        else
            TransmissionRateEthy(i)=(TotalTransoxy*t*(yo2(1)-yo2(i)))/V;
        end 

    TransmissionRateEthy(i)=-(TotalTransethy*t*(yc2h4(i)-yc2h4(1)))/V;
    ChangeInEthy(i)=Rc2h4(i)+TransmissionRateEthy(i);
    yc2h4(i+1)=yc2h4(i)+ ChangeInEthy(i);
        if yc2h4(i+1)<0
            yc2h4(i+1)=0;
        end
end

%oxygen and ethylene concentration inside a package over the time considering perforations

Oxy= yo2'; %oxygen inside package, mole fraction
Ethy=yc2h4'; %ethylene inside package, ppm
TimeInHours=timesinhr'; %cummulative time of experiment, h
TimesInDays= TimeInHours/24; %cummulative time of experiment, day

%calculation for respiration and ethylene production rate over the time

ko2m=ko2+zeros(length(Oxy),1);
rro2=ko2m.*(Oxy.^ao2); %mL kg-1 h-1


kc2h4m=kc2h4+zeros(length(Oxy),1); 
epr=kc2h4m.*(Oxy.^ac2h4); %µL kg-1 h-1


%Ethylwene scavenging effect for final ethylene concentration inside package after transmission

%initialize result matrix

resultethy = zeros(length(Ethy),1); 

for i = 2:length(Ethy)

    %perform operation on each row to get ethylene accumulation

    resultethy(i,1) = (Ethy(i,1)-(Ethy(i-1,1)-resultethy(i-1,1)))*(exp(-Kryan*t));

end
 
%amount of ethylene removed for each time step 

ethyleneremovedwithtime=Ethy-resultethy; 

threshold = qryanmax;

%code for a scavenger when it got finished to the full capacity 

if ethyleneremovedwithtime(length(Ethy))<=threshold
   
   %final ethylene accumulation with scavenger when capacity is not finished

   FinalEthy=resultethy; %ppm

   %remained scavenger capacity, ppm

   RemainedScavengerCapacity=(threshold-ethyleneremovedwithtime(length(Ethy)));

else         

   %Find the index of the first element that satisfies the threshold condition

   idx = find(ethyleneremovedwithtime > threshold, 1);

   %Split the matrix into two parts based on the threshold index
   
   firstpart1 = ethyleneremovedwithtime(1:idx-1);  
   secondpart1 = ethyleneremovedwithtime(idx:end);

   secondpart2=secondpart1-qryanmax;

   firstpart=resultethy(1:length(firstpart1));

   secondpart=firstpart(length(firstpart),1)+secondpart2;

   %final ethylene accumulation with scavenger when capacity is finished 

   FinalEthy=vertcat(firstpart, secondpart); %ppm
   

   %time at which scavenger finished its capacity, day

   TimeAtWhichScavengerFinishedItsCapacity=TimesInDays (length(firstpart));

end
FinalEthy(FinalEthy<0)=0;

%Finding the values of all for validation test from graph at time in day

Time_for_finding_oxygen_concentration = [0	0.152777778	0.208333333	1	1.1875	2.010416667	2.21875	2.989583333	3.170138889	4	4.208333333	6.211805556	8.038194444	9.048611111	10.02083333	11.01041667]; %day
Time_for_finding_ethylene_accumulation = [0	0.072916667	0.197916667	1.190972222	4.236111111	6.256944444	7.0625	8.288194444	9.090277778	10.0625]; %day

Ethylene_accumulation= zeros(length(Time_for_finding_ethylene_accumulation),1);
Actual_ethylene_produced= zeros(length(Time_for_finding_ethylene_accumulation),1);
Ethylene_production_rate= zeros(length(Time_for_finding_ethylene_accumulation),1);
Oxygen_concentration= zeros(length(Time_for_finding_oxygen_concentration),1);
Respiration_rate= zeros(length(Time_for_finding_oxygen_concentration),1);

for i=1: length(Time_for_finding_ethylene_accumulation)

[~,index] = min(abs(TimesInDays-Time_for_finding_ethylene_accumulation(i)));


if mryan <=0
    Ethylene_accumulation(i)= Ethy(index, 1); %ppm
    Actual_ethylene_produced (i)= Ethy(index, 1); %ppm

else
    Ethylene_accumulation(i)= FinalEthy(index, 1); %ppm
    Actual_ethylene_produced (i)= FinalEthy(index, 1); %ppm
end

Ethylene_production_rate(i)= epr(index, 1); %µL kg-1 h-1

end

for i=1: length(Time_for_finding_oxygen_concentration)

[~,index] = min(abs(TimesInDays-Time_for_finding_oxygen_concentration(i)));

Oxygen_concentration (i)= (Oxy(index, 1))*100; %percentage
Respiration_rate(i)= rro2(index, 1); %mL kg-1 h-1

end

%experimenatal data from validation test

Oxygen_validation=[20.9	17.111875	16.98125	14.499375	14.499375	14.499375	14.1075	14.499375	14.36875	14.238125	13.976875	14.36875	14.36875	15.283125	14.89125	14.89125];
Ethylene_validation=[0	0.0155	0.224	0.802	0.8015	0.975	0.9735	0.903	0.932	1.0175];

%standard deviation
Ethylene_validation_std=[0	0.02192031	0.002828427	0.004242641	0.001414214	0.018384776	0.01767767	0.009899495	0.018384776	0.028991378];

%R2 and RMSE of validation test (O2 and C2H4)

mean_oxygen = mean(Oxygen_validation);
mean_ethylene = mean(Ethylene_validation);
sse_oxygen = sum((Oxygen_validation' - Oxygen_concentration).^2); %sum of squared errors for oxygen
sse_ethylene = sum((Ethylene_validation' - Ethylene_accumulation).^2); %sum of squared errors for ethylene
tss_oxygen = sum((Oxygen_validation - mean_oxygen).^2); %total sum of squares for oxygen
tss_ethylene = sum((Ethylene_validation - mean_ethylene).^2); %total sum of squares for ethylene
R2_oxygen=(1-(sse_oxygen/tss_oxygen)); %R2 value for oxygen
R2_ethylene=(1-(sse_ethylene/tss_ethylene)); %R2 value for oxygen
rmse_oxygen = sqrt(sse_oxygen/length(Oxygen_validation)); %RMSE for oxygen
rmse_ethylene = sqrt(sse_ethylene/length(Ethylene_validation)); %RMSE for oxygen

%optimisation of perforation

yo2set=0.04; %required equilibrium oxygen concentration, mole fraction

syms drequiredo2

Eqo2=-((ko2*(yo2set^ao2))*Wp/V)+(((((T^1.724)*3600*1.00909*10^-5)/drequiredo2)*(0.78539816339*(drequiredo2^2)))*(0.209-yo2set)/V)==0;

Solo2=solve(Eqo2, drequiredo2);

do2=double(Solo2); %optimum perforation diameter for oxygen control, cm


yc2h4set=1.5; %required equilibrium ethylene concentration, ppm

drequiredc2h4=0.0200; %assumed perforation diameter to calculate number of perforations (Np), cm

syms Np

Eqc2h4=(((kc2h4*(yo2set^ac2h4))*Wp)/(V/1000))-(((0.04*AirVelocity)+(((2.4382*10^-6)*(T^1.81))/((AirVelocity^0.05)*(L^0.25)*(drequiredc2h4^0.8))))*(0.78539816339*(drequiredc2h4^2))*3600*(yc2h4set-0)*Np/V)==0;

Solc2h4=solve(Eqc2h4, Np);

Npfinal=double(Solc2h4);

dc2h4=Npfinal*drequiredc2h4; %optimum perforation diameter for ethylene control, cm

%percentage optimal for o2 and c2h4

percentageo2=0.80; %percentageo2=70%
percentagec2h4=1-percentageo2; %percentagec2h4=30%

%Optimal effective perforation diameter, cm

EffectivePerfoDia=((do2*percentageo2)+(dc2h4*percentagec2h4));

%graphs for oxygen & ethylene concentration with repsiration rate, transmission rate and scavenging effect

subplot(2,1,1)
    
   yyaxis left
   plot(TimesInDays,Oxy*100,'LineStyle', '-', 'LineWidth',1.5, 'color', 'b')
   xticks(0:2:Test_days);
   xlim([0 Test_days]);
   yticks(0:4:24);
   ylim([0 24]);
   xtickformat('%0.0f');
   ytickformat('%0.0f');
   hold on;
   plot(Time_for_finding_oxygen_concentration',Oxygen_validation', 'o', 'LineWidth',1.5,'color', 'b')
   xlabel('Time, days','fontsize',12, 'FontWeight', 'bold');
   ylabel('O_2, %','fontsize',12, 'color', 'b', 'FontWeight', 'bold');
   set(gca, 'YColor', 'b');
   hold on;
    
   yyaxis right
   plot(TimesInDays,rro2,'LineStyle', '-','LineWidth',1.5, 'color', 'r');
   xticks(0:2:Test_days);
   xlim([0 Test_days]);
   yticks(10:20:90);
   ylim([0 90]);
   xtickformat('%0.0f');
   ytickformat('%0.0f');
   xlabel('Time, days','fontsize',12, 'FontWeight', 'bold');
   ylabel('R_{O_2}, mL^3h^{-1}kg^{-1}','fontsize',12, 'color', 'r', 'FontWeight', 'bold');
   set(gca, 'YColor', 'r');
   legend('O_2 concentration','Experimental O_2','O_2 consumption rate', 'Location', 'northeast');
   legend('boxoff');
   legend('FontSize', 8);
   hold on;

subplot(2,1,2)
    
   yyaxis left
   plot(TimesInDays,FinalEthy,'LineStyle', '-', 'LineWidth',1.5, 'color', 'b');
   xticks(0:2:Test_days);
   xlim([0 Test_days]);
   yticks(0:1:4);
   ylim([0 4]);
   xtickformat('%0.1f');
   ytickformat('%0.0f');
   hold on;
   plot(Time_for_finding_ethylene_accumulation',Ethylene_validation', 'o', 'LineWidth',1.5, 'color', 'b')
   hold on;
   errorbar(Time_for_finding_ethylene_accumulation',Ethylene_validation', Ethylene_validation_std','LineWidth',1,'color', 'b')
   std = get(gca,'children');
   set(std(1),'LineStyle','none')
   xlabel('Time, days','fontsize',12, 'FontWeight', 'bold');
   ylabel('C_2H_4, ppm','fontsize',12, 'color', 'b', 'FontWeight', 'bold');
   set(gca, 'YColor', 'b');
   hold on,    
    
   yyaxis right
   plot(TimesInDays,epr,'LineStyle', '-','LineWidth',1.5, 'color', 'r')
   xticks(0:2:Test_days);
   xlim([0 Test_days]);
   yticks(0:0.4:2);
   ylim([0 2]);
   xtickformat('%0.0f');
   ytickformat('%0.1f');
   xlabel('Time, days','fontsize',12, 'FontWeight', 'bold');
   ylabel('R_{C_2H_4}, µL^3h^{-1}kg^{-1}','fontsize',12, 'color', 'r', 'FontWeight', 'bold');
   set(gca, 'YColor', 'r');
   legend('C_2H_4 accumulation','Experimental C_2H_4','standard deviation','C_2H_4 production rate', 'Location', 'northeast');
   legend('boxoff');
   legend('FontSize', 8);

%print a high resoltion image (600 dpi)

print(gcf,'Ethylene in avocado package', '-dpng');

%end