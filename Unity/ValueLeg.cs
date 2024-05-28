using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ValuesLeg : MonoBehaviour
{
    public GameObject Hip;

    public GameObject UpperLegR;
    public GameObject LowerLegR;
    public GameObject FootR;

    public GameObject UpperLegL;
    public GameObject LowerLegL;
    public GameObject FootL;

    public float kneeLAngleSit;
    public float kneeRAngleSit;

    public float kneeLAngleStand;
    public float kneeRAngleStand;


    void Update()
    {

        kneeLAngleStand = Vector3.Angle(LowerLegL.transform.position - FootL.transform.position, new Vector3(0,10,0)) - 10;
        kneeRAngleStand = Vector3.Angle(LowerLegR.transform.position - FootR.transform.position, new Vector3(0, 10, 0)) - 10;

        kneeLAngleSit = Vector3.Angle(LowerLegL.transform.position - FootL.transform.position, new Vector3(0, 10, 0))*(-1) + 100;
        kneeRAngleSit = Vector3.Angle(LowerLegR.transform.position - FootR.transform.position, new Vector3(0, 10, 0)) * (-1) + 100;
    }
}
