/*
 * QtRenderer.cpp
 *
 *  Created on: 28 Nov 2013
 *      Author: Francois Bleibel
 */
#include "QtRenderer.h"

namespace smart_tiles {

QtRenderer::QtRenderer(int argc, char** argv) : RendererBase(argc, argv) {
  app_ = new QApplication( argc, argv );
}

void QtRenderer::Setup(int num_leds_x, int num_leds_y, int display_width,
                       int display_height) {
  RendererBase::Setup(num_leds_x, num_leds_y, display_width, display_height);
  int argc = 0;
  char** argv = 0;
}

QtRenderer::~QtRenderer() {
  delete(app_);
}

} /* namespace smart_tiles */
