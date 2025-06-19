client = tcpclient("10.18.27.80",5000,"Timeout",30);

opticfreqs = [1 2 3 5 7 11 13 17 19 23 29 31 37 41];

blocks = 4;
trials_per_block = length(opticfreqs);
num_trials = trials_per_block * blocks;

sca;
close all;

screens=Screen('Screens');
Screen('Preference', 'SkipSyncTests',1);
screenNumber=max(screens);
black=BlackIndex(screenNumber);

[w, screenRect] = Screen('OpenWindow',screenNumber, black);
[screenXpixels, screenYpixels] = Screen('WindowSize', w);
[xCenter, yCenter] = RectCenter(screenRect);

for i=1:num_trials

movieSelection = [];
while isempty(movieSelection)
    movieSelection = readline(client);
end

writeline(client, movieSelection)

if movieSelection == "1"
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - CoCo/Code/0.1_Hz_sinwave.mp4';
elseif movieSelection == "101"
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - CoCo/Code/0.1_Hz_sinwave_lowAmp.mp4';
elseif movieSelection == "3"
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - CoCo/Code/0.3_Hz_sinwave.mp4';
elseif movieSelection == "103"
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - CoCo/Code/0.3_Hz_sinwave_lowAmp.mp4';
elseif movieSelection == "7"
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - CoCo/Code/0.7_Hz_sinwave.mp4';
elseif movieSelection == "107"
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - CoCo/Code/0.7_Hz_sinwave_lowAmp.mp4';
elseif movieSelection == "13"
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - CoCo/Code/1.3_Hz_sinwave.mp4';
elseif movieSelection == "113"
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - CoCo/Code/1.3_Hz_sinwave_lowAmp.mp4';
elseif movieSelection == "23"
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - CoCo/Code/2.3_Hz_sinwave.mp4';
elseif movieSelection == "123"
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - CoCo/Code/2.3_Hz_sinwave_lowAmp.mp4';
elseif movieSelection == "31"   
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - CoCo/Code/3.1_Hz_sinwave.mp4';
elseif movieSelection == "131"   
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - CoCo/Code/3.1_Hz_sinwave_lowAmp.mp4';
elseif movieSelection == "41"   
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - CoCo/Code/4.1_Hz_sinwave.mp4';
elseif movieSelection == "141"   
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - CoCo/Code/4.1_Hz_sinwave_lowAmp.mp4';
end

movieSelection = [];
m = Screen('OpenMovie', w, movie);
Screen('PlayMovie', m, 1);


startTime = [];

while isempty(startTime)
    startTime = readline(client);
end

writeline(client, startTime)

t = timer('StartFcn', @(~,~)disp('Started.'));
t.TimerFcn = {@runVideo, w, m,client};
startat(t, datetime(startTime));

cc = [];
while isempty(cc)
    cc = readline(client);
end
end

sca;
close all;
disp('Done!')

function runVideo(~,~,w,m,client)
    disp(datestr(now,'dd-mm-yyyy HH:MM:SS FFF'))

while 1
    % Wait for next movie frame, retrieve texture handle to it
    tex = Screen('GetMovieImage', w, m);
        
    % Valid texture returned? A negative value means end of movie reached:
    if tex<=0
        % We're done, break out of loop:
        break;
    end
        
    % Draw the new texture immediately to screen:
    Screen('DrawTexture', w, tex);
      
    % Update display:
    Screen('Flip', w);
        
    % Release texture:
    Screen('Close', tex);
end
    Screen('PlayMovie', m, 0);
    
    Screen('CloseMovie', m);

    writeline(client, "continue")

end

