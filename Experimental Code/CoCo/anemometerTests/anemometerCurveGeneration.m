Fs = 20000;

daqreset;
aio =  daq('ni');
aio.Rate = Fs;
ao_mfc = addoutput(aio,"Dev2","ao0","Voltage"); % Signal to MFC
s_mfc = addoutput(aio, "Dev2", "ao2", 'Voltage'); % Solenoid Valve controlling wind from MFC
a_sig = addinput(aio,"Dev2","ai0",'Voltage');

r = 0.18796; % radius of TUBE: change based upon size of tube in which wind exits
tube_area = pi * r^2; % in cm^2
windspeeds = 0:300; % min and max windspeeds to achieve, in cm/s
cm_flow_rate_per_sec = windspeeds * tube_area; % cm^3 / s
cm_flow_rate_per_min = cm_flow_rate_per_sec * 60; % cm^3 / min, mL / min
liters_per_min = cm_flow_rate_per_min / 1000;
mfc_values = liters_per_min * 5/2;

triallength = 12;
adjust_time = 3;

s_sig = 8 * ones(1, Fs*triallength);

for i=1:length(mfc_values)
    voltage = mfc_values(i);
    ws = windspeeds(i);
    data(i).windspeed = ws;
    data(i).voltage = voltage;
    disp(ws)
    disp(voltage)
    mfc_sig = voltage * ones(1, Fs*triallength);
    daq_sig = vertcat(mfc_sig,s_sig)';

    aSig = readwrite(aio,daq_sig,"OutputFormat","Matrix");
    data(i).anemVal = mean(aSig(adjust_time*Fs:end));

end

save('anemometerCurveAcrossAllWindspeeds_new','data')