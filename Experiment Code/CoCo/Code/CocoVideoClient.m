client = tcpclient("10.18.27.80",5000,"Timeout",30);

opticfreqs = [3 13 23];

blocks = 12;
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
  
if movieSelection == "3"
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - CoCo/Code/0.3_Hz_sinwave_ext.mp4';
elseif movieSelection == "13"
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - CoCo/Code/1.3_Hz_sinwave_ext.mp4';
elseif movieSelection == "23"
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - CoCo/Code/2.3_Hz_sinwave_ext.mp4';
elseif movieSelection == "100"
    movie = 'C:/Users/suverlab/Desktop/Kevin/Vanderbilt/SuverLab - CoCo/Code/20_ext.mp4';
end

movieSelection = [];
m = Screen('OpenMovie', w, movie);
Screen('PlayMovie', m, 1);
if i == 1
    pause(5);
end
pause(2);

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


cc = [];
while isempty(cc)
    cc = readline(client);
end
end

sca;
close all;
disp('Done!')


