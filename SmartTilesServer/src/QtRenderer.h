/*
 * QtRenderer.h
 *
 *  Created on: 28 Nov 2013
 *      Author: Francois Bleibel
 */

#ifndef QTRENDERER_H_
#define QTRENDERER_H_

#include <QApplication>
#include "RendererBase.h"
#include "glwidget.h"

namespace smart_tiles {

class QtOpenGLRenderer : public RendererBase {
public:
  // On initialisation, creates a GUI QApplication.
	QtOpenGLRenderer(int argc, char** argv);
	virtual ~QtOpenGLRenderer();

	// Set up the various components of this renderer. This will create a
	// QGLWidget and show() it.
	virtual void Setup(int num_leds_x, int num_leds_y, int display_width,
	                   int display_height);

	// See base class.
	virtual void AddSimulator();

	// See base class.
	virtual void RemoveSimulator();

	virtual void Render();

protected:
	QApplication* app_;
	GlWidget* view_;
};

} /* namespace smart_tiles */
#endif /* QTRENDERER_H_ */
