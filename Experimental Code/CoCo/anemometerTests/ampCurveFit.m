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

windspeed = x_curve;
tAmpVal = y_fit;
eAmpVal = y_curve;

save('ampFittedCurve',"windspeed","p","tAmpVal","eAmpVal")