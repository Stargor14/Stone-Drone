# Stone-Drone
The name is inspired by Dr. Stone a pretty cool anime I'm watching atm, This is a fully autonomous drone that uses a raspi, arduino mega and a multitude of sensors to be able to maneuver in and outdoors 

So far this project has been extremly fun to just plan out and as of late april 2021, I'm still waiting on parts to come in from China. 

https://docs.google.com/spreadsheets/d/1sfcIO34VnrTxYRGocUGCcTRqPbvwn5STOFTQCprg6zo/edit?usp=sharing
^^ spreadsheet with links to parts and costs. Some parts that I already ordered not included

I've wanted to do something like this for a while now, and now that I'm gttign a summer job I can finally afford it. 

Personally, I think building a drone is cool and all, but if it has ot be manually controlled, its kind of a lame project.
So, I decided that Im going to make this drone fullyautonmous using a raspi as a flight COMPUTER and an arduino running multiwii software as a flight CONTROLLER.
The idea right now is that for indoor flight, it's equiped with about 8 ultrasonic range detectors, which are suprisingly cheap(under 1$ a sensor)
Additionally, it has a raspi ir camera attached, but for now I'm not going to worry myself with image processing on a raspberry pi, I feel as though that would be a pain due to 
hardware contraints. However, if I manage to process the images on a laptop or even my PC, image processing could still be feasble, however then I run into teh issue of latency 
between the drone and my computer. For now it's an idea I will explore further.

Code wise, thankfully there are projects that have already controlled drones through raspberry pis and multiwii firmware, the one im taking inspirtation form for my code is https://github.com/darkterbear/drone. The creater of that project already wrote code to communicate to the flight controller through python code, so that takes a huge burden off my shoulders. 

On the engineering side of things, the drone uses 4 2300kv motors that are going to run on a 4S3P or 4S2P battery configuration with some nice ass 18650 cells (10A 3000mAh!!!) from LiitoKala.
In order to keep track of battery voltage (and subsequently a rough approximation of remaining capacity) the drone is going to use a basic voltmeter from the arduino, using 90kohm and 10k ohm resistors.

In the repository I included a program that calculates the approximate flight time of various battery sizes (also takes weight of cells into account) 

I'll keep this file updated as things progress
