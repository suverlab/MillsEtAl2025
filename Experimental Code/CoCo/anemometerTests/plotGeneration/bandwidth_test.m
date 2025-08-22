Fs = 20000;

daqreset;
aio =  daq('ni');
aio.Rate = Fs;
ao_mfc = addoutput(aio,"Dev2","ao0","Voltage"); % Signal to MFC
s_mfc = addoutput(aio, "Dev2", "ao2", 'Voltage'); % Solenoid Valve controlling wind from MFC
a_sig = addinput(aio,"Dev2","ai0",'Voltage');

r = 0.18796; % radius of TUBE: change based upon size of tube in which wind exits
tube_area = pi * r^2; % in cm^2
windminmax = [100 250]; % min and max windspeeds to achieve, in cm/s
cm_flow_rate_per_sec = windminmax * tube_area; % cm^3 / s
cm_flow_rate_per_min = cm_flow_rate_per_sec * 60; % cm^3 / min, mL / min
liters_per_min = cm_flow_rate_per_min / 1000;
minmax = liters_per_min * 5/2;

adj = (minmax(2) + minmax(1)) / 2;

triallength = 10;
s_sig_off = zeros(1, Fs*triallength/2);
s_sig_max = 8 * ones(1, Fs*triallength/2);
s_sig = horzcat(s_sig_off,s_sig_max);
mfc_sig = adj * ones(1, Fs*triallength);
daq_sig= vertcat(mfc_sig,s_sig)';

anem = readwrite(aio,daq_sig,"OutputFormat","Matrix");

s_sig = 8 * ones(1, Fs*triallength);
mfc_sig_pre = adj * ones(1, Fs*triallength/2);
mfc_sig_post = minmax(2) * ones(1, Fs*triallength/2);
mfc_sig = horzcat(mfc_sig_pre,mfc_sig_post);

daq_sig2= vertcat(mfc_sig,s_sig)';

write(aio, [adj, 0]);
pause(5)
anem2 = readwrite(aio,daq_sig2,"OutputFormat","Matrix");
