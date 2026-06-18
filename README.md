# atmos-seeing_analyser

----



### AIM

Our aim is to build a fast and reliable program for computing atmospheric seeing values. We will prepare two implementations: one for individual images and one for image sequences. 

### METHOD

  The seeing analyzer in this project derives atmospheric seeing from the jitter of the solar limb.
  The procedure is as follows: MIN2 first generates a perfect reference circle representing a non‑fluctuating solar disk. Then, along radial directions aligned with the pixel grid near the limb, the brightness profile is differentiated twice. The actual limb position is defined as the point where the second derivative reaches its maximum, located farther from the center than the first‑derivative peak. The radial deviation between this detected limb and the MIN2 reference circle is interpreted as geometric distortion, which is then quantified as the seeing value.
