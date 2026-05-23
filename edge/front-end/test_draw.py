from draw_pose import draw_pose,draw_all_poses
import matplotlib.pyplot as plt

#draws a single pose
fig, ax = draw_pose("both_arms_down")
# plt.show()


# fig, ax = draw_pose("star")
# plt.show()


#should make a repo and then save the individual image pose for all poses to a dir called poses
fig = draw_all_poses("songs/metadata.json", save_individual=True, output_dir="poses")