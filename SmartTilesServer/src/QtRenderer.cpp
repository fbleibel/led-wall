/*
 * QtRenderer.cpp
 *
 *  Created on: 28 Nov 2013
 *      Author: Francois Bleibel
 */
#include "QtRenderer.h"

namespace smart_tiles {

QtOpenGLRenderer::QtOpenGLRenderer(int argc, char** argv) : RendererBase(argc, argv) {
  app_ = new QApplication( argc, argv );
}

void QtOpenGLRenderer::Setup(int num_leds_x, int num_leds_y, int display_width,
                       int display_height) {
  RendererBase::Setup(num_leds_x, num_leds_y, display_width, display_height);
  view_ = new GlWidget();
  view_->show();
}

QtOpenGLRenderer::~QtOpenGLRenderer() {
  delete(view_);
  delete(app_);
}

// See base class.
void QtOpenGLRenderer::AddSimulator() {

}

// See base class.
void QtOpenGLRenderer::RemoveSimulator() {

}

void QtOpenGLRenderer::Render() {

}

} /* namespace smart_tiles */
