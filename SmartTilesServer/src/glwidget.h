#ifndef GLWIDGET_H
#define GLWIDGET_H

#include <QGLWidget>
#include <vector>
#include <glm/glm.hpp>

//! [0]
class GlWidget : public QGLWidget
{
    Q_OBJECT

public:
    GlWidget(QWidget *parent = 0);
    ~GlWidget();
    QSize sizeHint() const;

protected:
    void initializeGL();
    void resizeGL(int width, int height);
    void paintGL();

private:
    GLuint shaderProgram;
    std::vector<glm::vec3> vertices;
};
//! [0]

#endif // GLWIDGET_H
