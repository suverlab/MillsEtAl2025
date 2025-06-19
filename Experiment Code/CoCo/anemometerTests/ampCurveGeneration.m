Fs = 20000;

daqreset;
aio =  daq('ni');
aio.Rate = Fs;
ao_mfc = addoutput(aio,"Dev2","ao0","Voltage"); % Signal to MFC
s_mfc = addoutput(aio, "Dev2", "ao2", 'Voltage'); % Solenoid Valve controlling wind from MFC
a_sig = addinput(aio,"Dev2","ai0",'Voltage');

r = 0.18796; % radius of TUBE: change based upon size of tube in which wind exits
tube_area = pi * r^2; % in cm^2
windminmax = [150]; % min and max windspeeds to achieve, in cm/s
cm_flow_rate_per_sec = windminmax * tube_area; % cm^3 / s
cm_flow_rate_per_min = cm_flow_rate_per_sec * 60; % cm^3 / min, mL / min
liters_per_min = cm_flow_rate_per_min / 1000;
minmax = liters_per_min * 5/2;

F_list = (5:5:500)/100;

dt = 1/Fs;
amp = (minmax(2) - minmax(1)) / 2;
adj = (minmax(2) + minmax(1)) / 2;

numpeaks = 10;

write(aio,[adj 8])
pause(5)
for i=1:length(F_list)

F=F_list(i);
triallength = ceil(numpeaks/F);
disp(triallength)
t = (0:dt:triallength-dt);
s_sig = 8 * ones(1, Fs*triallength);
mfc_sig = (amp * sin(2*pi*t*F))+adj;
daq_sig = vertcat(mfc_sig,s_sig)';
pause(2)

anemometerData = readwrite(aio, daq_sig,"OutputFormat","Matrix");

data(i).F = F;
[pks, locs] = findpeaks(anemometerData,'MinPeakProminence',0.03,'MinPeakDistance',2500);
data(i).amp = mean(pks);

write(aio,[adj 8])
end

save('ampFreqCurveData','data')