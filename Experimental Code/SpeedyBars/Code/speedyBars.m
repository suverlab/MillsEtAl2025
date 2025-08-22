function speedyBars(condition, expnum, min_age, max_age)

%% TCP-IP Server Setup
[~,hostname] = system('hostname');
hostname = string(strtrim(hostname));
address = resolvehost(hostname,"address");
server = tcpserver(address,5000,"Timeout",30);

disp(['Launch videoClient.m now! Press any button in this command window' ...
    'to continue once visual stimulus is running...'])
pause()

%% Directory Creation
dateStr = string(datetime('today','Format','uuuu_MM_dd'));
dirStr = strcat('..\Data\',dateStr);
if ~isfolder(dirStr)
    mkdir(dirStr)
end
saveStr = strcat('C:\Users\suverlab\Desktop\Kevin\Vanderbilt\SuverLab - SpeedyBars\Data\',dateStr,'\',dateStr,'_E',num2str(expnum));
directory = dir(strcat(saveStr, '.mat'));

%% Constants and Trial Creation

FPS = 60;
Fs = 20000;
adjust_time = 2;
record_time = 6;
trial_time = adjust_time + record_time;
CAM_TRIG = 2;
trials_per_stimulus = 5;
numFrames = FPS * trial_time;

% RNG Initialization
s = rng("shuffle");

opticspeeds = [0 5 10 15 20 25 30 35 40 45 50 100];
extended_ids = repmat(opticspeeds, 1, trials_per_stimulus);
by_trial_id = extended_ids(randperm(length(extended_ids)));

num_trials = length(opticspeeds) * trials_per_stimulus;

%% DAQ Setup
daqreset;

aio =  daq('ni');
aio.Rate = Fs;
ao_mfc = addoutput(aio,"Dev2","ao0","Voltage"); % Signal to MFC
s_mfc = addoutput(aio, "Dev2", "ao2", 'Voltage'); % Solenoid Valve controlling wind from MFC
trig_cam = addoutput(aio, "Dev2","ao3","Voltage"); % Camera Trigger Signal

tachometer = addinput(aio,"Dev2","ai0","Voltage"); % Tachometer Signal
% tachometer.TerminalConfig = 'SingleEnded';
puffer = addinput(aio, "Dev2", "ai5","Voltage"); % Signal from Puffer
puffer.TerminalConfig = 'SingleEnded';
photodiode = addinput(aio, "Dev2", "ai2","Voltage");
photodiode.TerminalConfig = 'SingleEnded';

mfc_sig = zeros(aio.Rate * trial_time,1);
sol_sig = ones(aio.Rate * trial_time,1) * 8;
cam_sig = ones(aio.Rate * trial_time,1) * CAM_TRIG;
daqSeq = cat(2,mfc_sig,sol_sig,cam_sig);

%% Trial LOOP
for i=1:num_trials

disp(strcat('Trial num = ',num2str(i)))

data(i).date = dateStr;
data(i).expnumber = expnum;
data(i).condition = condition;
data(i).min_age = min_age;
data(i).max_age = max_age;
data(i).samplerate = Fs;
data(i).adjust_time = adjust_time; % Time during which the MFC adjusts to new speed (comes first)
data(i).record_time = record_time; % Time in which steady state wind should be measured (comes second)
data(i).fps = FPS;
data(i).nframes = numFrames;
data(i).trial = i;
data(i).stimulus = by_trial_id(i);

% Send and recieve trial selection
writeline(server, string(by_trial_id(i)))
movieSelection = [];
while isempty(movieSelection)
    movieSelection = readline(server);
end
movieSelection = [];

% Video Setup

if i < 10
    trialstr = strcat('0', num2str(i));
else
    trialstr = num2str(i);
end 

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
vid.FramesPerTrigger = numFrames;
vid.LoggingMode = 'disk';
vidfile = vidSaveStr;
logfile = VideoWriter(vidfile, 'Motion JPEG AVI');
set(logfile,'FrameRate',FPS)
vid.diskLogger = logfile;
triggerconfig(vid,'hardware','risingEdge','externalTrigger')

% Create and send start timer data
c = datetime('now');
startTime = c + seconds(6);
writeline(server, string(startTime))
returnTime = [];
while isempty(returnTime)
   returnTime = readline(server);
end
t = timer('StartFcn', @(~,~)disp('Started.'));
t.TimerFcn = {@runDAQ, aio, daqSeq, vid};
startat(t, returnTime);


% Wait for continue signal, send confirmation
cc = [];
while isempty(cc)
    cc = readline(server);
end

writeline(server, "continue")
end

%% Experiment Wrapup
disp('Done!')

%% runDAQ function

function runDAQ(~,~,aio,daqSeq, vid)
   
    disp(datestr(now,'dd-mm-yyyy HH:MM:SS FFF'))

    start(vid)
    trialdata = readwrite(aio, daqSeq,"OutputFormat","Matrix");

    write(aio, [0 0 0])
    
    data(i).pufferSignal = trialdata(:,2);
    data(i).tachometerSignal = trialdata(:,1);
    data(i).photodiodeSignal = trialdata(:,3);
    save(saveStr, 'data')

    pause(3)
end


end

