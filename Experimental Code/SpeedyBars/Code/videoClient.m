client = tcpclient("10.18.27.80",5000,"Timeout",30);

opticspeeds = [0 5 10 15 20 25 30 35 40 45 50 100];
trials_per_stimulus = 5;
num_trials = length(opticspeeds) * trials_per_stimulus;

sca;
close all;

screens=Screen('Screens');
Screen('Preference', 'SkipSyncTests',1);
screenNumber=max(screens);
black=BlackIndex(screenNumber);

[w, screenRect] = Screen('OpenWindow',screenNumber, black);
[screenXpixels, screenYpixels] = Screen('WindowSize', w);
[xCenter, yCenter] = RectCenter(screenRect);

movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - SpeedyBars/Code/30.mp4';

for i=1:num_trials

movieSelection = [];
while isempty(movieSelection)
    movieSelection = readline(client);
end

writeline(client, movieSelection)

if movieSelection == "0"
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - SpeedyBars/Code/0.mp4';
elseif movieSelection == "5"
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - SpeedyBars/Code/5.mp4';
elseif movieSelection == "10"
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - SpeedyBars/Code/10.mp4';
elseif movieSelection == "15"
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - SpeedyBars/Code/15.mp4';
elseif movieSelection == "20"
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - SpeedyBars/Code/20.mp4';
elseif movieSelection == "25"
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - SpeedyBars/Code/25.mp4';
elseif movieSelection == "30"
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - SpeedyBars/Code/30.mp4';
elseif movieSelection == "35"
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - SpeedyBars/Code/35.mp4';
elseif movieSelection == "40"
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - SpeedyBars/Code/40.mp4';
elseif movieSelection == "45"
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - SpeedyBars/Code/45.mp4';
elseif movieSelection == "50"   
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - SpeedyBars/Code/50.mp4';
elseif movieSelection == "100"   
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - SpeedyBars/Code/100.mp4';
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

