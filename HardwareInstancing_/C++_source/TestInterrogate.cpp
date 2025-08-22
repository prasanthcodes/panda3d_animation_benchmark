#include "TestInterrogate.h"

TestInterrogate::TestInterrogate(void) {}
TestInterrogate::~TestInterrogate(void) {}


PTA_LMatrix4f TestInterrogate::updateShaderTask(NodePath* MainNP, NodePath* model, NodePath* camNP, LVecBase3f model_center, float model_ray) 
{ 
	PT(Camera) cam = DCAST(Camera, camNP->node());
	PT(Lens) lens = cam->get_lens();
	lens->set_near(0.1);
	CPT(BoundingVolume) lens_boundingvolume_old = lens->make_bounds();

	PTA_LMatrix4f shader_data;

	NodePathCollection &children = MainNP->get_children();
	int number_visible_instance = 0;

	for (int i = 0; i < children.size(); ++i) {
		
		LVecBase3f new_center = children[i].get_mat().xform_point_general(model_center); 
		PT(BoundingSphere) np_bsphere_new = new BoundingSphere(new_center, model_ray*children[i].get_scale().get_x());
		const LMatrix4f &transform_mat = children[i].get_parent().get_mat(*camNP); 
		np_bsphere_new->xform(transform_mat); 

		if (lens_boundingvolume_old->contains(np_bsphere_new) != 0)
		{
			LMatrix4f mat = children[i].get_mat();
			mat.transpose_in_place();
			UnalignedLMatrix4f mat_final = UnalignedLMatrix4f(mat);
			shader_data.push_back(UnalignedLMatrix4());
			shader_data[number_visible_instance] = mat_final;
			number_visible_instance++;
		}
		

	}


	return shader_data;
}