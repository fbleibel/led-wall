CMAKE_MINIMUM_REQUIRED(VERSION 2.6)

ADD_DEFINITIONS( -std=c++11 )

PROJECT(SmartTilesQt)
FIND_PACKAGE(Qt4 REQUIRED)
SET(QT_USE_QTOPENGL TRUE)

SET(SmartTilesQt_SOURCES QtRenderer.cpp RendererBase.cpp SmartTilesApp.cpp glwidget.cpp)
SET(SmartTilesQt_HEADERS glwidget.h)

INCLUDE(${QT_USE_FILE})
ADD_DEFINITIONS(${QT_DEFINITIONS})

QT4_WRAP_CPP(SmartTilesQt_HEADERS_MOC ${SmartTilesQt_HEADERS})

ADD_EXECUTABLE(smart-tiles-qt ${SmartTilesQt_SOURCES} ${SmartTilesQt_HEADERS_MOC})

# Must restrict to using OpenGLES
SET_TARGET_PROPERTIES(smart-tiles-qt PROPERTIES COMPILE_DEFINITIONS "QT_OPENGL_ES_2")

TARGET_LINK_LIBRARIES(smart-tiles-qt ${QT_LIBRARIES} GLESv2)

ADD_EXECUTABLE(smart-tiles-server server/Server.cpp server/main.cpp)