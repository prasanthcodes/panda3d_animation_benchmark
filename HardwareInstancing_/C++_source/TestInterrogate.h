// TestInterrogate.h
#ifndef TESTINTERROGATE_H
#define TESTINTERROGATE_H


#include "stdafx.h"
#include "LVecBase3.h"
#include "nodePath.h"
#include "LVecBase4.h"
#include "spotlight.h"
#include "shader.h"
#include "camera.h"
#include "nodePathCollection.h"
#include "boundingSphere.h"
#include "pta_LMatrix4.h"

class EXPCL_PANDASKEL TestInterrogate
{
PUBLISHED:

	// every exposed class, which is not static, needs a constructor and destructor
	TestInterrogate(void);
	~TestInterrogate(void);

	static PTA_LMatrix4f  updateShaderTask(NodePath* MainNP, NodePath* model, NodePath* camNP, LVecBase3f model_center, float model_ray);

};
#endif