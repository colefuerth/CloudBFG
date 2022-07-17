# CloudBFG implelmentation

This is a cloud-based AI implementation of an SoC characterization algorithm.

Initial meeting notes can be found [here](notes.md).

## OCV Curves

The first version of the CloudBFG estimation algorithm will use a cache of pre-computed OCV curves.

For each of the batteries recorded in the [data](res/K_para.csv), the following OCV curve is generated, for use in estimating the K parameters of real batteries:

![OCV Curves](img/OCV_curves.png)

## Curve Fitting

Acceptable accuracy is 90% or more

### First Generation Estimation (completed)

- [x] start by generating the curves for each of the sample k parameters using zsoc.py
- [x] Generate a full discharge curve (no noise) for a battery with matching k parameters to the sample curves
- [x] look up the OCV curve for the battery with matching k parameters to the sample curves

- The guess can be using Vo from the simulator, for a perfect-match test case, as a proof of concept

#### Results

Since this is ideal-case, as soon as estimation was working, it was 100% accurate.

### Second Generation Estimation (ongoing)

- Second generation fitting will be done with noisy Vout curves
- This means that curve fitting will happen on the samples first, and then the clean curves will be compared to the sample set

#### The Process

I calculate the first and second derivatives, to try to fit based on rate of change of the cell potential. Below are the curves for all samples, with the first derivative and second derivative curves.

```py
# plot curves and derivatives for the sample battery
fig, ax = plt.subplots(3, 1, sharex=True)
for battery in batteries:
    ax[0].plot(battery['Vo'])
    ax[1].plot(battery['dV'])
    ax[2].plot(battery['dV2'])

ax[0].title.set_text('Vo')
ax[1].title.set_text('dVo')
ax[2].title.set_text('d2Vo')
fig.suptitle('Derivatives of Curves')
ax[0].grid(True)
ax[1].grid(True)
ax[2].grid(True)
plt.show()
```

![Derivatives](img/fig2_1.png)

#### First Attempt

- Taking the first and second derivatives of each OCV curve and comparing to the first and second derivatives of the sample is going to be the first attempt
- Going to account for voltage sag, but not noise

##### Results:

- The results are not perfect, but it is correct about half the time and is close to the correct answer when it isn't correct
- Looking at the results, it is clear that derivatives will be the best way to see if curves can be overlayed

![results_gen2_first_attempt](img/fig2_2.png)

```txt
expected Kbatt:  [-1.3313, 28.2101, -4.8784, 0.5292, -0.0247, -18.9233, 37.9843, -0.27]
actual Kbatt:    [-0.9741, 30.3903, -5.2017, 0.5596, -0.0259, -21.3917, 41.5533, -0.3517]
```

<sub>*This result is using a Model=1 BattSim with voltage sag, but no noise</sub>

#### Second Attempt

- I am going to try a metric where I subtract the sample and target curves, and calculate how consistent the distance between the curves are. 
  - This does essentially the same thing as the first attempt's dV derivative metric, but should help account for noise, where dV does not account for noise
  - It is being tested because, though it may not be scaleable, it may be computationally faster than noise removal/curve fitting and is worth trying

##### Results:

- Results are perfect every time, even with voltage noise introduced
- Changed the search metric used to subtract the sample from each target curve and integrate them, to get the area where the curves do not overlap. A shorter sum is better; pick the closest one

![results_gen2_second_attempt](img/fig2_3.png)

```txt
expected Kbatt:  [-4.4256, 83.6175, -14.0185, 1.4878, -0.0678, -64.5844, 118.3224, -0.8474]
actual Kbatt:    [-4.4256, 83.6175, -14.0185, 1.4878, -0.0678, -64.5844, 118.3224, -0.8474]
```

#### Third Attempt

- do testing to determine an actual accuracy %
- start introducing more noise into the curves until the accuracy starts to drop
- Introduce some current noise? still do a full 1C discharge, but with slight noise, so the curves can no longer be perfect matches

### Third Generation Estimation (untouched)

- Third generation will be where we start changing current throughout the discharge, since it will be rare that we will have a full, constant discharge curve.
- This means that outputs will have both sag noise, and voltage noise.
- The possiblity of calculating R0 is now introduced, since model 1 testing should see a linear scale in voltage drop based on current draw

### Fourth Generation Estimation (untouched)

- Incomplete curves will hopefully be able to be used, since it will be rare that a full discharge curve will be available.
- This is a lesser priority, since it is reasonable to request a full curve, although it will be difficult to collect from general use statistics.
