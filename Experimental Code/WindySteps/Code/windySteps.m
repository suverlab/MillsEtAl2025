function windySteps(condition, expnum, min_age, max_age)

%% Defining constants
FPS = 60; % framerate
Fs = 20000; % sampling rate
CAM_TRIG = 2;

%% Directory Creation
dateStr = string(datetime('today','Format','uuuu_MM_dd'));
dirStr = strcat('..\Data\',dateStr);
if ~isfolder(dirStr)
    mkdir(dirStr)
end

%% DAQ Initialization

daqreset;

aio =  daq('ni');
aio.Rate = Fs;
ao_mfc = addoutput(aio,"Dev2","ao0","Voltage"); % Signal to MFC
opto = false;
if strcmp(condition,'silenced')
    opto = true;
elseif strcmp(condition,'silenced_dark')
    opto = true;
elseif strcmp(condition,'18D07')
    opto = true;
elseif strcmp(condition,'74C10')
    opto = true;
elseif strcmp(condition,'ChrimCS')
    opto = true;
elseif strcmp(condition,'silencedCS')
    opto = true;
elseif strcmp(condition,'silencedCS_glued')
    opto = true;
end

if opto
trig_opto = addoutput(aio,"Dev2","ao1","Voltage"); % Opto triggering
end
s_mfc = addoutput(aio, "Dev2", "ao2", 'Voltage'); % Solenoid Valve controlling wind from MFC
trig_cam = addoutput(aio, "Dev2","ao3","Voltage"); % Camera Trigger Signal

tachometer = addinput(aio,"Dev2","ai0","Voltage"); % Tachometer Signal
% tachometer.TerminalConfig = 'SingleEnded';
puffer = addinput(aio, "Dev2", "ai5","Voltage"); % Signal from Puffer
puffer.TerminalConfig = 'SingleEnded';

%% Stimulus creation

r = 0.18796; % radius of TUBE: change based upon size of tube in which wind exits
tube_area = pi * r^2; % in cm^2
windspeeds = [0 50 100 150 200 250 300]; % various windspeeds to achieve, in cm/s
cm_flow_rate_per_sec = windspeeds * tube_area; % cm^3 / s
cm_flow_rate_per_min = cm_flow_rate_per_sec * 60; % cm^3 / min, mL / min
liters_per_min = cm_flow_rate_per_min / 1000;
mfc_values = liters_per_min * 5/2;

adjust_time = 3; % Non-recording time period at certain MFC value
record_time = 3; % recording time period at certain MFC value
mfc_time = adjust_time + record_time;

% RNG Initialization
s = rng("shuffle");

% UP Staircase
mfc_volt_sig_up = [];
for i=1:length(mfc_values)
signal = ones(aio.Rate * mfc_time,1) * mfc_values(i);
mfc_volt_sig_up = vertcat(mfc_volt_sig_up, signal); %#ok<*AGROW>
end
mfc_volt_sig_up(mfc_volt_sig_up == 0) = mfc_values(2);
mfc_volt_sig_up = vertcat(zeros(aio.Rate * mfc_time,1), mfc_volt_sig_up);

sol_sig_up = ones(length(mfc_volt_sig_up),1) * 8;
sol_sig_up(1:(mfc_time*2*aio.Rate)) = 0;

% DOWN Staircase
mfc_volt_sig_down = [];
mfc_values_inverse = flip(mfc_values);
for i=1:length(mfc_values)
signal = ones(aio.Rate * mfc_time,1) * mfc_values_inverse(i);
mfc_volt_sig_down = vertcat(mfc_volt_sig_down, signal); %#ok<*AGROW>
end
mfc_volt_sig_down = vertcat(ones(aio.Rate*mfc_time,1)*mfc_values(end), mfc_volt_sig_down);

sol_sig_down = ones(length(mfc_volt_sig_up),1) * 8;
sol_sig_down(1:(mfc_time*aio.Rate)) = 0;
sol_sig_down(end-(aio.Rate*mfc_time)+1:end) = 0;

% opto triggering if used

opto_sig = ones(length(mfc_volt_sig_down), 1) * 2;
opto_sig(1:(aio.Rate*mfc_time)) = 0;

% Camera Triggering

cam_sig = ones(length(mfc_volt_sig_down), 1) * CAM_TRIG;
cam_sig(1:(aio.Rate*mfc_time)) = 0;

% Signal concatenation

if opto
    out_vector_up = cat(2,mfc_volt_sig_up,opto_sig,sol_sig_up,cam_sig);
    out_vector_down = cat(2, mfc_volt_sig_down,opto_sig,sol_sig_down,cam_sig);
else
    out_vector_up = cat(2,mfc_volt_sig_up,sol_sig_up,cam_sig);
    out_vector_down = cat(2, mfc_volt_sig_down,sol_sig_down,cam_sig);
end
% Order Generation (1 = up, 2 = down)
trial_order = [1, 1, 1, 1, 1, 2, 2, 2, 2, 2];
randomized_trial_order = trial_order(randperm(length(trial_order)));

%% Data Struct creation
saveStr = strcat('C:\Users\suverlab\Desktop\Kevin\Vanderbilt\SuverLab - WindySteps\Data\',dateStr,'\',dateStr,'_E',num2str(expnum));
directory = dir(strcat(saveStr, '.mat'));

%% Running trials
disp('Beginning first trial...')

for i=1:length(randomized_trial_order)

    disp(strcat('Trial num = ',num2str(i)))

    data(i).date = char(dateStr);
    data(i).expnumber = expnum;
    data(i).condition = condition;
    data(i).min_age = min_age;
    data(i).max_age = max_age;
    data(i).samplerate = Fs;
    data(i).adjust_time = adjust_time; % Time during which the MFC adjusts to new speed (comes first)
    data(i).record_time = record_time; % Time in which steady state wind should be measured (comes second)
    data(i).fps = FPS;
    data(i).nframes = data(i).fps*(adjust_time+record_time)*length(mfc_values);
    data(i).trial = i;
    data(i).stimType = randomized_trial_order(i);

    if i < 10
        trialstr = strcat('0', num2str(i));
    else
        trialstr = num2str(i);
    end

    if i == 1
        if opto
            write(aio, [0 0 0 0]); % Initialize DAQ to nothing
        else
            write(aio, [0 0 0]);
        end
        disp('Puff now!')
        pause(2)
    end

    if randomized_trial_order(i) == 1
        out_vector = out_vector_up;
    elseif randomized_trial_order(i) == 2
        out_vector = out_vector_down;
    else
        disp('Check your trial order vector. Must be filled with ones and twos...')
        break;
    end

    % Camera Initialization

    imaqreset;
    imaqmex('feature','-limitPhysicalMemoryUsage',false);

    vidSaveStr = strcat(saveStr, '_Video_Dorsal_', trialstr);
    vid = videoinput('dcam',1,'Y8_640x480'); % Coronal (x) Camera
    src = getselectedsource(vid);
    src.ShutterMode = 'manual'; %this is important to maintain proper framerate!
    src.Shutter = 800; %any higher than this and we get < 60Hz framerate UPDATE!!!
    src.AutoExposure = 155;
    src.GainMode = 'manual';
    src.Gain = 0;
    src.Brightness = 0;
    src.FrameRate = num2str(FPS);
    vid.FramesPerTrigger = data(i).nframes;
    vid.LoggingMode = 'disk';
    vidfile = vidSaveStr;
    logfile = VideoWriter(vidfile, 'Motion JPEG AVI');
    set(logfile,'FrameRate',FPS)
    vid.diskLogger = logfile;
    triggerconfig(vid,'hardware','risingEdge','externalTrigger')
    
    preview(vid)

    start(vid)
    trialdata = readwrite(aio, out_vector,"OutputFormat","Matrix");
    
    data(i).pufferSignal = trialdata(:,2);
    data(i).tachometerSignal = trialdata(:,1);
    
    [b,a] = butter(2,[150 250]/(Fs/2));

    dataOut = filter(b,a,squeeze(trialdata(:,1)));
    data_smooth = smoothdata(dataOut,'sgolay');

    data(i).tachometerSignal_smoothed = data_smooth;
    
    if opto
        write(aio, [0 0 0 0])
    else
        write(aio, [0 0 0])
    end

    save(saveStr, 'data')
    if i ~= 10
        disp('Puff now!')
    end
    pause(2)
    
end

disp('Data Collection Complete! :)')

end