/*
 * RendererBase.cpp
 *
 *  Created on: 29 Nov 2013
 *      Author: bleyblue
 */

#include "RendererBase.h"

namespace smart_tiles {

RendererBase::RendererBase(int argc, char** argv) :
        num_leds_x_(0),
        num_leds_y_(0),
        display_width_(0),
        display_height_(0),
        simulator_(0) {}

void RendererBase::Setup(int num_leds_x, int num_leds_y, int display_width,
    int display_height) {
  num_leds_x_ = num_leds_x;
  num_leds_y_ = num_leds_y;
  display_width_ = display_width;
  display_height_ = display_height;
}


RendererBase::~RendererBase() {
  // TODO Auto-generated destructor stub
}

} /* namespace smart_tiles */
