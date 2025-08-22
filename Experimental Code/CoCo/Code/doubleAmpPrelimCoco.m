function doubleAmpPrelimCoco(condition, expnum, min_age, max_age)
%% condition check
wind = strcmp(condition,'wind');
visual = strcmp(condition,'visual');
both = strcmp(condition,'both');

%% TCP-IP Server Setup
if (visual | both)
[~,hostname] = system('hostname');
hostname = string(strtrim(hostname));
address = resolvehost(hostname,"address");
server = tcpserver(address,5000,"Timeout",30);
    
disp(['Launch CocoVideoClient.m now! Press any button in this command window ' ...
     'to continue once visual stimulus is running...'])
pause()
end

%% Directory Creation
dateStr = string(datetime('today','Format','uuuu_MM_dd'));
dirStr = strcat('..\Data\',dateStr);
if ~isfolder(dirStr)
   mkdir(dirStr)
end
saveStr = strcat('C:\Users\suverlab\Desktop\Kevin\Vanderbilt\SuverLab - CoCo\Data\',dateStr,'\',dateStr,'_E',num2str(expnum));
directory = dir(strcat(saveStr, '.mat'));

%% Constants and Trial Creation

FPS = 60;
Fs = 20000;
dt = 1/Fs;

cutoff_time = 2;
video_time = 10;
trial_time = cutoff_time + video_time;

CAM_TRIG = 2;
numFrames = FPS * video_time;

tcp_freqs = [1 101 3 103 7 107 13 113 23 123 31 131 41 141];

opticfreqs  = [0.1 0.1 0.3 0.3 0.7 0.7 1.3 1.3 2.3 2.3 3.1 3.1 4.1 4.1];
ampCon = [1 2 1 2 1 2 1 2 1 2 1 2 1 2];
ampV  = [0.77 0.39 0.835 0.43 0.99 0.515 1.335 0.715 2.09 1.09 2.37 1.28 2.46 1.26];
if visual
    baseV = 0;
else
    baseV = 2.4972571; % 150 cm/s
end

trials_per_block = length(opticfreqs);
blocks = 4;
num_trials = trials_per_block * blocks;

%% DAQ setup
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
%photodiode = addinput(aio, "Dev2", "ai2","Voltage");
%photodiode.TerminalConfig = 'SingleEnded';

if wind
    write(aio, [baseV 8 0])
end

for b=1:blocks
    % RNG Initialization
    rng("shuffle");
    block_freqs_idx = randperm(length(opticfreqs));
    block_ampV = ampV(block_freqs_idx);
    block_tcp_freqs = tcp_freqs(block_freqs_idx);
    block_opticfreqs = opticfreqs(block_freqs_idx);
    block_ampCon = ampCon(block_freqs_idx);
    for i = 1:length(block_freqs_idx)
        
        j = ((b-1) * length(block_freqs_idx)) + i;
        
        F = block_opticfreqs(i);
        t = (0:dt:trial_time-dt);

        if (wind | both)
            mfc_sig = ((block_ampV(i) * sin(2*pi*t*F))+baseV)';
        elseif visual   
            mfc_sig = zeros(aio.Rate * trial_time,1);
        end
    
        sol_sig = ones(aio.Rate * trial_time,1) * 8;
        cam_sig = ones(aio.Rate * trial_time,1) * CAM_TRIG;
        cam_sig(1:cutoff_time*Fs) = 0;
        daqSeq = cat(2,mfc_sig,sol_sig,cam_sig);
        
        disp(strcat('Block num = ',num2str(b)))
        disp(strcat('Trial num = ',num2str(i)))

        data(j).date = dateStr;
        data(j).expnumber = expnum;
        data(j).condition = condition;
        data(j).min_age = min_age;
        data(j).max_age = max_age;
        data(j).samplerate = Fs;
        data(j).fps = FPS;
        data(j).nframes = numFrames;
        data(j).trialLength = video_time;
        data(j).block = b;
        data(j).block_trial = i;
        data(j).trialnum = j;
        data(j).stimulus = block_opticfreqs(i);
        data(j).ampCondition = block_ampCon(i);

        if (visual | both)
            writeline(server, string(block_tcp_freqs(i)))
            movieSelection = [];
            while isempty(movieSelection)
                movieSelection = readline(server);
            end
            movieSelection = [];
        end

        if j < 10
            trialstr = strcat('0', num2str(j));
        else
            trialstr = num2str(j);
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

        if wind
            pause(2)
            preview(vid)
            start(vid)
            trialdata = readwrite(aio, daqSeq,"OutputFormat","Matrix");

            write(aio, [baseV 8 0])
    
            data(j).pufferSignal = trialdata(cutoff_time*Fs+1:end,2);
            data(j).tachometerSignal = trialdata(cutoff_time*Fs+1:end,1);
            % data(i).photodiodeSignal = trialdata(:,3);
            save(saveStr, 'data')
            disp('Puff now!')
            pause(2)
        elseif (visual | both)
            c = datetime('now');
            startTime = c + seconds(6);
            sendTime = startTime - milliseconds(10);
            writeline(server, string(sendTime))
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

    end
end

write(aio, [0 0 0])
disp('Data collection complete! :)')

function runDAQ(~,~,aio,daqSeq, vid)
   
    disp(datestr(now,'dd-mm-yyyy HH:MM:SS FFF'))
    preview(vid)
    start(vid)
    trialdata = readwrite(aio, daqSeq,"OutputFormat","Matrix");

    write(aio, [baseV 8 0])
    
    
    data(j).pufferSignal = trialdata(cutoff_time*Fs+1:end,2);
    data(j).tachometerSignal = trialdata(cutoff_time*Fs+1:end,1);
    % data(i).photodiodeSignal = trialdata(:,3);
    save(saveStr, 'data')

    pause(2)
end

end