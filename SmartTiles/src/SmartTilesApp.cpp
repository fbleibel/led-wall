/*
 * SmartTilesApp.cpp
 *
 *  Created on: 28 Nov 2013
 *      Author: Francois Bleibel
 */

#include "SmartTilesApp.h"
#include "QtRenderer.h"

namespace smart_tiles {

// Create the default renderer, which is defined in compilation flags.
SmartTilesApp::SmartTilesApp(int argc, char** argv) {
  renderer_ = new QtRenderer(argc, argv);
  renderer_->Setup(6, 5, 800, 600);
}

SmartTilesApp::~SmartTilesApp() {
  delete(renderer_);
}

} /* namespace smart_tiles */

int main(int argc, char** argv) {
  smart_tiles::SmartTilesApp app(argc, argv);
}
