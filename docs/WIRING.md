# Greenhouse Wiring

This section will go over the wiring of the current version of the electrical enclosure. It'll be broken down into the following sections:

* Power systems
* Instrument wiring
* Raspberry Pi
* Multiplexer
* Relay

In addition, this section will also cover smaller but essential concepts:

* Connector types
* Extending connectors

## Power Systems

As explained in the [ELECTRICAL](./docs/ELECTRICAL.md) section, there are three main components - the DC Power Adapter, the DC Power Distribution Block, and the Surge Protector. As described in the diagram below, the power adapter and any 120VAC components (e.g. the modified light bulb) are directly plugged into the surge protector.

[DIAGRAM HERE]

The power adapter is then connected to the DC power distribution block via a DC barrel plug to 2-pin terminal adapter. Lock the exposed wires on the other side into the corresponding positive and negative input terminals. The power distribution block then splits into 8 different channels that are gated with a fuse. These channels will power low-voltage, DC compatiable instruments like the 5V 120mm fans, the Raspberry Pi, and the water pump*.

[DIAGRAM HERE]
* - The water pump is technically rated at 6V, but it is tested to work at 5V with minimal initial impact on pump performance.

## Instrument Wiring

To power all the different instruments that invoke some kind of action within the greenhouse, we go through two methods - the DC power distribution block and the 120VAC wall outlet. For the former, the distribution block has two ports (negative and positive) for each channel. Since we're using the relay to control these instruments, connect a wire between the positive (live) wire from one of the channels from the DC PD to a relay module's center terminal. Then, the positive wire from the instrument will go into the the "Normally Open" terminal on the relay. It will be designated with the symbol below and is on the right terminal on the TSL0012. "Normally Open" means that in the off state of the relay, the relay will remain open, which means that the device connected to the relay will be turned off.

[DIAGRAM FOR RELAY TO DC PD WIRING]

For the 120VAC wiring, we split the live wire in the extension cord and do the same kind of wiring as the DC PD. The live wire on the end of the 3-prong terminal is inserted into the center of the relay module. Then the live wire going to the 120VAC device connects into the "Normally Open" terminal. **Please be careful when handling 120VAC wiring. If handled inproperly, it can lead to serious injury or death.** To add an additional level of safety for the 120VAC wiring, we add a 120VAC 2A fuse parrellel along the prong-side of the live wire [DOUBLE CHECK THIS]. In the event of a potential short caused by a ground and live wire touching, the fuse would pop and stop the circuit.

## Raspberry Pi

The Raspberry Pi is powered by the DC PD and can be powered by either of the two 5V pins (pin 2 and 4). Utilize a female-female or female-male JST connector with one end stripped to the raw wire.

If the power connection is stable, the Raspberry Pi's LED indicator should briefly show a red light, and immediately transfer to solid and then blinking green light. If it stays red or returns back to red, then double check the connection and the wire's intergrity. 

[PIC OF RPI POWER WIRING]

To connect to the TSL0012, the Raspberry Pi uses one GPIO pin per relay module. Using a female-female JST connector, connect any of the GPIO pins to the corresponding relay module's IO pins.

[PIC OF RPI WIRES TO RELAY MODULE]

## Relay

To power the TSL0012, connect the VCC pin to one of the channels in the DC PD. Connect the ground pin to the ground pin of the Raspberry Pi [VERIFY]. This is important in order to properly power the TSL0012 with a single power source. The TSL0012 has a jumper that tells the board to power both the relay modules and the GPIO circuits from the same 5V input or use seperate power sources. Set the jumper to the former for this to work with this greenhouse design. 