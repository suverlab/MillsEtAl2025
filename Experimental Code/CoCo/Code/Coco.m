function Coco(condition, expnum, min_age, max_age)
%% condition check
wind = strcmp(condition,'wind');
visual = strcmp(condition,'visual');
both = strcmp(condition,'both');
none = strcmp(condition,'none');

%% TCP-IP Server Setup
[~,hostname] = system('hostname');
hostname = string(strtrim(hostname));
address = resolvehost(hostname,"address");
server = tcpserver(address,5000,"Timeout",30);
    
disp(['Launch CocoVideoClient.m now! Press any button in this command window ' ...
     'to continue once visual stimulus is running...'])
pause()


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

trial_time = 19;
video_time = 16;
baseline_time = 6;
osc_time = 12;

CAM_TRIG = 2;
numFrames = FPS * video_time;

%tcp_freqs = [1 2 3 5 7 11 13 17 19 23 29 31 37 41];
%opticfreqs  = [0.1 0.2 0.3 0.5 0.7 1.1 1.3 1.7 1.9 2.3 2.9 3.1 3.7 4.1];
%ampV  = [0.77 0.8 0.835 0.915 0.99 1.21 1.335 1.62 1.76 2.09 2.15 2.37 2.05 2.46];

tcp_freqs = [3 13 23];
opticfreqs = [0.3 1.3 2.3];
ampV = [0.835 1.335 2.09];


baseV = 2.4972571; % 150 cm/s

trials_per_block = length(opticfreqs);
blocks = 12;
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
photodiode = addinput(aio, "Dev2", "ai6","Voltage");
photodiode.TerminalConfig = 'SingleEnded';

write(aio, [baseV 0 0])

trigger = addtrigger(aio,"Digital","StartTrigger","External","Dev2/PFI0");
trigger.Condition = "RisingEdge";

for b=1:blocks
    % RNG Initialization
    rng("shuffle");
    block_freqs_idx = randperm(length(opticfreqs));
    block_ampV = ampV(block_freqs_idx);
    block_tcp_freqs = tcp_freqs(block_freqs_idx);
    block_opticfreqs = opticfreqs(block_freqs_idx);
    for i = 1:length(block_freqs_idx)
        
        j = ((b-1) * length(block_freqs_idx)) + i;
        
        F = block_opticfreqs(i);
        t = (0:dt:osc_time-dt);

        pre_sig = baseV * ones(aio.Rate * baseline_time,1);
        end_sig = baseV * ones(aio.Rate,1);
        if (wind | both)            
            main_sig = ((block_ampV(i) * sin(2*pi*t*F))+baseV)';
            mfc_sig = vertcat(pre_sig,main_sig,end_sig);
        elseif (visual | none) 
            main_sig = baseV * ones(aio.Rate * osc_time,1);
            mfc_sig = vertcat(pre_sig,main_sig,end_sig);
        end
    
        sol_sig = ones(aio.Rate * trial_time,1) * 8;
        sol_sig((Fs*18)+1001:end,1) = 0;
        cam_sig = ones(Fs * trial_time,1) * CAM_TRIG;
        cam_sig(1:2*Fs) = 0;
        cam_sig((Fs*18)+1:end,1) = 0;

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

        if (visual | both)
            writeline(server, string(block_tcp_freqs(i)))
        elseif (wind | none)
            writeline(server, string(100))
        end

        movieSelection = [];
        while isempty(movieSelection)
            movieSelection = readline(server);
        end
        movieSelection = [];
        
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

        start(vid); preview(vid);
        trialdata = readwrite(aio, daqSeq,"OutputFormat","Matrix");

        data(j).pufferSignal = trialdata(2*Fs+1:end-Fs,2);
        data(j).tachometerSignal = trialdata(2*Fs+1:end-Fs,1);
        data(j).photodiodeSignal = trialdata(1:end-Fs,3);

        save(saveStr, 'data')

        % Wait for continue signal, send confirmation
        cc = [];
        while isempty(cc)
            cc = readline(server);
        end

        writeline(server, "continue")

    end
    disp('-----------')
end
disp('Data collection complete! :)')
end