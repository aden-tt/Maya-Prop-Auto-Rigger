import maya.cmds as cmds

# Global references to input controls
main_grp_field = None
root_jnt_field = None
geo_suffix_field = None
jnt_suffix_field = None
make_root_jnt_checkbox = None


def create_window():
    if cmds.window("AutomaticPropRigger", exists=True):
        cmds.deleteUI("AutomaticPropRigger")

    window = cmds.window("AutomaticPropRigger", title="Automatic Prop Rigger", menuBar=True, widthHeight=(350, 420))

    # --- Help & Documentation ----
    cmds.menu(label='Help', tearOff=False)
    cmds.menuItem(label='Documentation')
    cmds.menu(label='Preferences', tearOff=False)
    cmds.menuItem(label='Save')
    cmds.menuItem(label='Load')

    # --- Main Outer Layout
    main_layout = cmds.columnLayout(adjustableColumn=True)

    # --- Control Options ----
    cmds.text(label='Control Options', font='boldLabelFont', align='center')
    cmds.separator(height=5, style='none')

    ctrl_size_slider = cmds.floatSliderGrp(
        label='Control Size',
        field=True,
        minValue=0.1,
        maxValue=100,
        value=1.0,
        step=1,
        columnWidth=[(1, 90), (2, 50), (3, 150)]
    )

    ctrl_color_slider = cmds.colorSliderGrp(
        label='Control Color',
        hsv=(120, 1, 1),
        columnWidth=[(1, 90), (2, 50), (3, 150)]
    )

    cmds.separator(height=15, style='single')

    cmds.text(label='Control Shapes', font='boldLabelFont', align='center')
    cmds.separator(height=5, style='none')

    cmds.rowColumnLayout(
        numberOfColumns=3,
        columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2)],
        columnWidth=[(1, 110), (2, 110), (3, 110)],  # Base widths that scale evenly
        rowSpacing=[(1, 4), (2, 4), (3, 4)]
    )
    cmds.button(label='Box')
    cmds.button(label='Circle')
    cmds.button(label='Sphere')
    cmds.button(label='Cross')
    cmds.button(label='Square')
    cmds.button(label='Pointer')
    cmds.button(label='Custom')

    cmds.setParent(main_layout)  # Return to main layout
    cmds.separator(height=25, style='single')

    # --- Rig Options ----
    cmds.text(label='Rig Options', font='boldLabelFont', align='center')
    cmds.separator(height=5, style='none')

    cmds.rowColumnLayout(
        numberOfColumns=3,
        columnAttach=[(1, 'both', 2), (2, 'both', 2), (3, 'both', 2)],
        columnWidth=[(1, 110), (2, 110), (3, 110)],
        rowSpacing=[(1, 4)]
    )
    make_root_jnt_checkbox = cmds.checkBox(label='Make Root Joint')
    cmds.text(label='')
    cmds.text(label='')

    cmds.button(label='Full Rig', command=createJoints)
    cmds.button(label='Joints Only')
    cmds.button(label='Controls Only')
    cmds.setParent(main_layout)  # Exit back to main layout

    cmds.separator(height=15, style='none')

    # --- Naming Settings ---
    cmds.frameLayout(label='Naming Conventions', collapsable=True, marginWidth=5, marginHeight=5)
    cmds.rowColumnLayout(
        numberOfColumns=2,
        columnAttach=[(1, 'right', 5), (2, 'both', 0)],
        columnWidth=[(1, 120), (2, 1)],
        adj=2
    )
    cmds.text(label='Main Group Name')
    main_grp_field = cmds.textField()
    cmds.text(label='Root Joint Name')
    root_joint_field = cmds.textField()
    cmds.text(label='Geometry Suffix')
    geo_suffix_field = cmds.textField()
    cmds.text(label='Joint Suffix')
    jnt_suffix_field = cmds.textField()
    cmds.text(label='Offset Suffix')
    offset_suffix_field = cmds.textField()
    cmds.text(label='Control Suffix')
    ctrl_suffix_field = cmds.textField()

    cmds.setParent(main_layout)  # Return to main layout

    cmds.showWindow(window)


create_window()


def createJoints(objectList=cmds.ls(selection=True), makeRoot=True):
    jntList = []

    if makeRoot:
        cmds.select(clear=True)
        rootJoint = cmds.joint(name="root_jnt", sc=False)

    # Ensure the list contains only mesh objects
    meshXformList = [obj for obj in objectList if cmds.listRelatives(obj, type="mesh", path=True) is not None]
    if len(meshXformList) == 0:
        cmds.error(" Please select at least one mesh")

    for obj in meshXformList:
        # Add a joint to pivot center of each selection, if root option is checked, parent all joins to it
        cmds.select(clear=True)

        # Create a joint at the mesh pivot location
        pivotPos = cmds.xform(obj, query=True, pivots=True, worldSpace=True)
        jnt = cmds.joint(name=obj + "_jnt", sc=False, position=[pivotPos[0], pivotPos[1], pivotPos[2]])

        # Create an empty offset group
        offsetGroup = cmds.group(n=obj + "_offset", empty=True)

        # Position offset group at joint
        jnt_pos = cmds.xform(jnt, query=True, translation=True, worldSpace=True)
        cmds.xform(offsetGroup, translation=jnt_pos, worldSpace=True)

        # Create control at joint location
        control = cmds.circle(n=obj + "_ctrl")
        cmds.parent(control, offsetGroup)
        cmds.xform(control, translation=[0, 0, 0], rotation=[0, 0, 0])

        # Constrain joint to control
        cmds.parentConstraint(control, jnt, mo=True)

        # Skin the mesh geometry to the joint
        if makeRoot:
            jnt = cmds.parent(jnt, rootJoint)

        cmds.skinCluster(obj, jnt, toSelectedBones=True)
        jntList.append(jnt)

    if makeRoot:
        return jntList, rootJoint
    else:
        return jntList

