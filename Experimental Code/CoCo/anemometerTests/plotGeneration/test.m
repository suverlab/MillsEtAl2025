

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

F_list = [0.1:0.1:5];
triallength = 10;
dt = 1/Fs;
t = (0:dt:triallength-dt);
amp = (minmax(2) - minmax(1)) / 2;
adj = (minmax(2) + minmax(1)) / 2;

write(aio,[minmax(2) 0])
pause(2)

s_sig_max = 8 * ones(1, Fs*triallength);
mfc_sig_max = minmax(2) * ones(1, Fs*triallength);
daq_sig_max = vertcat(mfc_sig_max,s_sig_max)';

maximum = readwrite(aio,daq_sig_max,"OutputFormat","Matrix");

avg_max = mean(maximum(10000:end));


write(aio,[adj 0])
pause(2)


s_sig_baseline = 8 * ones(1, Fs*triallength);
mfc_sig_baseline = adj * ones(1, Fs*triallength);
daq_sig_baseline = vertcat(mfc_sig_baseline,s_sig_baseline)';

baseline = readwrite(aio,daq_sig_baseline,"OutputFormat","Matrix");

avg_baseline = mean(baseline(10000:end));

write(aio,[adj 0])
pause(5)
for i=1:length(F_list)

F=F_list(i);
s_sig = 8 * ones(1, Fs*triallength);

mfc_sig = (amp * sin(2*pi*t*F))+adj;

daq_sig = vertcat(mfc_sig,s_sig)';


anemometerData = readwrite(aio, daq_sig,"OutputFormat","Matrix");

data(i).F = F;
data(i).anemometerData = anemometerData;
data(i).mfcSig = mfc_sig;

[~, locs1] = findpeaks(anemometerData(1100:end),'MinPeakProminence',0.03,'MinPeakDistance',2500);
[~, locs2] = findpeaks(mfc_sig,'MinPeakProminence',0.5);

data(i).avgPhaseLag = mean(locs1(:) - locs2(:));

percentAmp = (max(anemometerData(10000:end)) - avg_baseline) / (avg_max-avg_baseline);
data(i).percentAmp = percentAmp;

[fitObj, gof] = fit(anemometerData, mfc_sig', 'sin1');
data(i).gof = gof;

save('anemometerData','data')

write(aio,[adj 0])
pause(3)
end