/*
 * SmartTilesApp.h
 *
 *  Created on: 28 Nov 2013
 *      Author: Francois Bleibel
 */
#include "RendererBase.h"

#ifndef SMARTTILESAPP_H_
#define SMARTTILESAPP_H_

namespace smart_tiles {

class SmartTilesApp {
public:
	SmartTilesApp(int argc, char** argv);
	void Run();
	virtual ~SmartTilesApp();
protected:
	RendererBase* renderer_;
};

} /* namespace smart_tiles */
#endif /* SMARTTILESAPP_H_ */
