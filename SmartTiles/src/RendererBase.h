/*
 * RendererBase.h
 *
 *  Created on: 29 Nov 2013
 *      Author: bleyblue
 */

#ifndef RENDERERBASE_H_
#define RENDERERBASE_H_

namespace smart_tiles {

class Simulator;

class RendererBase {
public:
  RendererBase(int argc, char** argv);
  virtual ~RendererBase();

  // Set up the various components of this renderer. By default, will render
  // a rectangular surface of num_leds_x * num_leds_y - the raw pixel data that
  // will be sent to the LEDs.
  virtual void Setup(int num_leds_x, int num_leds_y, int display_width,
    int display_height);

  // Initialises and add a Simulator to the renderer. The simulator displays
  // what the LED boards will look like and draws display_width * display_height
  // frames.
  virtual void AddSimulator();

  // Remove the simulator. Drawing now occurs on a display surface of num_leds_x
  // * num_leds_y pixels.
  virtual void RemoveSimulator();

  bool using_simulator() { return bool(simulator_); }

  // Render an image into the OpenGL buffer.
  virtual void Render();

protected:
  // The dimensions of the LED board
  int num_leds_x_;
  int num_leds_y_;
  // The dimensions of the screen drawing surface (that will be used if using
  // a simulator)
  int display_width_;
  int display_height_;

  Simulator* simulator_;
};

} /* namespace smart_tiles */
#endif /* RENDERERBASE_H_ */
