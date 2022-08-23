# Stone-Drone
<img src="https://github.com/Stargor14/Stone-Drone/blob/main/IMG_5996.jpg" alt="DEMO PHOTO" title="Test flight photo">
<img src="https://github.com/Stargor14/Stone-Drone/blob/main/IMG_5999.jpg" alt="DEMO PHOTO" title="Construction photo">
This is a fully autonomous drone that uses a raspi, arduino mega and a multitude of sensors to be able to maneuver in and outdoors 

This project was extremly fun to just plan out and construct. As of late june 2021, i finished physical construction of the drone and even got to fly, but the stabilization code was unfortunatly not good enough, so the drone would crash land after a few seconds of flight. 

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

On the engineering side of things, the drone uses 4 2300kv motors that are going to run on a 4S3P or 4S2P battery configuration with some nice ass 18650 cells (30A 3000mAh!!!) from LiitoKala, who know; maybe theyre fake.

In order to keep track of battery voltage (and subsequently a rough approximation of remaining capacity) the drone is going to use a basic voltmeter from the arduino, using  a  90kohm and 10k ohm resistor.

In the repository I included a program that calculates the approximate flight time of various battery sizes (also takes weight of cells into account). This uses linear regression to fill in gaps of the manufacturers datasheet (A @ thrust%, or thrust% @ thrust in grams)

I'll keep this file updated as things progress

Update1 Late April: Some battery parts came in, so I soldered together a sketchy ass battery from old laptop 18650s. Turns out soldering nickel strips onto a flat surface isnt very fun. My left index finger now has 50% less touch after i burnered it 6 consecutive times. I have to get a spot welder next time I do this. Also, the fire extinguisher is now in my room.

Update2 Early May: No new parts have come in yet, but many are close. I've written and msotly debugged the code for communcating between teh server(drone) and client(laptop or pc). It 
took a surpringly long time(2 days). The main flight loop is now be able to recognize people as well as other objects within a frame and move the camera sercos to attempot and 
centre the image. Once the servos reach their maximum movemnt, nothing happens at the moemnt, but I will probably add yaw control as well soon. That way teh drone will be able 
to more effectivly track a person or object. The image data from the raspi is heavily compressed(8-10% quality) so that it can reach a decently high fps(10? i think). There is 
very high quality loss, however the object recognition algorithim can still recognize people effectivly and to a decent degree of accuracy. Ill probably start writing the actual 
flight decision loop. Fail safes and decision overrides?
  Im not too sure about what Im going to add first but by the next update Ill probably be done human tracking functionailty. Now that I think of it, that will definelty be the first mode I introduce. 
  
Update3: early june
Im not sure why my last updatye didnt go through, but the gist of everything is that all parts came, and the drone is done physical construction. Somewhere along teh way I chose to scrap the idea of using multiwii firmware and instead opted to write my own stabiliztion and serial communcation protocol. So far thats been going well, but ive been lazy and havent started writing the pid loop until now. I've hung the drone off my ceiling using soime kind of rubber or nylon cable. Im not sure what it is, but teh point is that i can test the drone without risking snapping its arms (again). Once I finish some morestabiuliztion code, ill get working on actual decision making. 
