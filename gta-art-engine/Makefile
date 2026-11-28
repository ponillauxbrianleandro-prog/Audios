# make posing | make aiming | make all | make draft
posing:
	tools/run_pose.sh posing 3200 2000 48 0.0030 work/f_posing
aiming:
	tools/run_pose.sh aiming 3200 2000 48 0.0030 work/f_aiming
all: posing aiming
draft:      # borrador rápido (~1 min)
	tools/run_pose.sh posing 1600 1000 16 0.005 work/d_posing
	tools/run_pose.sh aiming 1600 1000 16 0.005 work/d_aiming
setup:
	./bootstrap.sh
