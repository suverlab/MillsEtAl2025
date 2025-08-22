% Generation of windspeed x anemometer value (amplitude) curve
data = load("anemometerCurveAcrossAllWindspeeds.mat");
data = data.data;
windspeeds = [data.windspeed];
anemVals = [data.anemVal];
x_curve = windspeeds(11:end);
y_curve = anemVals(11:end);

p = polyfit(x_curve,y_curve, 6);
y_fit = polyval(p,x_curve);
figure;
plot(x_curve,y_fit,'b')
hold on;
plot(x_curve, y_curve)
xlabel('windspeed (cm/s)')
ylabel('anemometer value (a.u.)')
title('windspeed x anemometer')
windspeed = x_curve;
tAnemVal = y_fit;
eAnemVal = y_curve;

save('anemometerFittedCurve',"windspeed","p","tAnemVal","eAnemVal")
p1 = p;

% Generation of frequency x amplitude curve
data = load("ampFreqCurveData.mat");
data = data.data;
F = [data.F];
amp = [data.amp];
x_curve = F(1:80);
y_curve = amp(1:80);

p = polyfit(x_curve,y_curve, 6);
y_fit = polyval(p,x_curve);
figure;
plot(x_curve,y_fit,'b')
hold on;
plot(x_curve, y_curve)
xlabel('frequency (hz)')
ylabel('average anemometer value maximum (a.u.)')
title('frequency x absolute amplitude')

windspeed = x_curve;
tAmpVal = y_fit;
eAmpVal = y_curve;

save('ampFittedCurve',"windspeed","p","tAmpVal","eAmpVal")

p2 = p;

% Curve comparison, generation of frequency x windspeed maximum curve

x = (5:5:400)/100;

anemVals = polyval(p2,x);
y = zeros(1, length(anemVals));
for i=1:length(anemVals)
    p_iter = p1;
    p_iter(7) = p1(7) - anemVals(i);
    r = roots(p_iter);
    r = r(imag(r)==0);
    r = r(10 <= r & r <= 300);
    y(i) = r;
end
p = polyfit(x,y,6);
y_fit = polyval(p,x);
figure;
plot(x,y_fit,'b')
hold on;
plot(x, y)
ylabel('windspeed (cm/s)')
xlabel('frequency (Hz)')
title('frequency x windspeed maximum')

