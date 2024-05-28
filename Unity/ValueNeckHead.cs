using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class ValueNeckHead : MonoBehaviour
{
    public GameObject TopHead; //non existent in unity
    public GameObject Head; // POsition Joint ForeArm (ELbow)
    public GameObject Neck; // Position Joint Shoulder 
    public GameObject Torso;
    public GameObject ShoulderL;
    public GameObject ShoulderR;

    public float NeckFlExAngle; // Shoulder Flexion / Exztension 
    public float HeadSideTilt;
    public float NeckBend;
    public float NeckTors;
    public Vector3 VectNktoHd; // Vector Neck to Head,
    public Vector3 VectNktoUnitA; // Vector Shoulder to Unit vector A, Plane for Flexion/Extension (Yellow-Blue)
    private Vector3 UnitVectorA;

    public Vector3 VectTstoNk; // Vector Torso to Neck
    public Vector3 Rotation;
    public Vector3 RotationNeck;

    public Vector3 ShoulderAxis;


    // Update is called once per frame
    void Update()
    {
        VectNktoHd = Head.transform.position - Neck.transform.position;    // Vector Head to Neck
        UnitVectorA = Head.transform.forward; // Unit vector in axis Z blue

        Rotation = Head.transform.localRotation.eulerAngles;

        NeckFlExAngle = Rotation.x;     //VEDANT
        //NeckFlExAngle = ((NeckFlExAngle > 180) ? NeckFlExAngle - 360 : NeckFlExAngle) +15;

        //NeckFlExAngle = Vector3.Angle(UnitVectorA, VectNktoHd) - 80; // Angle calculation

        NeckTors = Rotation.y;
        NeckTors = ((NeckTors > 180) ? NeckTors - 360 : NeckTors);

        VectTstoNk = Torso.transform.position - Neck.transform.position;
        NeckBend = Vector3.Angle(VectTstoNk, VectNktoHd)*(-1)+160;

        RotationNeck = Neck.transform.localRotation.eulerAngles;
        NeckBend = Rotation.x;
        // NeckBend = ((NeckBend > 180) ? NeckBend - 360 : NeckBend)+10;

        ShoulderAxis = ShoulderL.transform.position - ShoulderR.transform.position;

        VectNktoHd[2] = 0;
        UnitVectorA[2] = 0;
        HeadSideTilt = Vector3.Angle(VectNktoHd, ShoulderAxis)-90;  //VEDANT

    }
}
