#include <iostream>
#include <fstream>
#include <sstream>
#include <glm/gtc/type_ptr.hpp>

#include "glwidget.h"

using namespace glm;

//! [0]
GlWidget::GlWidget(QWidget *parent)
    : QGLWidget(QGLFormat(/* Additional format options */), parent)
{
}

GlWidget::~GlWidget()
{
}

QSize GlWidget::sizeHint() const
{
    return QSize(640, 480);
}

//! [0]
GLuint createShader(GLenum type, const std::string& path)
{
    std::ifstream file(path.c_str());
    if ( !file ) {
    	std::cout << "Could not open file " << path << " for reading" << std::endl;
    	return 0;
    }
    std::stringbuf contents;
    file >> &contents;
    file.close();
    const char* shaderSrc = contents.str().c_str();

    GLuint shader;
    GLint compiled;

    // Create the shader object
    shader = glCreateShader ( type );

    if ( shader == 0 )
    	return 0;

    // Load the shader source
    glShaderSource ( shader, 1, &shaderSrc, NULL );

    // Compile the shader
    glCompileShader ( shader );

	GLint infoLen = 0;
	glGetShaderiv ( shader, GL_INFO_LOG_LENGTH, &infoLen );
	if ( infoLen > 1 ) {
		char* infoLog = new char[infoLen];

		glGetShaderInfoLog ( shader, infoLen, NULL, infoLog );
		std::cout << "Error compiling shader:" << std::endl <<
				infoLog << std::endl;

		delete infoLog;

      glDeleteShader ( shader );
      return 0;
    }
	std::cout << "Read shader " << path << std::endl;
    return shader;
}

//! [1]
void GlWidget::initializeGL()
{
    //glEnable(GL_DEPTH_TEST);
    glEnable(GL_CULL_FACE);

    glClearColor(0, 0, 0, 1);
    GLuint vertexShader = createShader(GL_VERTEX_SHADER, "vertexShader.vsh");
    GLuint pixelShader = createShader(GL_FRAGMENT_SHADER, "fragmentShader.fsh");
    if (!vertexShader) {
    	std::cout << "Error loading vertex shader!" << std::endl;
    	return;
    }
    if (!pixelShader) {
		std::cout << "Error loading fragment shader!" << std::endl;
		return;
    }

    shaderProgram = glCreateProgram();
    glAttachShader(shaderProgram, vertexShader);
    glAttachShader(shaderProgram, pixelShader);
    glLinkProgram(shaderProgram);

    vertices.push_back(vec3(-1,-1,0));
    vertices.push_back(vec3(1,1,0));
    vertices.push_back(vec3(-1,1,0));
}

void GlWidget::resizeGL(int width, int height)
{
    if (height == 0) {
        height = 1;
    }

    glViewport(0, 0, width, height);
}

void GlWidget::paintGL()
{
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    if (vertices.empty()) {
    	std::cout << "paintGL called before initializeGL???" << std::endl;
    	return;
    }
    mat4 identity(1.0);

    vec4 color(1.0, 1.0, 0.0, 1.0);

    glUseProgram(shaderProgram);
    GLint mvpMatrixUniform = glGetUniformLocation(shaderProgram, "mvpMatrix");
    glUniformMatrix4fv(mvpMatrixUniform, 1, false, value_ptr(identity));

    GLint colorUniform = glGetUniformLocation(shaderProgram, "color");
    glUniform4fv(colorUniform, 1, value_ptr(color));

    GLint vertexAttrib = glGetAttribLocation(shaderProgram, "vertex");
    glVertexAttribPointer(vertexAttrib, 3, GL_FLOAT, false, 0, &vertices.at(0));
    glEnableVertexAttribArray(vertexAttrib);
    glDrawArrays(GL_TRIANGLES, 0, vertices.size());
    glDisableVertexAttribArray(vertexAttrib);
    glUseProgram(0);
}
