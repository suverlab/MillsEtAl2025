
%% TCP-IP Server Setup

[~,hostname] = system('hostname');
hostname = string(strtrim(hostname));
address = resolvehost(hostname,"address");
server = tcpserver(address,5000,"Timeout",30);
    
disp(['Launch photodiodeClient.m now! Press any button in this command window ' ...
     'to continue once visual stimulus is running...'])
pause()



%% Constants and Trial Creation

FPS = 60;
Fs = 20000;
dt = 1/Fs;

cutoff_time = 2;
video_time = 10;
trial_time = cutoff_time + video_time;

mfc_sig = 2.5 * ones(Fs*trial_time,1);
s_sig = zeros(Fs*trial_time,1);
s_sig(20000:40000) = 8;
s_sig(200000:220000) = 8;
signal = horzcat(mfc_sig, s_sig);
global data
%% DAQ setup
daqreset;

aio =  daq('ni');
aio.Rate = Fs;
sig = addoutput(aio,"Dev2","ao0","Voltage"); % Signal to MFC
s_mfc = addoutput(aio, "Dev2", "ao2", 'Voltage'); % Solenoid Valve controlling wind from MFC
%trig_cam = addoutput(aio, "Dev2","ao3","Voltage"); % Camera Trigger Signal

%tachometer = addinput(aio,"Dev2","ai0","Voltage"); % Tachometer Signal
% tachometer.TerminalConfig = 'SingleEnded';
%puffer = addinput(aio, "Dev2", "ai0","Voltage"); % Signal from Puffer
%puffer.TerminalConfig = 'SingleEnded';
photodiode = addinput(aio, "Dev2", "ai0","Voltage");
photodiode.TerminalConfig = 'SingleEnded';
anemometer = addinput(aio, "Dev2", "ai5","Voltage");
anemometer.TerminalConfig = 'SingleEnded';

num_reps = 5;

for n=1:num_reps
    data(n).rep = n;
    writeline(server, string(1))
    movieSelection = [];
    while isempty(movieSelection)
        movieSelection = readline(server);
    end
    movieSelection = [];
 


    c = datetime('now');
    startTime = c + seconds(6);
    sendTime = startTime;
    writeline(server, string(sendTime))
    returnTime = [];
    while isempty(returnTime)
        returnTime = readline(server);
    end
    t = timer('StartFcn', @(~,~)disp('Started.'));
    t.TimerFcn = {@runDAQ, aio, signal,n};
    startat(t, returnTime);


            % Wait for continue signal, send confirmation
            cc = [];
            while isempty(cc)
                cc = readline(server);
            end

            writeline(server, "continue")
end


function runDAQ(~,~,aio,signal,n)
   
    disp(datestr(now,'dd-mm-yyyy HH:MM:SS FFF'))

    
    trialdata = readwrite(aio, signal,"OutputFormat","Matrix");
    global data
    data(n).photodiodeSignal = trialdata(:,1);
    data(n).anemometerSignal = trialdata(:,2);
    save('photodiodeData2.mat','data')
    pause(2)
end
