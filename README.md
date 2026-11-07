# RBMK Reactor Simulation

This is a 2D simulation of an RBMK nuclear reactor (the type of reactor used at Chernobyl) that I made in Python with pygame. You can watch neutrons fly around, split uranium, boil the cooling water and poison the core with xenon. If you do the wrong things in the wrong order you can recreate what happened at Chernobyl in 1986.

A large part of this project was inspired by [Chernobyl Visually Explained](https://www.youtube.com/watch?v=P3oKNE72EzU&t=80s) by Higgsino physics. It explains how the reactor works and what went wrong way better than I could, so if you want to understand what's going on in the sim, watch that first.

## Running it

You need Python 3 and pygame.

```bash
pip install pygame
python main.py
```

I made it with Python 3.13 and pygame 2.6.1. The window is 1900x1000, so it fits best on a 1080p screen or bigger.

## What you're looking at

| On screen | What it is |
|---|---|
| Blue circles | Uranium fuel that's ready to split |
| Gray circles | Spent fuel that already split |
| Dark gray circles | Xenon-135, which soaks up neutrons and slows the reactor down |
| Red dots | Fast neutrons |
| Pink dots | Slow (thermal) neutrons, the only ones that can split uranium |
| Light blue squares | Cooling water. It gets redder as it heats up and turns white when it boils into steam |
| White bars | Graphite moderators that slow the neutrons down |
| Gray bars | Control rods that absorb neutrons |
| White tips on the rods | The graphite tips on the control rods (the design flaw) |
| Thin light blue strips under the rods | Water in the control rod channels |

## Controls

- **Raise Rods / Lower Rods**: hold to move all the control rods. Only works when Manual Control is on.
- **Manual Control**: switches between manual and automatic rod control. The green light means manual is on.
- **SCRAM**: emergency shutdown. Drives all the rods all the way in over about 20 seconds, and you can't stop it once it starts.
- **Pump Level**: how hard the water pumps are working. Lower means less cooling and more boiling, and at 0% the water drains out of the core.
- **Neutron Target**: in automatic mode the rods move on their own to keep the neutron count around this number.
- **Volume**: every time uranium splits it makes a Geiger counter click, and this sets how loud that is.

## The panel

- **Neutrons** and **Xenon Cells**: how many of each are in the core right now.
- **Fuel Temp**: hotter fuel is less likely to split, and that's what keeps the reactor stable when it's running normally.
- **Thermal**: the heat the reactor is putting out. A real RBMK ran at around 3200 MW.
- **Electric**: what the turbines make from that heat. It maxes out at 1000 MW like the real thing.
- **Coolant**: how much of the core still has water in it.
- **Steam**: how much of the core is boiling.
- **Rods In**: how far the absorbing part of the control rods is in the core.
- **Thermal Power graph**: the last 60 seconds of power. The scale on the side adjusts itself, and the dashed line is normal full power (3200 MW).

Numbers turn red when things start getting dangerous.

## How it works

- Only slow neutrons can split uranium. The fast neutrons that come out of a split have to hit a graphite moderator first to slow down.
- Every split makes 3 new neutrons, so if nothing absorbs them it can run away really fast.
- Water absorbs neutrons. When it boils into steam it stops absorbing them, so more boiling means more power, which means even more boiling. This is the positive void coefficient, and it's one of the big reasons the RBMK was so dangerous.
- Hot fuel is less likely to split, which pulls the power back down when it gets too high.
- Split fuel slowly turns into xenon, which eats neutrons. At high power the neutrons burn the xenon off as fast as it shows up, but at low power it builds up and can choke the reactor. This is the xenon pit.
- The control rods have graphite tips. When you hit SCRAM the tips go into the core first and push the water out, so the power actually jumps up before the rods can shut it down.

## Recreating Chernobyl

1. Turn on Manual Control and hold Raise Rods until the rods stop moving. Let it run at full power for a couple of minutes.
2. Hold Lower Rods until Rods In says about 80%, so the power drops way down. Leave it like that for about a minute and a half while the xenon builds up.
3. Raise the rods all the way out again. The power won't come back because the core is full of xenon. It's stuck in the xenon pit, which is pretty much where Chernobyl was before the test (theirs was stuck at around 200 MW).
4. Drop Pump Level to 0%. The water boils off from the top down, nothing is absorbing the neutrons anymore, and within about half a minute the power runs away.
5. Hit SCRAM right as the power starts climbing. The graphite tips go in first and push the power up even more before the rods can do anything.

## Note

This is a simplified model and not a real physics simulation. The power numbers are scaled to roughly match a real RBMK, but don't take any of them as accurate.

## Credits

- [Chernobyl Visually Explained](https://www.youtube.com/watch?v=P3oKNE72EzU&t=80s) by Higgsino physics. A large part of this project is based on this video.
