using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ValueBack : MonoBehaviour
{

    public GameObject Hip;
    public GameObject Low;
    public GameObject Mid;
    public GameObject High;
    public GameObject ShoulderL;
    public GameObject ShoulderR;

    public Vector3 HipSpineAngle1;
    public Vector3 HipSpineAngle2;
    public float TorsoTilt;
    public float TorsoSideTilt;
    public float BackTors;
    public float BackCurve;
    public float BackFlex;

    public Vector3 ShoulderAxis;
    public Vector3 RotationHip;
    public Vector3 RotationLow;
    public Vector3 RotationTors;

    // Update is called once per frame
    void Update()
    {
        HipSpineAngle1 = Hip.transform.position - High.transform.position;

        RotationHip = Hip.transform.localRotation.eulerAngles;
        BackFlex = RotationHip.x;
        BackFlex = ((BackFlex > 180) ? BackFlex - 360 : BackFlex)+5;

        //BackFlex = Vector3.Angle(HipSpineAngle1, Low.transform.position)-90;


        ShoulderAxis = ShoulderR.transform.position - ShoulderL.transform.position;
        HipSpineAngle2 = Hip.transform.position - High.transform.position;
        TorsoSideTilt = Vector3.Angle(HipSpineAngle2, ShoulderAxis)-90;

        //BackCurve = Vector3.Angle(Low.transform.position - Mid.transform.position, Mid.transform.position - High.transform.position);

        RotationLow = Low.transform.localRotation.eulerAngles;
        BackCurve = RotationLow.x;
        BackCurve = ((BackCurve > 180) ? BackCurve - 360 : BackCurve) + 5;

        //BackTors = Mid.transform.localRotation.y;

        RotationTors = Hip.transform.localRotation.eulerAngles;
        BackTors = RotationTors.y;
        BackTors = ((BackTors > 180) ? BackTors - 360 : BackTors)*(-1);
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
