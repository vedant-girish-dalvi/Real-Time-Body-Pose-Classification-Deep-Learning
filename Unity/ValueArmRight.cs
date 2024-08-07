using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class ValueArmRight : MonoBehaviour
{
    // Start is called before the first frame update
    private Vector3 VectAElbow; // Vector between ForeArm and Shoulder (Arm for unity)
    private Vector3 VectBElbow; // Vector between ForeArm and Wrist (Hand for Unity)
    private Vector3 VectShtoEL; // Vector Shoulder to Elbow 
    private Vector3 UnitVectorA; // Vector Shoulder to Unit  (1,x,z), Plane for abduction/adduction 
    private Vector3 UnitVectorB; // Vector Shoulder to Unit (x,y,1) , Plane for Flexion/Extension
    private Vector3 HandFlexationHelper;
    private Vector3 VectShtoUnitB;
    private Vector3 LowArmToWrist;

    private Vector3 BackAxis;
    private Vector3 xAxisArm;

    private Vector3 planeX;
    private Vector3 planeY;
    private Vector3 planeZ;

    private Vector3 RotationShoulder;
    private Vector3 RotationWrist;
    private Vector3 RotationLowArm;

    public GameObject LowerArm; // POsition Joint ForeArm (ELbow)
    public GameObject UpperArm; // Position Joint Shoulder 
    public GameObject Hand; // Position Joint Wrist
    public GameObject Shoulder; // Position Joint Clavicula
    public GameObject Finger;

    public GameObject Hip;
    public GameObject Spine2;

    public float ELbowAngle; // Elbow Flexion/ Extension
    public float ShAdAbAngle; // Shoulder Adduction/ Abduction
    public float ShFlExAngle; // Shoulder Flexion / Extension 
    public float lowArmPronateR;
    public float upArmRotateR;
    public float handFlexR;
    public float handRadDuctR;


    // Update is called once per frame
    void Update()
    {
        //Calculate the Elbow Angle  Flexion/Extension 
        VectAElbow = UpperArm.transform.position - LowerArm.transform.position;    // Vector Shoulder to Elbow
        VectBElbow = Hand.transform.position - LowerArm.transform.position;  // Vector Elbow to Wrist

        ELbowAngle = Vector3.Angle(VectAElbow, VectBElbow)*(-1)+180; // Angle calculation

        //Calculate the Adduction /abduction Angle of the shoulder
        //adduction and abduction angle ,axis +x (red) ref. Unity vectors
        VectShtoEL = UpperArm.transform.position - LowerArm.transform.position; // Vector from Arm (shoulder point) to Forearm (elbow point)
        UnitVectorA = LowerArm.transform.right; //+x (red) ref. Unity vectors

        BackAxis = Spine2.transform.position - Hip.transform.position;

        planeZ = new Vector3(0, 0, 0) - new Vector3(0, 0, 1);

        RotationShoulder = Shoulder.transform.localRotation.eulerAngles;
        ShAdAbAngle = RotationShoulder.z;
        ShAdAbAngle = ((ShAdAbAngle > 180) ? ShAdAbAngle - 360 : ShAdAbAngle) - 80;

        //ShAdAbAngle = SignedAngleBetween(BackAxis, VectShtoEL, planeZ) - 180;

        //Flexion and Extension angle ,axis +z (blue) regun Unity vectors
        //UnitVectorB = new Vector3(Arm.transform.position.x,Arm.transform.position.y, 1);
        //VectShtoUnitB = Arm.transform.position - UnitVectorB;
        UnitVectorB = LowerArm.transform.forward;       //axis +z (blue) ref. Unity vectors

        planeX = new Vector3(0, 0, 0) - new Vector3(1, 0, 0);

        /*
        RotationShoulder = Shoulder.transform.localRotation.eulerAngles;
        ShFlExAngle = RotationShoulder.x;
        ShFlExAngle = ((ShFlExAngle > 180) ? ShFlExAngle - 360 : ShFlExAngle) + 90;
        */
        
        ShFlExAngle = SignedAngleBetween(BackAxis, VectShtoEL, planeX) * (-1) + 185;

        //
        RotationWrist = Hand.transform.localRotation.eulerAngles;

        //Rotation

        planeY = new Vector3(0, 0, 0) - new Vector3(0, 1, 0);
        LowArmToWrist = LowerArm.transform.position - Hand.transform.position;


        RotationLowArm = LowerArm.transform.localRotation.eulerAngles;
        upArmRotateR = RotationLowArm.y;
        upArmRotateR = ((upArmRotateR > 180) ? upArmRotateR - 360 : upArmRotateR) + 10;

        //upArmRotateR = Vector3.SignedAngle(LowArmToWrist, planeX, planeY)*(-1)+90;


        lowArmPronateR = RotationWrist.z;
        lowArmPronateR = ((lowArmPronateR > 180) ? lowArmPronateR - 360 : lowArmPronateR) * (-1);

        //lowArmPronateR = Hand.transform.localRotation.x;


        HandFlexationHelper = Finger.transform.position - Hand.transform.position;
        HandFlexationHelper.x = 0;


        handFlexR = RotationWrist.x;
        handFlexR = ((handFlexR > 180) ? handFlexR - 360 : handFlexR);

        //handFlexR = Vector3.Angle(HandFlexationHelper, Hand.transform.localPosition)-90;

        HandFlexationHelper = Finger.transform.position - Hand.transform.position;
        HandFlexationHelper.y = 0;

        
        handRadDuctR = RotationWrist.y;
        handRadDuctR = ((handRadDuctR > 180) ? handRadDuctR - 360 : handRadDuctR);
        
        //handRadDuctR = Vector3.Angle(HandFlexationHelper, Hand.transform.localPosition);
    }

    float SignedAngleBetween(Vector3 a, Vector3 b, Vector3 n)
    {
        // angle in [0,180]
        float angle = Vector3.Angle(a, b);
        float sign = Mathf.Sign(Vector3.Dot(n, Vector3.Cross(a, b)));

        // angle in [-179,180]
        float signed_angle = angle * sign;

        // angle in [0,360]
        float angle360 = (signed_angle + 180) % 360;

        return angle360;
    }
}
